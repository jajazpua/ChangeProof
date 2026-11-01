# ChangeProof / ShenYu #7935: reproducible synthetic MCP fixture

Prepared 2026-11-01 for the [explicit artifact request from @Aias00](https://github.com/apache/shenyu/issues/7935#issuecomment-6552137262). This is an original synthetic regression proposal, not a capture from a deployed ShenYu server and not yet accepted by the maintainer.

## Quick independent check

The recorded run used Python 3.12.14. From this directory:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify_fixture.py
```

On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. The script prints a JSON report and exits 0 on success, 1 on a failed check, or 2 on a missing dependency. `--output verification.actual.json` optionally saves that report. Installation may download dependencies; verification itself makes no network requests and invokes no MCP tool. All schemas are local and contain no references.

The verifier is a small public comparator scoped to these fixtures. It independently computes structural diffs, validates schemas and four concrete witnesses, checks the simple set-inclusion arguments, compares recorded ChangeProof findings with the authored expectations, and checks file hashes. It does not import ChangeProof or prove arbitrary JSON Schema inclusion. Finite witnesses demonstrate the two rejected directions; the two inclusion directions follow from the explicitly checked, isolated schema edits.

## Files

- `snapshots/before.tools-list.json`: one synthetic baseline tool.
- `snapshots/combined.after.tools-list.json`: newly required input + output enum expansion + annotation change.
- `snapshots/annotation_only.after.tools-list.json`: isolated annotation control.
- `snapshots/unsupported.after.tools-list.json`: changed `allOf` / `not`; compatibility must require review.
- `snapshots/key_order_only.after.tools-list.json`: object-key-order control.
- `expected/structural_changes.json`: literal snapshot JSON Pointers and before/after facts.
- `expected/compatibility.json`: input/output direction, assumptions and test instances.
- `expected/changeproof_reports.json`: expected status, limitations and finding identities.
- `observed/changeproof_v123_*.json`: unchanged outputs from the existing ChangeProof V1.2.3 module.
- `observed/independent_validation.json`: recorded public-verifier run.
- `REPORT.md`: human-readable findings and limits.
- `reproduce_changeproof.py`: optional rerun adapter for a holder of the exact ChangeProof module.
- `provenance.json`, `observed/validation_environment.json`, `SHA256SUMS.json`: source and byte identities.
- `SUBMISSION_DRAFT.md`: proposed issue reply; not submitted by preparing this archive.

## Compatibility directions

Let `I_old` / `I_new` be accepted argument sets, and `O_old` / `O_new` be accepted structured-output sets.

| Direction | Required relation | Combined fixture |
| --- | --- | --- |
| Old callers use new tool | `I_old ⊆ I_new` | False: `{ "query": "alpha" }` lacks newly required `workspace_id` |
| New callers use old tool | `I_new ⊆ I_old` | True for this isolated input change |
| New tool serves strict old consumer | `O_new ⊆ O_old` | False: `{ "status": "paused", "count": 0 }` uses a new enum value |
| Old tool serves new consumer | `O_old ⊆ O_new` | True for this isolated output change |

The output finding is conditional on strict/exhaustive old consumers. Schema acceptance does not establish application behavior. The annotation-only control leaves both validation schemas unchanged and still requires metadata review; advisory hints do not establish permissions or behavior.

## Scope and representation

These files are single-page `tools/list` result bodies (`{"tools": [...]}`), without JSON-RPC envelopes, cursors, sessions or runtime identifiers. Tool title, description, input/output schemas and annotations are preserved. Omitted fields are not filled with defaults. No ShenYu invocation configuration or credential reference is included.

`expected/structural_changes.json` uses RFC 6901 paths such as `/tools/0/inputSchema/required`. ChangeProof's raw `pointer` field instead uses semantic tool-name locators such as `/tools/fixture_lookup/inputSchema/required/workspace_id`; it must not be passed directly to a JSON Pointer resolver for these snapshots.

Object key order is ignored by the structural comparator. Array order is preserved. The single-tool array is traversed by index; changed schema arrays are reported as whole-array replacements. A sorted-key JSON digest is included only as an ASCII-fixture control. It is not RFC 8785 canonicalization or evidence of schema-semantic equivalence.

The public package includes the independently runnable fixture evaluator and recorded ChangeProof results. It excludes the commercial engine module. If that exact module is already available locally, rerun it with:

```bash
python reproduce_changeproof.py --module /path/to/changeproof/deep_verification_v12.py
```

The adapter checks the source SHA-256 before importing the module and compares all four reruns against the recorded reports. Without that module, the public verifier checks the contract examples, structural facts and recorded-report consistency; it does not recreate the proprietary engine execution.

No tool execution, ShenYu integration, generation consistency, concurrency, pinning enforcement, remote rollback or production migration was tested. No general agent accuracy estimate or maintainer endorsement is claimed.

References: [MCP tool definitions](https://modelcontextprotocol.io/specification/2025-06-18/server/tools), [JSON Schema 2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation).
