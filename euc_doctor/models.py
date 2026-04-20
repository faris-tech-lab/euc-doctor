from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable


class ActionType(str, Enum):
    DIAGNOSE = "diagnose"
    FIX = "fix"
    INFO = "info"


class ActionCategory(str, Enum):
    CACHE = "cache"
    STORAGE = "storage"
    NETWORK = "network"
    PERFORMANCE = "performance"
    APPS = "apps"
    IDENTITY = "identity"
    SECURITY = "security"
    DESKTOP = "desktop"
    PRINTING = "printing"
    UPDATES = "updates"
    MDM = "mdm"
    ACCOUNTS = "accounts"
    HARDWARE = "hardware"

    @property
    def label(self) -> str:
        return CATEGORY_LABELS[self]


CATEGORY_LABELS: dict[ActionCategory, str] = {
    ActionCategory.CACHE: "Cache & Temp Files",
    ActionCategory.STORAGE: "Storage & Cleanup",
    ActionCategory.NETWORK: "Network & Connectivity",
    ActionCategory.PERFORMANCE: "Performance & Resources",
    ActionCategory.APPS: "Application Fixes",
    ActionCategory.IDENTITY: "Identity & Directory",
    ActionCategory.SECURITY: "Security & Compliance",
    ActionCategory.DESKTOP: "Desktop & UI",
    ActionCategory.PRINTING: "Printing",
    ActionCategory.UPDATES: "Updates & Patches",
    ActionCategory.MDM: "MDM & Enrollment",
    ActionCategory.ACCOUNTS: "User Accounts & Keychain",
    ActionCategory.HARDWARE: "Hardware & Peripherals",
}


class Severity(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    FIXED = "fixed"
    SKIPPED = "skipped"
    INFO = "info"


ActionHandler = Callable[["ExecutionContext", "ActionDefinition"], "ActionResult"]


@dataclass
class ExecutionContext:
    dry_run: bool = False
    assume_yes: bool = False
    confirmer: Callable[["ActionDefinition"], bool] | None = None

    def should_continue(self, action: "ActionDefinition") -> bool:
        if action.action_type != ActionType.FIX or self.dry_run or self.assume_yes:
            return True
        if self.confirmer is None:
            return False
        return self.confirmer(action)


@dataclass
class ActionDefinition:
    action_id: str
    category: ActionCategory
    action_type: ActionType
    name: str
    description: str
    handler: ActionHandler = field(repr=False, compare=False)
    touches: tuple[str, ...] = ()
    requires_admin: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "category": self.category.value,
            "category_label": self.category.label,
            "action_type": self.action_type.value,
            "name": self.name,
            "description": self.description,
            "touches": list(self.touches),
            "requires_admin": self.requires_admin,
        }


@dataclass
class ActionResult:
    action_id: str
    category: ActionCategory
    action_type: ActionType
    name: str
    severity: Severity
    message: str
    detail: str | None = None
    bytes_freed: int | None = None
    requires_restart: bool = False
    requires_admin: bool = False
    touched_paths: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["category"] = self.category.value
        payload["category_label"] = self.category.label
        payload["action_type"] = self.action_type.value
        payload["severity"] = self.severity.value
        payload["touched_paths"] = list(self.touched_paths)
        return payload


@dataclass
class ToolkitRun:
    target: str
    platform: str
    timestamp: str
    dry_run: bool
    results: list[ActionResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def bytes_freed(self) -> int:
        return sum(result.bytes_freed or 0 for result in self.results)

    @property
    def requires_restart_count(self) -> int:
        return sum(1 for result in self.results if result.requires_restart)

    def severity_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for result in self.results:
            counts[result.severity.value] += 1
        return dict(counts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "platform": self.platform,
            "timestamp": self.timestamp,
            "dry_run": self.dry_run,
            "summary": {
                "total": self.total,
                "bytes_freed": self.bytes_freed,
                "requires_restart_count": self.requires_restart_count,
                "severity_counts": self.severity_counts(),
            },
            "results": [result.to_dict() for result in self.results],
        }
