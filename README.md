# wood-quality-assessment

**Solid Wood & Handicraft Quality Assessment** — Wood Quality & Forestry-Standards Compliance evidence-backed analysis harness.

[![Claude Skill](https://img.shields.io/badge/Claude-Skill-blue)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests: 251/251](https://img.shields.io/badge/tests-251%2F251-brightgreen)](tests/TEST_RESULTS.md)
[![Unit Tests: 124/124](https://img.shields.io/badge/unit_tests-124%2F124-brightgreen)](tools/test_knowledge_updater.py)
[![Status: Production](https://img.shields.io/badge/status-production-success)](#production-readiness)
[![Version: 1.1.0](https://img.shields.io/badge/version-1.1.0-blue)](CHANGELOG.md)

A professional-grade Claude Code harness for **Wood Quality & Forestry-Standards
Compliance**. It gathers real-time authoritative data, applies recognized domain
methods (IAWA anatomy, MC/density benchmarks, CITES/IUCN legality), integrates
academic research, and delivers evidence-backed, risk-disclosed outputs through a
self-improving knowledge pipeline.

## Features

- **Real-time data aggregation** from authoritative forestry & timber-legality
  sources (CITES, IUCN, FSC/PEFC, InsideWood, Wood Database, USDA FPL).
- **Systematic domain analysis** with full IAWA hardwood (1-122) and softwood
  (S1-S27) feature coding, anatomical decision trees, and genus-specific profiles.
- **Academic research integration** with an auto-updating knowledge base
  (Semantic Scholar + ArXiv + RSS crawl, SHA-256 dedup, composite scoring).
- **Risk/limitation-disclosed outputs** with Best/Base/Worst scenarios and a
  5-category verdict framework (Authentic / Suspected Adulteration / Prohibited /
  Non-compliant / Inconclusive).
- **11 quality gates** (6 universal + 5 domain) with auto-fix and graceful
  degradation across 5 levels.
- **Vietnamese & English** language support with full translation tables.
- **Self-improving knowledge pipeline** (weekly academic + daily news cron).

## Installation

```bash
pip install -r requirements.txt          # runtime deps (requests, feedparser, dateutil)
pip install -r requirements-dev.txt       # dev tooling (ruff, mypy, pytest)
```

Install the skill files to `~/.claude/skills/` (or your project `CLAUDE.md`)
and invoke through Claude Code.

## Usage

```bash
# In Claude Code:
/wood-quality-assessment [your query]
```

Example queries:
- "Assess this teak sample: Tectona grandis, MC 11%, density 640 kg/m³, origin Vietnam, EU market"
- "Is this rosewood real? Claimed Dalbergia latifolia, end-grain photo attached, USA import"
- "Phân tích chất gỗ: Trắc (Dalbergia cochinchinensis), độ ẩm 13%, xuất xứ Việt Nam"

### Knowledge-base maintenance

```bash
python -m tools.knowledge_updater --dry-run       # preview crawl (no writes)
python -m tools.knowledge_updater                # append vetted entries to SKB
python -m tools.knowledge_updater --news-only    # CITES/ITTO RSS only
```

## Architecture

```
USER INPUT
    │
[skills/main.md — wood-quality-assessment harness]
    │
    ├─► sub-gather-requirements     → structured intake (species, photos, MC, density, origin, market)
    ├─► sub-router (Step 1.5)        → chain-of-thought run/skip plan by analysis_type
    ├─► sub-evidence-collector      → CITES, IUCN, legality, anatomy reference, physical benchmarks
    ├─► sub-grain-image-analysis    → IAWA feature coding → candidate species/genus
    ├─► sub-physical-property-analysis → MC state, density vs benchmark, drying, mechanical grade
    ├─► sub-authenticity-compliance → species match, substitution risk, CITES/IUCN, legality
    ├─► sub-knowledge-updater       → SECOND-KNOWLEDGE-BRAIN citations + gap flags
    └─► sub-quality-advisor         → verdict + grade + scenarios + risks + evidence chain
    │
    └─► [11 QUALITY GATES — U1-U6 + G1-G5] → verify → auto-fix → deliver
```

See `PROJECT-detail.md` for the full architecture diagram and `skills/main.md`
for the 8-step execution protocol.

## Quality Gates

Universal gates **U1–U6** (source count, disclosure ordering, evidence tiering,
language consistency, output template, claim traceability) plus domain gates
**G1–G5** (anatomy reference, moisture/density benchmarks, CITES/IUCN dual
check, verdict category validity, image-only uncertainty). Defined in
`skills/main.md`.

## Data Sources

- **CITES Checklist** — checklist.cites.org (Appendix I/II/III species status)
- **IUCN Red List** — iucnredlist.org (conservation status)
- **ITTO** — itto.int (tropical timber market & MIS statistics)
- **FSC** — fsc.org (chain-of-custody & responsible forestry rules)
- **PEFC** — pefc.org (sustainable forest certification)
- **The Wood Database** — wood-database.com (species physical & anatomical data)
- **InsideWood** — insidewood.lib.ncsu.edu (IAWA-coded wood anatomy atlas)
- **USDA Forest Products Laboratory** — fs.usda.gov/research/fpl (mechanics & drying)
- **EUTR/EUDR** — EU due-diligence & legality
- **US Lacey Act / APHIS** — plant & timber import legality
- **VNFOREST / VNTLAS** — Vietnam forestry & timber legality
- **IAWA** — International Association of Wood Anatomists (feature standards)

## Testing

```bash
python -m tools.test_knowledge_updater       # 20 unit tests for the crawl pipeline
python -m tools.test_reference_data         # 52 unit tests for the grounding layer
python -m tools.test_tools_registry         # 52 unit tests for the tools registry
python -m tools.run_test_scenarios --full    # 251-check structural validation
python -m tools.run_test_scenarios --all     # validate 7 scenario definitions
python -m scripts.tools_registry --list      # list executable tool handlers
python -m scripts.reference_data --list      # list cached species
pytest tools/                                 # pytest-compatible mode
```

## Knowledge Base

`SECOND-KNOWLEDGE-BRAIN.md` is a living knowledge base with 7 sections (IAWA
features, MC/drying, density/mechanics, CITES/legality, standards, papers,
methods). Auto-updated weekly via `tools/knowledge_updater.py` (cron schedule
documented in `CLAUDE.md`).

## Production Readiness

- **251/251** structural validation checks pass.
- **124/124** unit tests pass (20 knowledge + 52 reference-data + 52 tools-registry).
- All 6 phases (0-5) at 100% completion.
- Cross-file references verified consistent.
- CI: lint (ruff) + type-check (mypy) + tests on Python 3.11/3.12.

## Roadmap

- [x] Phase 0: Architecture
- [x] Phase 1: Core sub-skills
- [x] Phase 2: Main harness + gates
- [x] Phase 3: Knowledge pipeline
- [x] Phase 4: Testing
- [x] Phase 5: Integration & polish
- [x] Phase 6: Reference grounding data, executable tools registry, chain-of-thought router

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, content guidelines,
coding standards, and PR checklist. All contributions are licensed under MIT.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and deployment
best-practices.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT — see [LICENSE](LICENSE).

## Citation

```bibtex
@software{wood-quality-assessment,
  title  = {wood-quality-assessment: Solid Wood & Handicraft Quality Assessment},
  year   = {2026},
  version = {1.1.0},
  url    = {https://github.com/972026/wood-quality-assessment}
}
```
