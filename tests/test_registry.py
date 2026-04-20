from __future__ import annotations

import unittest

from euc_doctor.formatters.markdown import build_markdown
from euc_doctor.models import ActionType, ExecutionContext
from euc_doctor.registry import list_actions, resolve_target, run_target


class RegistryTests(unittest.TestCase):
    def test_action_catalog_has_expected_items(self) -> None:
        actions = list_actions()
        action_ids = {action.action_id for action in actions}
        self.assertIn("cache.sizes", action_ids)
        self.assertIn("cache.all", action_ids)
        self.assertIn("apps.teams_status", action_ids)
        self.assertIn("apps.dropbox_playbook", action_ids)
        self.assertIn("apps.anyconnect_status", action_ids)
        self.assertIn("apps.jamf_connect_playbook", action_ids)
        self.assertIn("apps.vscode_playbook", action_ids)
        self.assertIn("net.summary", action_ids)
        self.assertIn("net.cert_check", action_ids)
        self.assertIn("mdm.enrollment", action_ids)
        self.assertIn("mdm.logs", action_ids)
        self.assertIn("mdm.jamf_connection", action_ids)

    def test_diagnose_mode_excludes_fixes(self) -> None:
        actions = resolve_target("cache", include_fixes=False)
        self.assertTrue(actions)
        self.assertTrue(all(action.action_type != ActionType.FIX for action in actions))

    def test_run_report_renders_markdown(self) -> None:
        report = run_target("apps", ExecutionContext(dry_run=True, assume_yes=True), include_fixes=False)
        markdown = build_markdown(report)
        self.assertIn("# EUC Doctor Report", markdown)
        self.assertIn("Microsoft Teams status", markdown)

    def test_health_target_actions_exist(self) -> None:
        from euc_doctor.health import health_actions

        actions = health_actions()
        self.assertTrue(actions)
        self.assertIn("mdm.jamf_binary", {action.action_id for action in actions})


if __name__ == "__main__":
    unittest.main()
