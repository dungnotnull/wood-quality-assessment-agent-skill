# Contributing to wood-quality-assessment

Thank you for your interest in improving **wood-quality-assessment** — a
professional-grade Claude Code harness for Wood Quality & Forestry-Standards
Compliance. This document explains how to contribute effectively.

---

## Project Structure

```
wood-quality-assessment/
├── skills/                       # Markdown sub-skill definitions (the harness)
│   ├── main.md                    #   Harness entry point + 11 quality gates
│   └── sub-*.md                   #   7 domain sub-skills
├── tools/                         # Python tooling (crawl pipeline + tests)
│   ├── knowledge_updater.py       #   Crawl → score → append pipeline
│   ├── test_knowledge_updater.py  #   Unit tests for the pipeline
│   └── run_test_scenarios.py      #   Full harness validation orchestrator
├── tests/                         # Test scenarios + results
│   ├── test-scenarios.md          #   7 concrete scenario definitions
│   └── TEST_RESULTS.md            #   Latest documented run
├── SECOND-KNOWLEDGE-BRAIN.md      # Living knowledge base (auto-updated)
├── CLAUDE.md                      # Skill manifest / harness summary
├── PROJECT-detail.md              # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # Build roadmap + status
├── progression.json               # Machine-readable project metadata
└── pyproject.toml                 # Python packaging + lint config
```

The core deliverable is a **markdown-based skill harness** executed by Claude
Code. The Python tools support the harness (crawl pipeline, validation,
tests).

---

## How to Contribute

### Reporting Issues

Open an issue with:
- A clear title describing the problem.
- The exact command or skill invocation that triggered it.
- Expected vs actual behavior.
- Relevant file paths and line numbers.
- For wood-identification inaccuracies: the species, the IAWA features used,
  and the reference source consulted.

### Suggesting Enhancements

- Describe the use case the enhancement serves.
- Reference the relevant sub-skill file (e.g. `skills/sub-grain-image-analysis.md`).
- Where possible, cite the authoritative source (CITES, IUCN, IAWA, ISO/EN/ASTM)
  that supports the change.

### Pull Requests

1. Fork the repository and create a branch:
   `git checkout -b fix/descriptive-name` or `feat/descriptive-name`.
2. Make your changes. Keep edits focused — one logical change per PR.
3. **Run the full validation suite before opening a PR:**
   ```bash
   python tools/test_knowledge_updater.py
   python tools/run_test_scenarios.py --full
   ```
   Both must pass with 0 failures. The orchestrator enforces 251+ structural
   checks across the harness.
4. If you change `SECOND-KNOWLEDGE-BRAIN.md` or sub-skill content, confirm the
   orchestrator's section checks still pass.
5. Update `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` if your change touches a
   phase deliverable.
6. Write a clear PR description referencing the issue number.

---

## Content Guidelines

### Sub-skill markdown
- Every sub-skill MUST have: front-matter (`name`, `description`), a
  `## Role & Persona` section, a `## Workflow`, a `## Tools` section, an
  `## Output Format`, and a `## Quality Gates` checklist.
- Never assert species identity without an IAWA-coded feature or cited
  anatomical reference.
- Always disclose limitations before recommendations.

### Knowledge base (SECOND-KNOWLEDGE-BRAIN.md)
- New entries are appended ONLY by `tools/knowledge_updater.py` (or a PR that
  follows the same Tier-labeled markdown block format).
- Every paper entry needs: DOI/URL, Tier (1-4), Year, Venue, Authors, Key Finding.
- Prefer Tier 1-2 (official standards, peer-reviewed) over Tier 3-4.

### Crawl pipeline (Python)
- Keep `KNOWLEDGE_CONFIG` keys stable — tests and cron rely on them.
- Use the module-level `_LOG` logger; do not add bare `print()` calls.
- Never raise on a single source failure — degrade to `[]` and log a warning.
- Add a unit test for any new public function.

---

## Coding Standards

- Python ≥ 3.11. Use `from __future__ import annotations`.
- Format with `ruff` (`ruff check --fix tools/`); configs live in `pyproject.toml`.
- Type-check with `mypy` (`mypy tools/`).
- Prefer explicit types; avoid `Any` except for unstructured crawl payloads.
- Functions that can fail on missing dependencies (requests/feedparser) must
  return `None`/`[]` rather than raising.

---

## Testing

- `python -m tools.test_knowledge_updater` — 20 unit tests for the crawl pipeline.
- `python -m tools.run_test_scenarios --full` — 251 structural checks for the
  full harness (file structure, sub-skill content, knowledge base, gate
  coverage, verdict coverage, architecture, cross-references).
- `python -m tools.run_test_scenarios --all` — validate the 7 scenario
  definitions.
- Optional: `pytest tools/` runs the pytest-compatible test functions.

---

## License

By contributing you agree your contributions are licensed under the project's
[MIT License](LICENSE).
