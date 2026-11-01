#!/usr/bin/env python3
"""Independent, fixture-scoped evaluator. Does not import ChangeProof."""

import argparse
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path, PurePosixPath
import sys

CASES = ("combined", "annotation_only", "unsupported", "key_order_only")


class VerificationFailure(Exception):
    pass


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sorted_json_digest(value):
    # Scoped ASCII-fixture encoding, not RFC 8785 canonicalization.
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def escape(token):
    return str(token).replace("~", "~0").replace("/", "~1")


def structural_diff(before, after, pointer=""):
    """Ignore object order; traverse fixture tools by index, other arrays whole."""
    if type(before) is not type(after):
        return [{"operation": "replace", "json_pointer": pointer,
                 "before": before, "after": after}]
    if isinstance(before, dict):
        changes = []
        for key in sorted(before.keys() | after.keys()):
            child = pointer + "/" + escape(key)
            if key not in before:
                changes.append({"operation": "add", "json_pointer": child,
                                "after": after[key]})
            elif key not in after:
                changes.append({"operation": "remove", "json_pointer": child,
                                "before": before[key]})
            else:
                changes.extend(structural_diff(before[key], after[key], child))
        return changes
    if pointer == "/tools" and isinstance(before, list) and len(before) == len(after):
        changes = []
        for index, (old_tool, new_tool) in enumerate(zip(before, after)):
            changes.extend(structural_diff(old_tool, new_tool, pointer + "/" + str(index)))
        return changes
    if before != after:
        return [{"operation": "replace", "json_pointer": pointer,
                 "before": before, "after": after}]
    return []


def reject_references(value):
    if isinstance(value, dict):
        if "$ref" in value or "$dynamicRef" in value:
            raise VerificationFailure("This fixture verifier permits no schema references")
        for child in value.values():
            reject_references(child)
    elif isinstance(value, list):
        for child in value:
            reject_references(child)


