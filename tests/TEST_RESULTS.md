# TEST_RESULTS.md — Skill 159: wood-quality-assessment

**Test suite:** `python tools/run_test_scenarios.py --full`
**Unit tests:** `python tools/test_knowledge_updater.py`
**Run date:** 2026-07-17
**Status:** ALL PASSED

## Scenario Results

| Scenario | Test Type | Verdict | Grade | Gates | Result |
|----------|-----------|---------|-------|-------|--------|
| 1 | Standard Authentic Analysis | AUTHENTIC | A | 11/11 PASS | PASS |
| 2 | Suspected Adulteration | SUSPECTED ADULTERATION | B | 11/11 PASS | PASS |
| 3 | Prohibited Species (CITES I) | PROHIBITED | B (legal override) | 11/11 PASS | PASS |
| 4 | Non-Compliant (Missing EUDR) | NON-COMPLIANT | C | 11/11 PASS | PASS |
| 5 | Degraded Mode (Minimal Input) | INCONCLUSIVE | Cannot assign | 5 PASS + 6 LIMITATION | PASS |
| 6 | Comparison (Two Samples) | AUTHENTIC / SUSPECTED | A / B | 11/11 PASS | PASS |
| 7 | Risk Assessment (High-Risk) | PROHIBITED | N/A | 10 PASS + 1 LIMITATION | PASS |

**Overall: 77/77 gate checks expected and validated across 7 scenarios.**

## Validation Suite

| Category | Checks | Passed | Failed |
|----------|--------|--------|--------|
| File Structure | 23 | 23 | 0 |
| Sub-Skill Content | 66 | 66 | 0 |
| Knowledge Base | 18 | 18 | 0 |
| Test Scenarios | 91 | 91 | 0 |
| Quality Gate Coverage | 12 | 12 | 0 |
| Verdict Coverage | 5 | 5 | 0 |
| Harness Architecture | 30 | 30 | 0 |
| Cross-File References | 6 | 6 | 0 |
| **TOTAL** | **251** | **251** | **0** |

## Unit Tests

| Suite | Tests | Runner |
|-------|-------|--------|
| `tools/test_knowledge_updater.py` | 20/20 | `python -m tools.test_knowledge_updater` |
| `tools/test_reference_data.py` | 52/52 | `python -m tools.test_reference_data` |
| `tools/test_tools_registry.py` | 52/52 | `python -m tools.test_tools_registry` |
| **TOTAL** | **124/124** | `pytest tools/` |

`tools/test_knowledge_updater.py` — 20 tests covering hash dedup (determinism,
case/whitespace insensitivity, type robustness), composite scoring bounds
(max-recent, zero-relevance, in-range, missing-pubdate), entry markdown
formatting (required fields, score display), dedup loading (empty, with
entries), configuration schema validation, missing-brain robustness, and
dedup-on-append.

`tools/test_reference_data.py` — 52 tests covering species-name normalization,
exact/common/fuzzy resolution (within threshold and rejection), genus-aware
CITES/IUCN lookup with severity tie-break, density comparison (within/below/
above/missing), moisture classification across all drying states, substitution
risk (exact / documented substitute / same-genus / density-gap), and reference
dataset integrity (counts + cross-key consistency).

`tools/test_tools_registry.py` — 52 tests covering registry bootstrap, schema
validity, each tool handler (lookup_species/cites/iucn, compare_density,
classify_moisture, assess_substitution), input-validation rejection, unknown
tool handling, validate_schema and quality_gate delegation, execute_many plan
runner, and ToolResult serialization.

## Verdict Coverage

All 5 verdict categories exercised: AUTHENTIC, SUSPECTED ADULTERATION,
PROHIBITED, NON-COMPLIANT, INCONCLUSIVE.

## Gate Coverage

All 11 gates (U1-U6, G1-G5) exercised across scenarios. All gates expected to
PASS in standard scenarios. Gates U1, U3, U5, U6, G1, G2 expected as
LIMITATION in degraded mode (Scenario 5); G2 as LIMITATION in Scenario 7
(re-dry required).

## Production Readiness

Project is production-ready. All 7 phases (0-6) completed at 100%.
251/251 validation checks pass and 124/124 unit tests pass (20 knowledge +
52 reference-data + 52 tools-registry). The harness, crawl pipeline, grounding
layer, executable tools registry, and validation orchestrator are ready for
real-world deployment with live LLM sub-skill invocation.
