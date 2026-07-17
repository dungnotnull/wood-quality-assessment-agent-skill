# CLAUDE.md — Skill 159: wood-quality-assessment

## Skill Identity
- **Skill Name:** `wood-quality-assessment`
- **Tagline:** Solid Wood & Handicraft Quality Assessment — Wood Quality & Forestry-Standards Compliance analysis & decision-support harness.
- **Current Phase:** Phase 6 — Grounding Layer, Tools Registry & Router (Production Ready)
- **Version:** 1.1.0
- **Folder:** `D:\972026\159-wood-quality-assessment\`

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Wood Quality & Forestry-Standards Compliance**. It gathers authoritative real-time and reference data, applies
recognized domain methods, cross-references academic research, and delivers
actionable outputs that are fully evidenced, risk/limitation-disclosed, and
traceable to authoritative sources — continuously self-improving through an
automated knowledge crawl pipeline.

---

## Harness Flow Summary

```
/wood-quality-assessment invoked
│
├─ Step 1: sub-gather-requirements   → Clarify the object under assessment (claimed species, sample photos, moisture reading & method, density if available, claimed origin, intended use, market/region) and language before any analysis.
├─ Step 2: sub-evidence-collector   → Fetch authoritative reference data for the candidate species: CITES Appendix status, IUCN status, FSC/PEFC rules, EUTR/Lacey/VNFOREST legality requirements, and a reference grain/anatomy atlas entry (InsideWood, Wood Database).
├─ Step 3: sub-grain-image-analysis   → Analyze provided grain/figure imagery using IAWA hardwood/softwood feature lists to estimate vessel arrangement, ray width, parenchyma pattern, ring density and boundaries, and color — yielding a candidate species/genus group.
├─ Step 4: sub-physical-property-analysis   → Interpret moisture content (MC%) and density (kg/m3) against species benchmarks and standards (ISO 3129, ASTM D143) to assess drying adequacy, dimensional stability and mechanical-grade suitability.
├─ Step 5: sub-authenticity-compliance   → Detect adulteration/substitution/mislabeling and assess legality: compare detected candidate species vs claimed species, and check candidates against CITES Appendices, IUCN status, and national bans (EUTR/Lacey/VNFOREST) and origin-mismatch illegal-logging risk.
├─ Step 6: sub-knowledge-updater   → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative wood-anatomy, drying, density, and CITES/standards evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
├─ Step 7: sub-quality-advisor   → Synthesize all prior analysis into a risk-disclosed verdict and grade with a full evidence chain and remediation actions.
└─ Step 8: main (quality gate)       → verify evidence hierarchy, disclosure, output polish
```

---

## Sub-Skills

| `skills/sub-gather-requirements.md` | Clarify the object under assessment (claimed species, sample photos, moisture reading & method, density if available, claimed origin, intended use, market/region) and language before any analysis. |
| `skills/sub-evidence-collector.md` | Fetch authoritative reference data for the candidate species: CITES Appendix status, IUCN status, FSC/PEFC rules, EUTR/Lacey/VNFOREST legality requirements, and a reference grain/anatomy atlas entry (InsideWood, Wood Database). |
| `skills/sub-grain-image-analysis.md` | Analyze provided grain/figure imagery using IAWA hardwood/softwood feature lists to estimate vessel arrangement, ray width, parenchyma pattern, ring density and boundaries, and color — yielding a candidate species/genus group. |
| `skills/sub-physical-property-analysis.md` | Interpret moisture content (MC%) and density (kg/m3) against species benchmarks and standards (ISO 3129, ASTM D143) to assess drying adequacy, dimensional stability and mechanical-grade suitability. |
| `skills/sub-authenticity-compliance.md` | Detect adulteration/substitution/mislabeling and assess legality: compare detected candidate species vs claimed species, and check candidates against CITES Appendices, IUCN status, and national bans (EUTR/Lacey/VNFOREST) and origin-mismatch illegal-logging risk. |
| `skills/sub-knowledge-updater.md` | Query SECOND-KNOWLEDGE-BRAIN.md for authoritative wood-anatomy, drying, density, and CITES/standards evidence; surface citations with tier labels and flag gaps for the crawl pipeline. |
| `skills/sub-quality-advisor.md` | Synthesize all prior analysis into a risk-disclosed verdict and grade with a full evidence chain and remediation actions. |

---

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Wood Quality & Forestry-Standards Compliance authoritative sources
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness

---

## Knowledge Sources

### Domain Authoritative Sources
- CITES Checklist — checklist.cites.org (Appendix I/II/III species status)
- IUCN Red List — iucnredlist.org (conservation status of candidate species)
- ITTO — itto.int (tropical timber market & MIS statistics)
- FSC — fsc.org (chain-of-custody & responsible forestry rules)
- PEFC — pefc.org (sustainable forest certification)
- The Wood Database — wood-database.com (species physical & anatomical data)
- InsideWood — insidewood.lib.ncsu.edu (IAWA-coded wood anatomy atlas)
- USDA Forest Products Laboratory — fs.usda.gov/research/fpl (mechanics & drying data)
- EU Timber Regulation (EUTR) — due-diligence & legality
- US Lacey Act / APHIS — plant & timber import legality
- VNFOREST — vnforest.gov.vn (Vietnam forestry & timber legality)
- IAWA — International Association of Wood Anatomists (feature standards)

### Academic & Research Sources
- IAWA Journal — wood anatomy & identification (Oxford)
- Wood Science and Technology — Springer
- Holzforschung — De Gruyter (wood chemistry & physics)
- European Journal of Wood and Wood Products — Springer
- Semantic Scholar — 'wood anatomy identification', 'wood density species'
- InsideWood anatomy database — coded reference atlas

### Academic Crawl Targets
- Semantic Scholar / Google Scholar for "Wood Quality & Forestry-Standards Compliance" keyword clusters
- Domain preprint servers where applicable
- Standards bodies and professional associations (see data sources)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/__init__.py` | Package marker; enables `python -m tools.*` execution |
| `tools/knowledge_updater.py` | Crawl pipeline: fetches latest papers + news → scores → appends to SECOND-KNOWLEDGE-BRAIN.md (structured logging, type hints, dataclass model, exponential backoff) |
| `tools/test_knowledge_updater.py` | 20 unit tests for knowledge_updater.py (pytest-compatible + standalone runner) |
| `tools/run_test_scenarios.py` | Test orchestrator: 251 validation checks across 8 categories (file structure, sub-skill content, knowledge base, scenarios, gate coverage, verdict coverage, harness architecture, cross-references) |
| `scripts/reference_data.py` | Grounding layer: loads references/*.json and exposes fuzzy species resolution, genus-aware CITES/IUCN lookup, density/moisture analysis, substitution-risk scoring (CLI: `python -m scripts.reference_data`) |
| `scripts/tools_registry.py` | Executable tool registry: 8 JSON-Schema-bound offline-safe handlers (lookup_species/cites/iucn, compare_density, classify_moisture, assess_substitution, validate_schema, quality_gate). CLI: `python -m scripts.tools_registry --list` |
| `scripts/seed_reference_data.py` | Idempotent generator for references/{species_database,cites_listings,iucn_status}.json with cross-key integrity |
| `tools/test_reference_data.py` | 52 unit tests for reference_data.py (pytest-compatible + standalone runner) |
| `tools/test_tools_registry.py` | 52 unit tests for tools_registry.py (pytest-compatible + standalone runner) |

Run with `python -m tools.<module>` or directly. CLI entry points are defined
in `pyproject.toml`: `wqa-knowledge-update`, `wqa-test-scenarios`,
`wqa-test-knowledge`.

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM)
0 8 * * 1 python -m tools.knowledge_updater >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM)
0 7 * * * python -m tools.knowledge_updater --news-only >> logs/knowledge_news.log 2>&1
```

Manual: `python -m tools.knowledge_updater --dry-run` | `--keywords "..."` | `--news-only` | `--log-level DEBUG`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (this file, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills
- [x] Phase 2: Main harness + quality gates
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation
- [x] Phase 5: Integration & polish
- [x] Production-grade open-source release (pyproject.toml, CI, CONTRIBUTING, CHANGELOG, CODE_OF_CONDUCT, SECURITY)
- [x] Phase 6: Reference grounding data, executable tools registry, chain-of-thought router, example output, grounding + tools unit tests

---

## References

- `skills/main.md` — harness entry point with full quality gate logic and language detection
- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap (all phases 100% complete)
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `progression.json` — skill progression and metadata
- `CONTRIBUTING.md` — development setup and contribution guide
- `CHANGELOG.md` — release history
- `SECURITY.md` — vulnerability reporting and deployment best-practices
- `pyproject.toml` — Python packaging, lint/type/test config, CLI entry points
- `D:\972026\SKILL-STANDARD.md` — library-wide standard
- Reference impl: `D:\vn-finance-analysis-hd-skill`
