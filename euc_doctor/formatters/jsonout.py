from __future__ import annotations

import json

from euc_doctor.models import ToolkitRun


def build_json(run: ToolkitRun) -> str:
    return json.dumps(run.to_dict(), indent=2)
