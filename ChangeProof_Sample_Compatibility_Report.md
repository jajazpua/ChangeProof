# ChangeProof — Sample Compatibility Report

**Historical demonstration.** Recorded output from an earlier ChangeProof V1.0 Sales Pilot run using bundled synthetic, non-sensitive fixtures. No external API was called, no payment was made, and no actual customer validation has been performed.

The version label identifies that historical run, not the current build. See the [public evidence index](docs/PUBLIC_EVIDENCE.md) for other versioned cases.

ChangeProof compares supplied definitions; it does **not** verify upstream authenticity, runtime behavior, or that a change will definitely break a particular client.

## Summary

| Source | Status | Review priority | Findings |
|---|---|---|---:|
| MCP | WARN | HIGH | 3 |
| OPENAPI | WARN | HIGH | 5 |

## MCP findings

- Before SHA-256: `9e0a9f456047f92c9bf669a9d19177f185cf16c7a8ee370a6c2435781ac959dc`
- After SHA-256: `2ec1ec1401bf7ddcbb6ebd0bf6809304c53943d4a3b29be717aaf31e943c8d2b`

| Severity | Finding | Target | Interpretation |
|---|---|---|---|
| HIGH | MCP_DESCRIPTION_CHANGED | send_email | Tool instructions changed; inspect for prompt-injection or misleading content |
| HIGH | MCP_INPUT_SCHEMA_CHANGED | send_email | Input contract changed; agent calls may need updating |
| HIGH | MCP_HINTS_CHANGED | send_email | Advisory safety annotations changed; these are NOT proof of actual behavior |

## OPENAPI findings

- Before SHA-256: `e7aa319986dc37862254e2b1abaf52fa17ff9c909069f15725a94cbe59e3d589`
- After SHA-256: `dfdab27da2e3ea6ce4489c602a4794a191d9284bbcc6ae8a988c08bd68304bc4`

| Severity | Finding | Target | Interpretation |
|---|---|---|---|
| REVIEW | API_OPERATION_ADDED | GET /health | New API operation; assess permissions and consumers |
| HIGH | API_SECURITY_CHANGED | GET /records | Effective operation security requirement changed; review authorization |
| HIGH | API_REFERENCED_SCHEMAS_CHANGED | GET /records | Referenced component schema changed; run contract tests |
| HIGH | API_OPERATION_CONTRACT_CHANGED | GET /records | Operation definition changed; impact not proven |
| HIGH | API_OPERATION_REMOVED | GET /reports | API operation removed; dependent clients may fail |

## Recommended review

1. Review each HIGH finding against actual client call patterns and authentication requirements.
2. Run downstream contract and integration tests before deployment.
3. Treat client-submitted definitions as unverified until their provenance is independently established.

## Scope and constraints

- Static comparison of synthetic MCP and OpenAPI 3.x JSON fixtures only.
- No MCP tool was executed, and no remote source was fetched.
- This report is evidence of the recorded comparison functionality, **not** of commercial demand, independent validation, or production payment readiness.
- Risk levels indicate review priority, not a measured probability of failure.
