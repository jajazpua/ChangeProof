#!/usr/bin/env python3
"""Optionally rerun a locally available, hash-matched ChangeProof V1.2.3 module."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        source = args.module.resolve()
        expected_hash = load_json(root / "provenance.json")["changeproof"]["source_module_sha256"]
        actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError("Source SHA-256 mismatch; module was not imported")
        spec = importlib.util.spec_from_file_location("changeproof_local_fixture_rerun", source)
        if spec is None or spec.loader is None:
            raise ValueError("Cannot load the supplied module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        baseline = load_json(root / "snapshots/before.tools-list.json")
        results = []
        for case in ("combined", "annotation_only", "unsupported", "key_order_only"):
            after = load_json(root / f"snapshots/{case}.after.tools-list.json")
            rerun = module.analyze("mcp", baseline, after, algorithm_version=module.VERSION)
            recorded = load_json(root / f"observed/changeproof_v123_{case}.json")
            if rerun != recorded:
                raise ValueError("Rerun differs from the complete recorded output: " + case)
            results.append({"case": case, "exact_report_match": True})
        print(json.dumps({"status": "PASS", "source_module_sha256": actual_hash,
                          "cases": results}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