def evaluate(root, validator):
    checks = []
    report = {"format_version": 1, "status": "FAIL", "checks": checks}

    def require(name, condition, detail):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise VerificationFailure(name + ": " + detail)

    try:
        manifest = read_json(root / "SHA256SUMS.json")
        require("manifest_algorithm", manifest["algorithm"] == "SHA-256",
                "Manifest declares SHA-256")
        required_files = {
            "README.md", "REPORT.md", "SUBMISSION_DRAFT.md", "verify_fixture.py",
            "reproduce_changeproof.py", "requirements.txt", "provenance.json",
            "expected/structural_changes.json", "expected/compatibility.json",
            "expected/changeproof_reports.json", "snapshots/before.tools-list.json",
            "observed/validation_environment.json", "observed/independent_validation.json",
        }
        for case in CASES:
            required_files.add(f"snapshots/{case}.after.tools-list.json")
            required_files.add(f"observed/changeproof_v123_{case}.json")
        require("manifest_coverage", set(manifest["files"]) == required_files,
                f"Exactly {len(required_files)} distributed files are tracked; manifest excludes itself")
        for relative, expected_hash in manifest["files"].items():
            path = PurePosixPath(relative)
            if path.is_absolute() or ".." in path.parts:
                raise VerificationFailure("Unsafe manifest path")
            actual_path = root.joinpath(*path.parts)
            if actual_path.is_symlink() or not actual_path.is_file():
                raise VerificationFailure("Missing or non-regular file: " + relative)
            if sha256(actual_path) != expected_hash:
                raise VerificationFailure("SHA-256 mismatch: " + relative)
        require("distributed_file_integrity", True,
                f"All {len(required_files)} distributed file hashes match")

        baseline = read_json(root / "snapshots/before.tools-list.json")
        candidates = {case: read_json(root / f"snapshots/{case}.after.tools-list.json")
                      for case in CASES}
        expected_changes = read_json(root / "expected/structural_changes.json")["cases"]
        expected_compat = read_json(root / "expected/compatibility.json")
        expected_engine = read_json(root / "expected/changeproof_reports.json")["cases"]
        provenance = read_json(root / "provenance.json")

        for label, snapshot in [("before", baseline), *candidates.items()]:
            require("snapshot_shape_" + label,
                    set(snapshot) == {"tools"} and len(snapshot["tools"]) == 1
                    and snapshot["tools"][0]["name"] == "fixture_lookup",
                    "Single synthetic tool in a tools/list result body")
            reject_references(snapshot)
            for field in ("inputSchema", "outputSchema"):
                validator.check_schema(snapshot["tools"][0][field])
        require("local_schema_validation", True,
                "Ten schemas are valid under Draft 2020-12; no references are present")

        actual_changes = {}
        for case, snapshot in candidates.items():
            actual_changes[case] = structural_diff(baseline, snapshot)
            require("structural_diff_" + case,
                    actual_changes[case] == expected_changes[case],
                    f"{len(actual_changes[case])} literal structural changes match the authored expectation")
        report["structural_changes"] = actual_changes

        old = baseline["tools"][0]
        new = candidates["combined"]["tools"][0]
        old_input, new_input = old["inputSchema"], new["inputSchema"]
        old_required, new_required = set(old_input["required"]), set(new_input["required"])
        old_without_required, new_without_required = copy.deepcopy(old_input), copy.deepcopy(new_input)
        del old_without_required["required"]
        del new_without_required["required"]
        require("input_inclusion_argument",
                old_without_required == new_without_required
                and new_required == old_required | {"workspace_id"}
                and "workspace_id" in old_input["properties"]
                and "workspace_id" not in old_required,
                "Only an existing optional property becomes required: I_new is a subset of I_old")

        old_output, new_output = old["outputSchema"], new["outputSchema"]
        old_enum = set(old_output["properties"]["status"]["enum"])
        new_enum = set(new_output["properties"]["status"]["enum"])
        output_without_enum_old, output_without_enum_new = copy.deepcopy(old_output), copy.deepcopy(new_output)
        del output_without_enum_old["properties"]["status"]["enum"]
        del output_without_enum_new["properties"]["status"]["enum"]
        require("output_inclusion_argument",
                output_without_enum_old == output_without_enum_new
                and new_enum == old_enum | {"paused"} and "paused" not in old_enum,
                "Only the status enum expands: O_old is a subset of O_new")

        witness_results = []
        required_witnesses = {
            "old_input_missing_workspace": ("inputSchema", {"query": "alpha"}, True, False),
            "new_input_with_workspace": ("inputSchema", {"query": "alpha", "workspace_id": "demo"}, True, True),
            "old_output_ready": ("outputSchema", {"status": "ready", "count": 1}, True, True),
            "new_output_paused": ("outputSchema", {"status": "paused", "count": 0}, False, True),
        }
        require("witness_coverage",
                len(expected_compat["witnesses"]) == 4
                and {w["id"] for w in expected_compat["witnesses"]} == set(required_witnesses),
                "Both counterexamples and both unchanged-valid examples are present")
        for witness in expected_compat["witnesses"]:
            field, instance, before_ok, after_ok = required_witnesses[witness["id"]]
            require("witness_definition_" + witness["id"],
                    witness["case"] == "combined" and witness["schema"] == field
                    and witness["instance"] == instance
                    and witness["valid_before"] is before_ok
                    and witness["valid_after"] is after_ok,
                    "Witness matches the independently specified regression case")
            result = {"id": witness["id"]}
            for revision, schema in (("before", old[field]), ("after", new[field])):
                errors = sorted(validator(schema).iter_errors(instance),
                                key=lambda error: (str(error.path), str(error.schema_path)))
                valid = not errors
                keywords = sorted({str(error.validator) for error in errors})
                require("witness_" + witness["id"] + "_" + revision,
                        valid is witness["valid_" + revision],
                        f"valid={valid}; failed keywords={keywords}")
                expected_keyword = witness.get(revision + "_error_keyword")
                if expected_keyword:
                    require("witness_keyword_" + witness["id"] + "_" + revision,
                            expected_keyword in keywords, "Expected rejecting validation keyword is present")
                result["valid_" + revision] = valid
                result[revision + "_error_keywords"] = keywords
            witness_results.append(result)
        report["witnesses"] = witness_results

        inp = expected_compat["combined"]["inputs"]
        out = expected_compat["combined"]["outputs"]
        require("expected_compatibility_directions",
                inp["old_clients_to_new_tool"]["holds"] is False
                and inp["new_clients_to_old_tool"]["holds"] is True
                and out["new_tool_to_strict_old_consumer"]["holds"] is False
                and out["old_tool_to_new_consumer"]["holds"] is True,
                "Authored directions agree with the two counterexamples and isolated-edit inclusion arguments")

        annotation_tool = candidates["annotation_only"]["tools"][0]
        annotation_expected = expected_compat["annotation_only"]
        require("annotation_policy_separation",
                annotation_tool["inputSchema"] == old_input
                and annotation_tool["outputSchema"] == old_output
                and annotation_expected == {
                    "input_schema_unchanged": True, "output_schema_unchanged": True,
                    "schema_validation_sets_unchanged": True, "metadata_review_required": True}
                and expected_compat["combined"]["annotations"]["classification"] == "REVIEW"
                and expected_compat["combined"]["annotations"]["input_or_output_validation_rule"] is False,
                "Annotation control preserves schemas but retains a separate metadata-review judgment")
        unsupported = expected_compat["unsupported"]
        require("unsupported_requires_review",
                unsupported["compatibility_direction"] == "REQUIRES_REVIEW"
                and unsupported["input_set_inclusion"] is None
                and unsupported["output_set_inclusion"] is None
                and unsupported["comparison_complete"] is False,
                "No compatibility direction is asserted for the changed composition")

        before_path = root / "snapshots/before.tools-list.json"
        reordered_path = root / "snapshots/key_order_only.after.tools-list.json"
        digest_controls = {
            "structural_changes": bool(actual_changes["key_order_only"]),
            "parsed_json_equal": baseline == candidates["key_order_only"],
            "raw_file_hash_equal": sha256(before_path) == sha256(reordered_path),
            "fixture_sorted_json_digest_equal": sorted_json_digest(baseline) == sorted_json_digest(candidates["key_order_only"]),
            "semantic_equivalence_proof": False,
        }
        require("object_key_order_control", digest_controls == expected_compat["key_order_only"],
                "Raw bytes differ; parsed JSON and fixture-only sorted-key digest agree")
        report["key_order_control"] = digest_controls

        engine_results = {}
        for case in CASES:
            observed = read_json(root / f"observed/changeproof_v123_{case}.json")
            comparable = {
                "status": observed["status"],
                "comparison_complete": observed["comparison_complete"],
                "structural_findings": [
                    {key: finding[key] for key in ("code", "role", "pointer", "risk")}
                    for finding in observed["structural_findings"]],
                "limitations": observed["limitations"],
            }
            require("recorded_engine_report_" + case,
                    comparable == expected_engine[case]
                    and observed["analysis_version"] == provenance["changeproof"]["analysis_version"],
                    "Recorded report matches expected status, completeness, findings, locators and limitations")
            engine_results[case] = comparable
        report["recorded_engine_reports"] = engine_results
        report["environment"] = {"python": sys.version.split()[0],
                                 "jsonschema": importlib.metadata.version("jsonschema")}
        report["scope"] = "Independent fixture and recorded-report checks; no ChangeProof module imported, MCP tool invoked or arbitrary-schema compatibility theorem established."
        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, help="Write a fresh result outside the distributed files")
    args = parser.parse_args()
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print(json.dumps({"status": "FAIL", "error": "Install requirements.txt first"}))
        return 2
    if args.output:
        try:
            tracked = read_json(args.root / "SHA256SUMS.json")["files"]
            protected = {args.root.joinpath(path).resolve() for path in tracked}
            protected.add((args.root / "SHA256SUMS.json").resolve())
            if args.output.resolve() in protected:
                parser.error("--output must not overwrite a distributed file")
        except (OSError, KeyError, ValueError):
            pass  # evaluate() will report a missing or invalid manifest.
    result = evaluate(args.root.resolve(), Draft202012Validator)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
