# Denkeeper #583 — synthetic MCP descriptor-drift pilot report

**Date:** 2026-11-02. **Source issue:** https://github.com/Temikus/denkeeper/issues/583

**Status:** 44 offline checks passed in a local independent verifier. This is a synthetic fixture, **not** a production Denkeeper test or a run of the proprietary ChangeProof engine.

## Summary

The MCP tool `note_update` retains exactly the same name across the six controlled after states. The following changes are compared independently:

| Scenario | Changed field | Proposed pin changes? | Finding |
| --- | --- | --- | --- |
| description_only | `description` | Yes | Instruction text drift requires review, no proof of malicious prompt. |
| annotation_only | `annotations.readOnlyHint`: false → true | Yes | Higher-risk behavioral claim; require operator re-approval before trusting. |
| input_required_only | `inputSchema.required` adds `approval_code` | Yes | Existing caller without this field is rejected under the new schema. |
| output_enum_only | `outputSchema.properties.status.enum` adds `queued` | **No** | Strict old output consumer may reject the new value; the proposed digest omits outputSchema. |
| combined | All four independent changes | Yes | Separate schema compatibility from metadata and security review. |
| key_order_only | Object-property order only | No | Raw bytes differ but equivalent JSON objects give the same sorted-key test digest. |

## Reproducible input/output witnesses

- `{"note_id":"N-1"}`: accepted by old input schema; rejected after the new required `approval_code`.
- `{"note_id":"N-1","approval_code":"okay"}`: accepted by both, because unspecified additional properties are permitted in this fixture.
- `{"status":"queued"}`: rejected by strict old output schema; accepted by the new output schema.
- `{"status":"updated"}`: accepted by both output schemas.

These are schema acceptance checks for particular examples. They do not prove runtime behavior or general JSON Schema inclusion.

## Observation and recommendation

Denkeeper's issue proposes pinning `sha256(name, description, inputSchema, annotations)`. This projection protects the listed fields but does not cover the optional MCP `outputSchema` or `title`. **Recommendation:** decide and document whether all supported client-visible fields should be pinned, and test output-only changes explicitly. Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools

The `readOnlyHint` false-to-true case should be treated as an operator review event even with unchanged schema and tool name. Tool annotations are **untrusted claims**; trust-tier or dry-run enforcement needs independent controls. Description-only drift may merit review without being a structural schema break.

For an actual Denkeeper acceptance test, verify snapshot persistence, first registration, restart rediscovery, health-probe rediscovery, isolation of only the changed tool, audit entries, explicit operator re-pin, and fail-closed behavior. **None of these runtime paths were tested here.**

## Evidence

- Seven local snapshot hashes: [SHA256SUMS.json](SHA256SUMS.json).
- Offline test program: [verify.py](verify.py) and [requirements.txt](requirements.txt).
- Seven fixture files: [snapshots/](snapshots/).
- Recorded run: six scenario assertions, four schema witnesses, all seven raw byte digests; total 44 scoped checks.

Hash normalization uses sorted JSON keys **for this restricted ASCII fixture**. It is *not* RFC 8785, and source-file hashes do not authenticate a deployed server.

**Non-claims:** no actual Denkeeper vulnerability exploited, no production API inspected, no claim of developer endorsement, no paid customer engagement.
