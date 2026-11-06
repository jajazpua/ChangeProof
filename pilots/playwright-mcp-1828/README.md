# Playwright MCP #1828 — evidence-backed contract review

**Issue:** https://github.com/microsoft/playwright-mcp/issues/1828

**Pinned source:** https://github.com/microsoft/playwright/tree/58d69dcc392af3a6994eab0323dc2e883f05f396 (the source revision named by the reporter).

**Method:** Manual, source-anchored comparison between tool input schemas, MCP schema export and handlers. This is **not a live Playwright MCP test**, a ChangeProof engine run, or a demonstrated security exploit. Source lines are listed in the [machine-readable evidence](./evidence.json), with a [read-only static verifier](./verify_source.py).

## Findings

### A. Five defaulted inputs across four tools are at risk of being incorrectly advertised as required

The exporter in [tool.ts lines 30–39](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/utils/mcp/tool.ts#L30-L39) calls the Zod JSON-Schema generator without specifying input mode. The reporter's tools/list observation says that the defaults below appear in the required list, despite the accepted input shape allowing omission:

| Tool | Field | Zod declaration | Source |
|---|---|---|---|
| browser_take_screenshot | scale | default(css) | [screenshot.ts L33](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/screenshot.ts#L33) |
| browser_console_messages | level | default(info) | [console.ts L27](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/console.ts#L27) |
| browser_network_requests | static | default(false) | [network.ts L38](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/network.ts#L38) |
| browser_mouse_wheel | deltaX, deltaY | default(0) | [mouse.ts L95–96](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/mouse.ts#L95-L96) |

**Smallest potential correction to test:** supply the option shown below; validate all tool schemas before adopting it as a global change.

~~~ts
// current
inputSchema: zod.toJSONSchema(tool.inputSchema) as mcpServer.Tool['inputSchema'],
// candidate
inputSchema: zod.toJSONSchema(tool.inputSchema, { io: 'input' }) as mcpServer.Tool['inputSchema'],
~~~

**Acceptance check:** an omitted defaulted field succeeds in the real tool parser and the generated tools/list input schema does not mark it required. Genuinely required fields must remain in required.

### B. Tool-level annotations flatten conditional side effects

[tool.ts L30–39](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/utils/mcp/tool.ts#L30-L39) sets readOnlyHint based on tool category, with destructiveHint as its boolean inverse. But:

* browser_take_screenshot is classified readOnly and saves an output file even with no explicit filename ([screenshot.ts L55, L75–84](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/screenshot.ts#L55-L84)).
* browser_console_messages is classified readOnly and can write a result when filename is set ([console.ts L27–40](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/console.ts#L27-L40)).
* browser_tabs is classified as an action for its list, new, close and select branches ([tabs.ts L25–40](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/tabs.ts#L25-L40)). Note that list calls ensureTab, so it should not automatically be assumed to have zero effects in all states.

These hints are **advisory**, not authorization guarantees. Consider an explicit per-tool side-effect audit, documenting file-output behavior; for argument-dependent behavior, tool splitting or conservative hints may be more accurate than a single derived boolean.

### C. Missing lower bound on wait duration

[browser_wait_for.time](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/wait.ts#L30) is z.number().optional(). Negative values can pass the schema and reach the truthiness/Math.min branch ([wait.ts L42](https://github.com/microsoft/playwright/blob/58d69dcc392af3a6994eab0323dc2e883f05f396/packages/playwright-core/src/tools/backend/wait.ts#L42)). The original reporter also describes invalid resize dimensions; that case was not independently reproduced here. Test negative, zero, valid and excessive values before choosing positive/integer bounds; new validation may itself change compatibility.

## Reproduction and scope

The dependency-free Python checker tests 14 **literal, pinned source lines**, not live network traffic or tool behavior:

~~~bash
python pilots/playwright-mcp-1828/verify_source.py
# Validates bundled evidence metadata only.

git clone https://github.com/microsoft/playwright.git
cd playwright
git checkout 58d69dcc392af3a6994eab0323dc2e883f05f396
python ../ChangeProof/pilots/playwright-mcp-1828/verify_source.py .
~~~

A separate test in the actual server environment should compare the exported tools/list schema with argument parsing, check file writes under controlled output-directory policy, and assert invalid input rejection. The reporter's observed runtime failures are attributed to the issue report, **not** claimed as results of our own execution.

**Recommended first test:** one requiredness regression for a defaulted input (scale), then extend to the other listed fields. This is a narrowly scoped, reproducible improvement without modifying browser behavior.

This is a manually prepared technical contribution related to ChangeProof, not a paid engagement or an endorsement by Microsoft/Playwright.
