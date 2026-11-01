# Synthetic MCP compatibility fixture for ShenYu #7935

This package addresses the requested combined case and adds three controls. The source is a synthetic `fixture_lookup` tool; no deployed ShenYu data is represented.

## Combined result

The unchanged ChangeProof V1.2.3 module returned **REVIEW_REQUIRED**, `comparison_complete: true`, with three findings. Here `comparison_complete` is the engine's static-traversal flag, not proof of semantic or runtime completeness.

| Structural fact | Expected compatibility judgment | Recorded finding |
| --- | --- | --- |
| Existing optional `workspace_id` becomes required | Old callers may be rejected by the new tool (`I_old ⊄ I_new`) | `REQUIRED_ADDED`, request, `BREAKING_CANDIDATE` |
| Output `status` enum adds `paused` | New output may be rejected by strict old consumers (`O_new ⊄ O_old`) | `ENUM_VALUES_ADDED`, response, `BREAKING_CANDIDATE` |
| `readOnlyHint` changes from `true` to `false` | Review metadata/client policy; do not infer runtime side effects or authorization | `TOOL_HINTS_CHANGED`, tool, `REVIEW` |

Four JSON instances are independently validated against both revisions. The old request without `workspace_id` is valid before and invalid after (`required`). The new `paused` output is valid after and invalid before (`enum`). One request with the field and one old output remain valid under both versions. These concrete examples do not measure overall analyzer accuracy.

The reverse inclusion directions hold for this fixture because the input edit only adds an already declared property to `required`, and the output edit only expands one enum. The independent script checks that no other schema constraints change before using those arguments.

## Controls

| Case | Recorded status | Expected behavior |
| --- | --- | --- |
| Annotation only | `REVIEW_REQUIRED`, complete `true` | One metadata finding; both input and output validation schemas unchanged |
| Changed `allOf` / `not` | `INDETERMINATE`, complete `false` | `COMPLEX_SCHEMA_CHANGED` plus `COMPLEX_COMPOSITION`; require review, no compatibility direction established |
| Object key order only | `NO_CHANGE`, complete `true` | Zero structural findings; file-byte hashes differ, parsed JSON and fixture sorted-key digests match |

The unsupported control is valid JSON Schema; "unsupported" refers to compatibility reasoning in this ChangeProof version. A validator's ability to accept individual instances is separate from establishing compatibility between two schemas.

## Reproducibility and limits

Expected directions and literal structural facts are separate files from the actual engine outputs. The public script independently checks those facts and witnesses and verifies recorded-report consistency. A separate optional adapter reproduces the engine reports when the exact commercial module is available; that module is not redistributed here. Source SHA-256 and environment versions are recorded.

All four observed engine runs used `deep-verification-v1.2.3` without source edits. No external tool call, live API, ShenYu runtime, generation/concurrency mechanism or pinning enforcement was exercised. This package proposes a regression fixture; it is not a runtime safety guarantee, a completed ShenYu integration or evidence of general ChangeProof accuracy.
