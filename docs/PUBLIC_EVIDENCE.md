# Public evidence and technical case studies

[← ChangeProof overview](../README.md) · [Request a supervised pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)

ChangeProof publishes inspectable MCP/OpenAPI compatibility research. **These are different kinds of evidence, not a list of paying customers, third-party certifications or production deployments.** A source-anchored audit, a synthetic test fixture and a ChangeProof-generated report answer different questions.

## Evidence at a glance

| Case | Evidence type | Main technical result | Scope |
| --- | --- | --- | --- |
| **[UniFi Network API — 10.4.57 → 11.0.97](../ChangeProof_UniFi_68_Validated_Pilot_Report.md)** | Existing ChangeProof engine + semantic review of supplied OpenAPI versions | Required switch-stack `members` → `units` representation change; related LAG and model changes | Static contract findings; client/runtime breakage not verified |
| **[Apache ShenYu #7935](../pilots/shenyu-7935/README.md)** | Synthetic MCP `tools/list` fixtures, recorded ChangeProof V1.2.3 results + independent verifier | New required input, expanded output enum and changed annotation analyzed separately | Synthetic regression contribution, not a deployed ShenYu integration |
| **[Denkeeper #583](../pilots/denkeeper-583/README.md)** | Synthetic MCP snapshots + independent offline verifier | Descriptor/annotation drift, required input and output-only change that a proposed hash omits; 44 scoped local checks recorded | Not a Denkeeper runtime test or a ChangeProof engine execution |
| **[Microsoft Playwright MCP #1828](https://github.com/jajazpua/ChangeProof/blob/415a46e13ab2c132ecfde931ddb7ecf5f081117b/pilots/playwright-mcp-1828/README.md)** | Manual source-anchored technical review | Defaulted inputs potentially advertised as required, conditional side effects and numeric-validation gaps; 14 source anchors | No live MCP execution; review stored on a separate evidence branch |
| **[1platformlabs #84](../pilots/1platformlabs-84/REPORT.md)** | Read-only inspection of public contract-drift evidence and deployment workflow | Published documentation contract is stale relative to the newer API artifacts; proposes reviewed spec refresh | Not a full independently executed before/after ChangeProof comparison |

## Featured: UniFi — a real OpenAPI version comparison

[Read the detailed report](../ChangeProof_UniFi_68_Validated_Pilot_Report.md)

**Question:** Which published contract changes should API consumers inspect before moving from 10.4.57 to 11.0.97?

**Evidence:** The supplied JSON contracts, recorded input SHA-256 values, schema paths and recommended downstream tests. The report records **42 granular findings: 9 HIGH-priority candidates and 33 REVIEW items**. Several findings describe the *same underlying migration*; they are not 42 independently demonstrated application failures.

**Primary change:** `IntegrationSwitchStackDto.members` is no longer represented as before; the candidate uses a required `units` collection with a different referenced item model. Strict/generated clients relying on the old representation may need attention.

**Boundary:** These are definition-level findings from the existing ChangeProof pipeline and semantic review. No specific production consumer failure is established.

## Apache ShenYu — a reproducible MCP regression contribution

[Fixture README](../pilots/shenyu-7935/README.md) · [Findings](../pilots/shenyu-7935/REPORT.md) · [Upstream issue](https://github.com/apache/shenyu/issues/7935) · [Submitted PR #8309](https://github.com/apache/shenyu/pull/8309)

The fixture makes compatibility *direction* explicit:

- **Inputs:** an optional `workspace_id` becomes required. Previously valid callers may fail under the new schema.
- **Outputs:** a `status` enum gains `paused`. Strict older output consumers may reject the new value.
- **Annotations:** `readOnlyHint` changes, which calls for policy review rather than an automatic runtime-safety conclusion.
- **Controls:** changed object key order should not imply a structural change; complex schema composition must produce a qualified, limited conclusion.

Recorded results came from the existing ChangeProof V1.2.3 module; an independent script checks the fixture facts and witnesses. The publicly linked PR is a **submitted contribution**, not evidence of a merged upstream change or maintainer endorsement.

## Denkeeper — drift and safety-metadata controls

[Fixture README](../pilots/denkeeper-583/README.md) · [Technical report](../pilots/denkeeper-583/REPORT.md) · [Upstream discussion](https://github.com/Temikus/denkeeper/issues/583)

A public/synthetic fixture checks six controlled changes, including `readOnlyHint: false → true`, an added required input, and an output enum expansion. The recorded independent offline verification passed **44 scoped checks**.

**Important observation:** the proposed descriptor hash over name, description, input schema and annotations misses changes confined to `outputSchema`. This is a finding about the proposal's field selection, **not proof of a real Denkeeper exploit or runtime defect**. The package was prepared after the issue author welcomed a fixture; this is not a commercial engagement.

## Playwright MCP — source-anchored review, not an engine benchmark

[Read the source review](https://github.com/jajazpua/ChangeProof/blob/415a46e13ab2c132ecfde931ddb7ecf5f081117b/pilots/playwright-mcp-1828/README.md) · [Machine-readable anchors](https://github.com/jajazpua/ChangeProof/blob/415a46e13ab2c132ecfde931ddb7ecf5f081117b/pilots/playwright-mcp-1828/evidence.json) · [Upstream issue #1828](https://github.com/microsoft/playwright-mcp/issues/1828)

The source audit identifies five defaulted tool arguments across four tools and their schema-export path, plus advisory annotation mappings that compress conditional file-writing behavior. Fourteen source lines are indexed as evidence anchors, **not fourteen distinct defects**.

The report proposes focused acceptance tests for `tools/list` and actual argument parsing. No live server/tool execution or ChangeProof engine run is claimed.

## 1platformlabs — public workflow and specification drift triage

[Read the review](../pilots/1platformlabs-84/REPORT.md) · [Upstream issue #84](https://github.com/1platformlabs/1platform-api-developer/issues/84)

A read-only investigation found that the site serves committed versioned OpenAPI files while a drift workflow reports changes without updating those files. The recommended remediation is a reviewed specification-refresh PR, with verification after merge. Some full before/after counts come from the upstream comparator rather than our independent execution, as the report explains.

## Synthetic demo — what a ChangeProof-style finding looks like

[View the sample MCP/OpenAPI report](../ChangeProof_Sample_Compatibility_Report.md)

The demo is explicitly synthetic. A simple illustrative input-contract change:

| Before | After | Interpretation |
| --- | --- | --- |
| `required: ["query"]` | `required: ["query", "workspace_id"]` | Existing callers omitting `workspace_id` are breaking candidates under the new schema |

This table illustrates contract reasoning; it is **not** a measured production failure.

## How to interpret the evidence

- **Structural evidence:** exact JSON fields, types, required arrays, references and metadata differ.
- **Compatibility direction:** the kinds of old/new callers and consumers that may be affected, subject to schema semantics and stated assumptions.
- **Reproducibility:** public snapshots, source links, inputs, hashes or scripts as available in each specific report.
- **Explicit unknowns:** runtime behavior, service availability, permissions, upstream provenance and particular consumer failures require independent validation.
- **No endorsements implied:** upstream issues/PRs identify technical discussions, not customers, partners or acceptance of ChangeProof.

## Request a review

For a focused, **free supervised pilot**, provide two public/sanitized contract revisions and one compatibility question:

**[Request a pilot through the ChangeProof site](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)** · **[Request a scoped paid quote](https://github.com/jajazpua/ChangeProof/issues/new?template=quote-request.yml)**

Paid work requires individual agreement on scope, delivery and price. No public unattended analysis endpoint or automated checkout is currently offered.
