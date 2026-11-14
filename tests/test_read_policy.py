from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.read_policy import sections, select


class ReadPolicyTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "docs/WORKING-LOOP.md").read_text(encoding="utf-8")

    def test_exact_sections_and_subheadings(self):
        names = sections(self.source)
        task = names["task-first-execution-and-progressive-context"]
        self.assertIn("### Risk-proportional rigor", task)
        self.assertIn("### One evidence packet", task)
        self.assertNotIn("## Exclusive ownership", task)
        self.assertEqual(task, select(self.source, ["task-first-execution-and-progressive-context"]))
        self.assertLess(len(task), len(self.source) // 2)

    def test_all_core_sections_retain_source_verbatim(self):
        parsed = sections(self.source)
        required = {"12-point-definition-of-ready", "adr-lifecycle-merge-is-acceptance",
                    "bounded-provisional-contract-lane", "exclusive-ownership",
                    "four-user-decisions-no-ritual-approvals", "desktop-safe-test-execution",
                    "verification-and-merge", "review-convergence-and-evidence-reuse"}
        self.assertTrue(required <= parsed.keys())
        self.assertEqual(self.source[self.source.index("## Task-first"):],
                         select(self.source, list(parsed)))

    def test_deduplicates_and_preserves_source_order(self):
        first, second = list(sections(self.source))[:2]
        self.assertEqual(select(self.source, [first, second]),
                         select(self.source, [second, first, second]))

    def test_unknown_and_duplicate_headings_fail_closed(self):
        for ids in ([], ["missing"], ["exclusive-ownership", "missing"]):
            with self.assertRaises(ValueError):
                select(self.source, ids)
        with self.assertRaises(ValueError):
            sections("## A\nfirst\n## A\nsecond\n")

    def test_fenced_headings_are_not_sections(self):
        src = "## A\n```text\n## not a heading\n```\n### sub\n## B\nlast\n"
        self.assertEqual(["a", "b"], list(sections(src)))
        self.assertIn("## not a heading", select(src, ["a"]))

    def test_cli_list_and_unknown(self):
        cmd = [sys.executable, str(ROOT / "tools/read_policy.py")]
        listing = subprocess.run(cmd + ["--list"], capture_output=True, text=True, check=True)
        self.assertIn("desktop-safe-test-execution", listing.stdout)
        denied = subprocess.run(cmd + ["missing"], capture_output=True, text=True)
        self.assertNotEqual(0, denied.returncode)
        self.assertEqual("", denied.stdout)


if __name__ == "__main__":
    unittest.main()
