import os
import time
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    multiprocess,
)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "route", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

SERVICE_INFO = Gauge(
    "service_info",
    "Static service metadata",
    ["service", "version", "env"],
    multiprocess_mode="max",
)


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return str(route.path)
    return request.url.path


def _metrics_payload() -> bytes:
    multiproc_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR", "").strip()
    if multiproc_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return generate_latest(registry)
    return generate_latest()


def install_metrics(app: FastAPI, service_name: str, version: str, env: str) -> None:
    SERVICE_INFO.labels(service=service_name, version=version, env=env).set(1)

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: Callable):
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            route = _route_template(request)
            method = request.method
            HTTP_REQUESTS.labels(
                service=service_name,
                method=method,
                route=route,
                status=str(status_code),
            ).inc()
            REQUEST_LATENCY.labels(
                service=service_name,
                method=method,
                route=route,
            ).observe(time.perf_counter() - start)

    @app.get("/metrics", include_in_schema=False)
    async def metrics_endpoint() -> Response:
        return Response(content=_metrics_payload(), media_type=CONTENT_TYPE_LATEST)
