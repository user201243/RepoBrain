# Self Review

## What Is Strong Right Now

- The repo has a coherent thesis instead of being a random search prototype.
- CLI, storage, scanner, retrieval, and MCP-style transport are separated cleanly.
- Parser selection now has an adapter seam instead of being hard-wired to regex heuristics.
- The local chat loop makes the product easier to try without changing the core engine contract.
- Docs already explain the product, not just the code.
- The fixture pack is aligned to the acceptance queries, which keeps iteration practical.

## What Is Intentionally Thin

- call graph extraction is heuristic, not deep semantic analysis
- confidence is rule-based, not calibrated
- provider adapters are SDK-backed, including Gemini, but remote paths still need live-key smoke testing outside CI
- MCP transport is a lightweight stdio JSON adapter, not a full protocol implementation

## Where The MVP Could Mislead Users

- high scores can still look more certain than the evidence really deserves
- TS/JS parsing is still shallow when optional tree-sitter packages are unavailable
- import-based edges do not yet prove real runtime flow
- benchmark quality on fixtures is not the same as real-world benchmark quality

## Technical Debt To Pay Down First

1. deepen tree-sitter extraction and add CI coverage with optional parser packages
2. make retrieval fusion more principled
3. tighten warning logic for sparse or contradictory evidence
4. expand fixtures into more realistic route/service/config patterns

## What A Senior Engineer Should Do Next

- add more deterministic scoring tests around reranking and confidence
- introduce richer role extraction for frameworks like FastAPI, Express, and Next.js
- add live-provider smoke docs once a public repo and test keys strategy exist
- improve chat output with compact summaries after confidence calibration improves

## Release Risks

- users may assume "trace" means exact runtime truth rather than likely grounded flow
- users may over-trust edit targets if confidence UX stays too optimistic
- docs can drift if future implementation changes are not reflected here

## Bottom Line

The MVP is a good architecture and narrative foundation. It is not yet a final retrieval engine, but it is already shaped like a product with a believable trust model and a clear path to becoming genuinely useful.
