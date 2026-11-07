"""Offline tests for repository evidence checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_evidence.py"
SPEC = importlib.util.spec_from_file_location("evidence_checker", PATH)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class EvidenceTests(unittest.TestCase):
    def run_check(self, files):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="")
            return checker.check_repository(root, list(files))

    def test_valid_relative_links(self):
        result = self.run_check({"README.md": "[Guide](docs/guide.md#section) ![art](art.svg)",
                                 "docs/guide.md": "[Home](../README.md)",
                                 "art.svg": '<svg xmlns="http://www.w3.org/2000/svg"/>'})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checks"]["relative_links"], 3)

    def test_missing_relative_link(self):
        result = self.run_check({"README.md": "[Missing](missing.md)"})
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Missing relative link", result["errors"][0]["reason"])

    def test_external_links_are_not_probed(self):
        result = self.run_check({"README.md": "[External](https://example.invalid/x) [Anchor](#here)"})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checks"]["relative_links"], 0)

    def test_fenced_examples_are_ignored(self):
        text = "```markdown\n[example](not-a-real-file.md)\n```\n"
        self.assertEqual(self.run_check({"README.md": text})["status"], "PASS")

    def test_paths_cannot_escape_repository(self):
        with self.assertRaisesRegex(ValueError, "escapes repository"):
            checker.relative_link("README.md", "../outside.md")
        with self.assertRaisesRegex(ValueError, "Unsafe tracked"):
            checker.check_repository(Path("."), ["../outside.md"])

    def test_encoded_filename_and_directory(self):
        result = self.run_check({"README.md": "[file](docs/a%20b.md) [folder](docs/)",
                                 "docs/a b.md": "# Guide"})
        self.assertEqual(result["status"], "PASS")

    def test_json_rejects_duplicates_and_nan(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', '{"x":-1e999}'):
            with self.subTest(text=text):
                self.assertEqual(self.run_check({"data.json": text})["status"], "FAIL")

    def test_syntax_and_xml_failures_are_reported(self):
        result = self.run_check({"bad.py": "def broken(:", "bad.svg": "<svg>"})
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len(result["errors"]), 2)

    def test_manifest_accepts_exact_bytes_and_rejects_changes(self):
        source = '{"example":true}\n'
        manifest = json.dumps({"algorithm": "SHA-256", "files": {
            "data.json": hashlib.sha256(source.encode()).hexdigest()}})
        files = {"case/SHA256SUMS.json": manifest, "case/data.json": source}
        result = self.run_check(files)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checks"]["manifest_entries"], 1)
        files["case/data.json"] = '{"example":false}\n'
        self.assertEqual(self.run_check(files)["status"], "FAIL")

    def test_angle_brackets_and_parentheses_in_links(self):
        result = self.run_check({"README.md": "[space](<docs/a b.md>) [paren](docs/a(b).md)",
                                 "docs/a b.md": "# One", "docs/a(b).md": "# Two"})
        self.assertEqual(result["status"], "PASS")

    def test_malformed_manifests_fail_cleanly(self):
        for value in ([], {"algorithm": "SHA-256", "files": []}, {"algorithm": "SHA-256"}):
            with self.subTest(value=value):
                self.assertEqual(self.run_check({"SHA256SUMS.json": json.dumps(value)})["status"], "FAIL")

    def test_html_image_links_are_checked(self):
        result = self.run_check({"demo.html": '<img src="missing.svg">'})
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
