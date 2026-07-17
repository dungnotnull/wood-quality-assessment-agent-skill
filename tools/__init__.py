"""wood-quality-assessment tools package.

Supporting Python tooling for the wood-quality-assessment Claude Code skill:

- ``knowledge_updater``   — crawl pipeline that fetches the latest papers and
  news, scores them, and appends vetted entries to SECOND-KNOWLEDGE-BRAIN.md.
- ``test_knowledge_updater`` — unit-test suite for the crawl pipeline.
- ``run_test_scenarios``  — production-grade test orchestrator that validates
  the harness architecture, sub-skill content, knowledge base structure, and
  quality-gate coverage.

All modules are runnable directly, e.g.::

    python -m tools.knowledge_updater --dry-run
    python -m tools.test_knowledge_updater
    python -m tools.run_test_scenarios --full
"""

__version__ = "1.0.0"
__all__ = ["knowledge_updater", "test_knowledge_updater", "run_test_scenarios"]
