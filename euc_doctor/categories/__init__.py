from __future__ import annotations

from euc_doctor.models import ActionDefinition

from .accounts import ACTIONS as ACCOUNTS_ACTIONS
from .apps import ACTIONS as APPS_ACTIONS
from .cache import ACTIONS as CACHE_ACTIONS
from .desktop import ACTIONS as DESKTOP_ACTIONS
from .hardware import ACTIONS as HARDWARE_ACTIONS
from .identity import ACTIONS as IDENTITY_ACTIONS
from .mdm import ACTIONS as MDM_ACTIONS
from .network import ACTIONS as NETWORK_ACTIONS
from .performance import ACTIONS as PERFORMANCE_ACTIONS
from .printing import ACTIONS as PRINTING_ACTIONS
from .security import ACTIONS as SECURITY_ACTIONS
from .storage import ACTIONS as STORAGE_ACTIONS
from .updates import ACTIONS as UPDATES_ACTIONS


def all_actions() -> list[ActionDefinition]:
    return [
        *CACHE_ACTIONS,
        *STORAGE_ACTIONS,
        *NETWORK_ACTIONS,
        *PERFORMANCE_ACTIONS,
        *APPS_ACTIONS,
        *DESKTOP_ACTIONS,
        *IDENTITY_ACTIONS,
        *SECURITY_ACTIONS,
        *PRINTING_ACTIONS,
        *UPDATES_ACTIONS,
        *MDM_ACTIONS,
        *ACCOUNTS_ACTIONS,
        *HARDWARE_ACTIONS,
    ]
