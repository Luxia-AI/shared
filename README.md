# Shared Module

`shared` contains reusable code used across backend services.

## Current Contents

- `shared/metrics.py`: shared Prometheus instrumentation middleware installer

## Usage

`socket-hub`, `dispatcher`, and `worker` call `install_metrics(...)` during app startup to expose standardized HTTP request counters and latency histograms.

## Canonical Docs

- `docs/system-overview.md`
- `docs/interfaces-and-contracts.md`
- `docs/deployment-and-operations.md`

Last verified against code: February 13, 2026
