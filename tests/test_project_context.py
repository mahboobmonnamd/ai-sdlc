import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "project_context.py"
SPEC = importlib.util.spec_from_file_location("project_context", MODULE_PATH)
project_context = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(project_context)


class ProjectContextValidationTests(unittest.TestCase):
    def make_project(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        source = root / "docs" / "architecture.md"
        source.parent.mkdir(parents=True)
        source.write_text("authoritative architecture\n", encoding="utf-8")
        fingerprint = project_context.git_blob_sha(source)
        index = {
            "schema_version": "0.1",
            "authority": "derived-navigation-index",
            "nodes": [
                {
                    "id": "COMP-A",
                    "kind": "component",
                    "title": "Component A",
                    "summary": "Owns the example boundary.",
                    "sources": [
                        {"path": "docs/architecture.md", "fingerprint": fingerprint}
                    ],
                    "relationships": [{"type": "depends_on", "target": "COMP-B"}],
                },
                {
                    "id": "COMP-B",
                    "kind": "component",
                    "title": "Component B",
                    "summary": "A related component.",
                    "sources": [
                        {"path": "docs/architecture.md", "fingerprint": fingerprint}
                    ],
                    "relationships": [],
                },
            ],
        }
        return temp, root, source, index

    def test_valid_index(self):
        temp, root, _, index = self.make_project()
        self.addCleanup(temp.cleanup)
        self.assertEqual([], project_context.validate(index, root))

    def test_stale_source_is_detected(self):
        temp, root, source, index = self.make_project()
        self.addCleanup(temp.cleanup)
        source.write_text("changed architecture\n", encoding="utf-8")
        errors = project_context.validate(index, root)
        self.assertTrue(any("stale source" in error for error in errors))

    def test_duplicate_and_dangling_nodes_are_detected(self):
        temp, root, _, index = self.make_project()
        self.addCleanup(temp.cleanup)
        index["nodes"][1]["id"] = "COMP-A"
        index["nodes"][0]["relationships"][0]["target"] = "MISSING"
        errors = project_context.validate(index, root)
        self.assertTrue(any("duplicate node id" in error for error in errors))
        self.assertTrue(any("dangling relationship" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
