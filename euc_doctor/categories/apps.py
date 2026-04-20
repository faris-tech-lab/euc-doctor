from __future__ import annotations

from euc_doctor.app_modules import all_app_actions
from euc_doctor.models import ActionCategory, ActionDefinition, ActionType
from euc_doctor.utils import info_result


def _permissions(_, action: ActionDefinition):
    return info_result(action, "Permissions audit placeholder.", "Next build should inspect TCC-sensitive services like camera, microphone, screen recording, and accessibility with a more structured report.")


ACTIONS = all_app_actions() + [
    ActionDefinition("apps.app_permissions", ActionCategory.APPS, ActionType.INFO, "App permissions audit", "Describe the planned TCC permissions audit for common collaboration apps.", _permissions),
]
