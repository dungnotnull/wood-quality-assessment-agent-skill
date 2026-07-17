# Changelog

All notable changes to **wood-quality-assessment** are documented here.
The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-07-17

### Added — Reference grounding layer, executable tools registry, router
- `references/species_database.json` — 28 curated species profiles
  (family, wood type, porosity, density range, moisture benchmarks, T/R
  shrinkage, IAWA features, heartwood color, native origin, uses, documented
  substitution risks). Replaces prior placeholder listing.
- `references/cites_listings.json` — 16 CITES appendix listings (I/II/III)
  with annotations, listing dates, and notes.
- `references/iucn_status.json` — 28 IUCN Red List assessments.
- `scripts/seed_reference_data.py` — idempotent generator for the three
  reference datasets with cross-key integrity checks.
- `scripts/reference_data.py` — grounding layer: lazy-loaded, thread-safe,
  fuzzy-tolerant (Levenshtein <=2) species resolution plus genus-aware
  CITES/IUCN lookup, density comparison, moisture classification, and
  substitution-risk scoring. CLI for ad-hoc lookups.
- `scripts/tools_registry.py` — executable tools registry binding JSON
  Schema (Draft 7) input+output contracts to deterministic offline-safe
  Python handlers: `lookup_species`, `lookup_cites`, `lookup_iucn`,
  `compare_density`, `classify_moisture`, `assess_substitution`,
  `validate_schema`, `quality_gate`. Schema-validated execution; handler
  exceptions degrade gracefully (never raise to callers).
- `skills/sub-router.md` — chain-of-thought routing sub-skill invoked as
  Step 1.5 by `main.md`; emits an ordered run/skip plan, degradation
  forecast, and limitation notes based on `analysis_type`.
- `assets/examples/sample_output.md` — golden example output report
  (Scenario 1, Teak, Vietnamese) demonstrating all 11 quality gates passing.
- `tools/test_reference_data.py` — 52 unit tests for the grounding layer.
- `tools/test_tools_registry.py` — 52 unit tests for the tools registry.

### Changed
- `skills/main.md` — added Step 1.5 routing hook and references the offline
  grounding tools and tool registry.
- `scripts/setup.py` — validates the new reference datasets, example output,
  and bootstraps the tools registry (health report now 61 checks).
- `SKILL.md` — architecture tree, references/assets/scripts sections, and a
  new Routing & Tools Registry section; placeholder language removed.
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`, `CLAUDE.md`, `README.md`,
  `progression.json` — bumped to v1.1.0 and Phase 6 (grounding + tooling).

### Tests
- 251/251 orchestrator checks, 20/20 knowledge-updater unit tests,
  52/52 reference-data unit tests, 52/52 tools-registry unit tests.

## [1.0.0] — 2026-07-10

### Added — Production-grade open-source release
- Complete 6-phase build (Phase 0-5) — production ready.
- 7 domain sub-skills (`skills/sub-*.md`) with real reference data:
  70+ species normalization table, full IAWA hardwood (1-122) and softwood
  (S1-S27) feature codes, 25+ CITES-protected timber genera, 20+ IUCN-status
  species, EUTR/Lacey/VNFOREST/Japan/Australia legality frameworks.
- `skills/main.md` harness with 8-step execution protocol, 11 quality gates
  (U1-U6 universal + G1-G5 domain), 5-level graceful degradation protocol,
  Vietnamese/English language detection with translation table, 8-error
  recovery table, 12-section output template.
- `SECOND-KNOWLEDGE-BRAIN.md` living knowledge base: 7 sections, 14
  DOI-cited papers with Tier labels, genus-specific IAWA feature profiles.
- `tools/knowledge_updater.py` — production-grade crawl pipeline (Semantic
  Scholar + ArXiv + RSS) with SHA-256 dedup, composite scoring
  (recency 0.4 + relevance 0.4 + citations 0.2), dry-run mode, structured
  logging, type hints, dataclass model, exponential-backoff network layer.
- `tools/test_knowledge_updater.py` — 20 unit tests (pytest-compatible +
  standalone runner) covering hashing, scoring bounds, formatting, dedup,
  config validation, missing-brain robustness, dedup-on-append.
- `tools/run_test_scenarios.py` — orchestrator with 251 validation checks
  across 8 categories (file structure, sub-skill content, knowledge base,
  test scenarios, gate coverage, verdict coverage, harness architecture,
  cross-references). Offline-safe and deterministic.
- `tests/test-scenarios.md` — 7 concrete scenarios covering all 5 verdicts,
  all 11 gates, both languages (en/vi), CITES I/II/Not-listed, markets
  EU/USA/Vietnam/Global.
- `pyproject.toml` — proper Python packaging metadata, ruff/mypy/pytest
  config, CLI entry points (`wqa-knowledge-update`, `wqa-test-scenarios`,
  `wqa-test-knowledge`).
- `tools/__init__.py` — package marker enabling `python -m tools.*` execution.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` — open-source
  community files.
- `.github/workflows/ci.yml` — CI: lint (ruff), type-check (mypy), tests
  (unit + orchestrator) on push/PR across Python 3.11/3.12.
- `requirements-dev.txt` — pinned dev tooling (ruff, mypy, pytest, type stubs).

### Quality
- 251/251 structural validation checks pass.
- 20/20 unit tests pass.
- All 7 scenarios validated; all 5 verdicts and 11 gates exercised.
- Cross-file references verified consistent.

### Documentation
- `README.md`, `CLAUDE.md`, `PROJECT-detail.md`,
  `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`, `progression.json` — all current
  to Phase 5 / production ready.

[1.0.0]: https://github.com/972026/wood-quality-assessment/releases/tag/v1.0.0
