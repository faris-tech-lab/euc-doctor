from __future__ import annotations

from datetime import datetime, timezone

from euc_doctor.categories import all_actions
from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity, ToolkitRun
from euc_doctor.utils import current_platform_label, write_history_entry

ACTIONS: list[ActionDefinition] = all_actions()
ACTION_INDEX = {action.action_id: action for action in ACTIONS}


def list_actions(category: str | None = None, include_fixes: bool = True) -> list[ActionDefinition]:
    actions = ACTIONS
    if category:
        actions = [action for action in actions if action.category.value == category]
    if not include_fixes:
        actions = [action for action in actions if action.action_type != ActionType.FIX]
    return sorted(actions, key=lambda action: (action.category.value, action.action_id))


def list_categories() -> list[ActionCategory]:
    return list(ActionCategory)


def resolve_target(target: str, include_fixes: bool = True) -> list[ActionDefinition]:
    normalized = target.lower()
    if normalized in ACTION_INDEX:
        action = ACTION_INDEX[normalized]
        if include_fixes or action.action_type != ActionType.FIX:
            return [action]
        return []
    if normalized == "all":
        return list_actions(include_fixes=include_fixes)
    return list_actions(category=normalized, include_fixes=include_fixes)


def execute_action(action: ActionDefinition, ctx: ExecutionContext) -> ActionResult:
    if action.action_type == ActionType.FIX and not ctx.should_continue(action):
        return ActionResult(
            action_id=action.action_id,
            category=action.category,
            action_type=action.action_type,
            name=action.name,
            severity=Severity.SKIPPED,
            message="Skipped by user confirmation.",
            requires_admin=action.requires_admin,
        )
    return action.handler(ctx, action)


def run_actions(target: str, actions: list[ActionDefinition], ctx: ExecutionContext) -> ToolkitRun:
    timestamp = datetime.now(timezone.utc).isoformat()
    run = ToolkitRun(target=target, platform=current_platform_label(), timestamp=timestamp, dry_run=ctx.dry_run)
    for action in actions:
        result = execute_action(action, ctx)
        run.results.append(result)
        write_history_entry(target, result, ctx.dry_run)
    return run


def run_target(target: str, ctx: ExecutionContext, include_fixes: bool = True) -> ToolkitRun:
    actions = resolve_target(target, include_fixes=include_fixes)
    return run_actions(target, actions, ctx)
