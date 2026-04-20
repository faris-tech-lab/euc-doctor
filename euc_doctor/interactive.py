from __future__ import annotations

from dataclasses import dataclass

from euc_doctor.display import render_action_catalog, render_category_overview
from euc_doctor.registry import list_actions, list_categories


@dataclass
class MenuSelection:
    mode: str
    target: str


def launch_menu() -> MenuSelection | None:
    try:
        from InquirerPy import inquirer
    except ImportError as exc:
        raise RuntimeError("InquirerPy is required for menu mode.") from exc

    categories = list_categories()
    while True:
        category_rows = [(category.label, category.value, len(list_actions(category=category.value))) for category in categories]
        render_category_overview(category_rows, clear_first=True)

        category_choices = [{"name": f"{category.label} ({len(list_actions(category=category.value))})", "value": category.value} for category in categories]
        category_choices.extend(
            [
                {"name": "Machine Health Check", "value": "__health__"},
                {"name": "Run Full Diagnostic", "value": "__diagnose__"},
                {"name": "Exit", "value": "__exit__"},
            ]
        )

        category = inquirer.select(message="Pick a category", choices=category_choices, cycle=True).execute()
        if category == "__exit__":
            return None
        if category == "__health__":
            return MenuSelection(mode="health", target="health")
        if category == "__diagnose__":
            return MenuSelection(mode="diagnose", target="all")

        actions = list_actions(category=category)
        category_label = next(item.label for item in categories if item.value == category)
        while True:
            render_action_catalog(actions, category_label=category_label, clear_first=True)
            action_choices = [
                {"name": f"[{action.action_type.value.upper()}] {action.name}", "value": action.action_id}
                for action in actions
            ]
            action_choices.append({"name": "Run whole category", "value": category})
            action_choices.append({"name": "Run category diagnostics only", "value": f"__diagnose__:{category}"})
            action_choices.append({"name": "Back", "value": "__back__"})
            chosen = inquirer.select(message="Pick an action from this category", choices=action_choices, cycle=True).execute()
            if chosen == "__back__":
                break
            if chosen.startswith("__diagnose__:"):
                return MenuSelection(mode="diagnose", target=chosen.split(":", 1)[1])
            return MenuSelection(mode="run", target=chosen)
