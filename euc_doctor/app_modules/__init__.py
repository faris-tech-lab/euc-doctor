from __future__ import annotations

from euc_doctor.models import ActionDefinition

from .adobe_cc import MODULE as ADOBE_CC
from .anyconnect import MODULE as ANYCONNECT
from .chrome import MODULE as CHROME
from .common import AppSupportModule, build_actions
from .dropbox import MODULE as DROPBOX
from .firefox import MODULE as FIREFOX
from .jamf_connect import MODULE as JAMF_CONNECT
from .onedrive import MODULE as ONEDRIVE
from .outlook import MODULE as OUTLOOK
from .safari import MODULE as SAFARI
from .slack import MODULE as SLACK
from .teams import MODULE as TEAMS
from .vscode import MODULE as VSCODE
from .zoom import MODULE as ZOOM

APP_MODULES: tuple[AppSupportModule, ...] = (
    TEAMS,
    OUTLOOK,
    SLACK,
    ZOOM,
    CHROME,
    SAFARI,
    FIREFOX,
    ONEDRIVE,
    DROPBOX,
    ADOBE_CC,
    VSCODE,
    ANYCONNECT,
    JAMF_CONNECT,
)


def all_app_actions() -> list[ActionDefinition]:
    actions: list[ActionDefinition] = []
    for module in APP_MODULES:
        actions.extend(build_actions(module))
    return actions
