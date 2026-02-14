from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PolicyAudit:
    strictness_profile: Dict[str, Any]
    override_fired: str
    override_reason: str
    key_numbers: Dict[str, Any]

