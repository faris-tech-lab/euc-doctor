from __future__ import annotations

from euc_doctor.models import ToolkitRun
from euc_doctor.utils import format_bytes


def build_markdown(run: ToolkitRun) -> str:
    lines = [
        "# EUC Doctor Report",
        "",
        f"- Target: `{run.target}`",
        f"- Platform: `{run.platform}`",
        f"- Timestamp: `{run.timestamp}`",
        f"- Dry run: `{run.dry_run}`",
        f"- Bytes freed: `{format_bytes(run.bytes_freed)}`",
        "",
        "## Results",
        "",
    ]
    for result in run.results:
        lines.append(f"### {result.name}")
        lines.append(f"- ID: `{result.action_id}`")
        lines.append(f"- Category: `{result.category.label}`")
        lines.append(f"- Type: `{result.action_type.value}`")
        lines.append(f"- Severity: `{result.severity.value}`")
        lines.append(f"- Message: {result.message}")
        if result.bytes_freed is not None:
            lines.append(f"- Bytes freed: `{format_bytes(result.bytes_freed)}`")
        if result.detail:
            lines.append("")
            lines.append("```text")
            lines.append(result.detail)
            lines.append("```")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
