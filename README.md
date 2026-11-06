# ChangeProof

**Know what changed before your AI agent or API client breaks.**

**Evidence-backed MCP & OpenAPI contract compatibility reviews.** Compare two versions of a tool definition or API specification, identify potential breaking changes, and receive inspectable findings with scope and uncertainty stated plainly.

**[Request a free compatibility pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)** · **[Explore public evidence](docs/PUBLIC_EVIDENCE.md)** · **[Request a paid quote](https://github.com/jajazpua/ChangeProof/issues/new?template=quote-request.yml)**

> **Available today:** owner-supervised, manually reviewed compatibility checks. **Not yet available:** public self-service analysis API, unattended paid MCP endpoint or automated checkout. The backend and private infrastructure are not distributed here.

## Preview the report you receive

[![ChangeProof synthetic MCP and OpenAPI report preview](docs/assets/compatibility-demo-preview.svg)](demo/README.md)

*Visual preview of the [published synthetic sample](ChangeProof_Sample_Compatibility_Report.md): 8 finding records, 7 HIGH review-priority items and 1 REVIEW. **Illustration only** — not a live API check, independent accuracy benchmark or a customer case.*

**[Explore the HTML demo and how to open it](demo/README.md)** · **[View HTML source](demo/ChangeProof_Compatibility_Demo.html)** · **[Inspect machine-readable demo findings](demo/findings.json)**

The HTML demonstration is a **standalone local file**. GitHub displays HTML source rather than hosting or executing the file. Open the [demo guide](demo/README.md) to download and view it in a browser. No separate site is created.

## See the problem in 10 seconds

An MCP tool keeps the same name, but a previously optional argument becomes required:

| Contract | Accepted input requirement |
| --- | --- |
| **BEFORE** | `required: ["query"]` |
| **AFTER** | `required: ["query", "workspace_id"]` |
| **ChangeProof-style finding** | **BREAKING CANDIDATE** — an existing caller that sends only `query` may be rejected by the new input schema. |

*Illustrative synthetic example. A contract finding is not proof that any particular production agent failed.*

ChangeProof separates **what changed**, **who could be affected**, and **what still needs a test**.

## Real public evidence, with precise limits

| Case | What was examined | Evidence |
| --- | --- | --- |
| **UniFi Network API** | Two real OpenAPI contract versions; a required `members` → `units` switch-stack representation change and related schema migration | [Static compatibility report](ChangeProof_UniFi_68_Validated_Pilot_Report.md) |
| **Apache ShenYu #7935** | Synthetic MCP before/after contract snapshots, compatibility directions and recorded ChangeProof results | [Reproducible fixture](pilots/shenyu-7935/README.md) · [Submitted PR #8309](https://github.com/apache/shenyu/pull/8309) |
| **Denkeeper #583** | Synthetic MCP descriptor and safety-metadata drift; 44 scoped independent offline checks | [Fixture and findings](pilots/denkeeper-583/README.md) |
| **Microsoft Playwright MCP #1828** | Source-level review of defaulted parameters, annotations and input validation; 14 evidence anchors | [Source-anchored report](https://github.com/jajazpua/ChangeProof/blob/415a46e13ab2c132ecfde931ddb7ecf5f081117b/pilots/playwright-mcp-1828/README.md) |

**[Browse the full public evidence index, including 1platformlabs](docs/PUBLIC_EVIDENCE.md)** · **[Open a synthetic sample report](ChangeProof_Sample_Compatibility_Report.md)**

These examples have **different validation levels**. The Playwright report is a manual code audit, not a ChangeProof engine execution; Denkeeper uses an independent fixture verifier; ShenYu is a synthetic contribution, not a merged production integration. None is presented as a paying-customer testimonial or third-party certification.

## What a compatibility review delivers

| Review area | Typical result |
| --- | --- |
| **MCP `tools/list`** | Added/removed tools, required argument changes, schema/enum differences, metadata and annotation drift |
| **OpenAPI** | Added/removed operations; changes to request/response schemas, referenced models and required properties |
| **Evidence and reproducibility** | Source references, relevant before/after facts, machine-readable findings and hashes when inputs are available |
| **Compatibility assessment** | Breaking candidates vs. review-only changes; input/output direction and known limitations |
| **Actionable next steps** | Targeted contract/integration tests for affected clients before deployment |

A report is not a guarantee of runtime compatibility or a substitute for authorization, integration testing or application-specific validation. Multiple technical findings may describe one underlying migration.

## How the supervised pilot works

1. **Ask one question.** Submit a [free pilot request](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot), e.g. “Will this new required tool argument break old callers?”
2. **Supply contract versions.** Link to two **public or sanitized** MCP `tools/list` JSON snapshots or OpenAPI JSON/YAML specifications, preferably with version identifiers.
3. **Owner reviews suitability.** We verify the scope and safe inputs, then run an appropriate local analysis where supported.
4. **Receive reviewed findings.** We inspect the results before delivery, distinguish structural changes from compatibility judgments, and disclose what was not tested.

No GitHub token, production access, installation, wallet key or private data is required for a public/sanitized pilot. Please never post secrets in GitHub Issues.

**[Start a free pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)** · [Public GitHub pilot form](https://github.com/jajazpua/ChangeProof/issues/new?template=pilot-request.yml)

## Work with ChangeProof

**One compatibility question, or a larger API/MCP migration?** Choose the request that fits your situation:

| Service | Best for | Next step |
| --- | --- | --- |
| **Free supervised pilot** | One focused compatibility question using two public or sanitized definitions | **[Request a free pilot](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot)** |
| **Scoped paid review** | Larger migrations, multiple tools or operations, higher-volume reviews, or repeat monitoring needs | **[Request a manual quote](https://github.com/jajazpua/ChangeProof/issues/new?template=quote-request.yml)** |

### Deliverables to agree before the review

- **Reviewed findings:** what changed, where, and which changes are breaking candidates versus items needing human review.
- **Inspectable evidence:** affected tool/operation/schema locations, before/after facts and hashes where original inputs are supplied.
- **Integration recommendations:** targeted tests for actual callers, generated clients or deployment policy.
- **Report format:** a human-readable summary plus structured findings; HTML/JSON files and reproducibility materials when supported and agreed for the case.

**Commercial terms:** scope, format, turnaround, price and payment method are agreed **manually before paid work begins**. There is no automatic checkout or public unattended analysis API. We will not request production credentials or private contracts in public GitHub issues.

**[See an example of the deliverable format](demo/README.md)** · **[Get a scoped quote](https://github.com/jajazpua/ChangeProof/issues/new?template=quote-request.yml)**

## Scope and integrity

- Contract-level comparisons are conservative: they do not prove deployment safety, tool side effects, schema-semantic equivalence or a specific client failure without further evidence.
- SHA-256 identifies the exact supplied bytes, not the authenticity of an upstream origin.
- Public case studies are technical contributions and investigations, not vendor endorsements or customer references.
- This repository publishes the product overview and selected evidence, **not** the proprietary ChangeProof backend, private keys or production infrastructure. No license for unpublished code is implied.

---

**Have two contract revisions?** [Request a supervised ChangeProof compatibility check](https://changeproof-agent-checks.russet-spark-1861.chatgpt.site/#/pilot).
