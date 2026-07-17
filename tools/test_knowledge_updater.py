"""test_knowledge_updater.py — Skill 159: wood-quality-assessment

Production-grade unit tests for ``tools/knowledge_updater.py``.

Covers:
    - hash determinism, case/whitespace insensitivity, type robustness
    - composite scoring bounds (max-recent, zero-relevance, in-range)
    - entry markdown formatting (required fields, score display)
    - dedup loading from a real brain file (empty, with entries)
    - configuration schema validation
    - graceful behavior when the brain file is missing

The suite is runnable two ways::

    python -m tools.test_knowledge_updater          # self-contained runner
    pytest tools/test_knowledge_updater.py -v       # pytest-compatible

Each ``test_*`` function is a standalone assertion block so it works under
both runners without depending on pytest fixtures.
"""

from __future__ import annotations

import datetime
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import knowledge_updater as ku  # noqa: E402

__all__ = ["run_all"]

_TESTS_PASSED = 0
_TESTS_FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record a pass/fail and print a one-line result."""
    global _TESTS_PASSED, _TESTS_FAILED
    if condition:
        _TESTS_PASSED += 1
        print(f"[PASS] {name}")
    else:
        _TESTS_FAILED += 1
        print(f"[FAIL] {name} — {detail}")


# --------------------------------------------------------------------------
# Hashing
# --------------------------------------------------------------------------
def test_hash_deterministic() -> None:
    """Identical identifiers yield identical hashes; differing identifiers differ."""
    h1 = ku.compute_hash("https://example.com/doc/123")
    h2 = ku.compute_hash("https://example.com/doc/123")
    h3 = ku.compute_hash("https://example.com/doc/456")
    check("hash_deterministic", h1 == h2 and h1 != h3, f"h1={h1[:8]}, h2={h2[:8]}, h3={h3[:8]}")


def test_hash_case_insensitive() -> None:
    """Case differences do not change the dedup hash."""
    h1 = ku.compute_hash("HTTPS://EXAMPLE.COM/DOC")
    h2 = ku.compute_hash("https://example.com/doc")
    check("hash_case_insensitive", h1 == h2, f"h1={h1[:8]}, h2={h2[:8]}")


def test_hash_whitespace_insensitive() -> None:
    """Surrounding whitespace does not change the dedup hash."""
    h1 = ku.compute_hash("  https://example.com/doc  ")
    h2 = ku.compute_hash("https://example.com/doc")
    check("hash_whitespace_insensitive", h1 == h2, f"h1={h1[:8]}, h2={h2[:8]}")


def test_compute_hash_types() -> None:
    """Hash output is always a 64-char hex digest, including for empty input."""
    h1 = ku.compute_hash("doi:10.1234/test")
    h2 = ku.compute_hash("arxiv:2101.12345")
    h3 = ku.compute_hash("")
    check("hash_doi", len(h1) == 64, f"len={len(h1)}")
    check("hash_arxiv", len(h2) == 64, f"len={len(h2)}")
    check("hash_empty", len(h3) == 64, f"len={len(h3)}")


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
def test_score_max_recent() -> None:
    """A maximally-recent, highly-relevant, highly-cited entry scores near 10."""
    now = datetime.datetime.now()
    entry = {
        "title": ku.KNOWLEDGE_CONFIG["domain"],
        "abstract": " ".join(ku.KNOWLEDGE_CONFIG["keywords"]),
        "published_date": now,
        "citation_count": 10000,
    }
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    check("score_max_recent", 8.0 <= score <= 10.0, f"score={score}")


def test_score_zero() -> None:
    """An irrelevant, old, uncited entry scores near zero."""
    now = datetime.datetime.now()
    entry = {
        "title": "unrelated topic",
        "abstract": "nothing to do with wood",
        "published_date": now - datetime.timedelta(days=2000),
        "citation_count": 0,
    }
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    check("score_zero_irrelevant", 0.0 <= score <= 2.0, f"score={score}")


def test_score_in_range() -> None:
    """A partially-relevant entry scores within [0, 10]."""
    now = datetime.datetime.now()
    entry = {
        "title": "wood anatomy identification",
        "abstract": "CITES timber species density analysis",
        "published_date": now - datetime.timedelta(days=100),
        "citation_count": 5,
    }
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    check("score_in_range", 0.0 <= score <= 10.0, f"score={score}")


def test_score_missing_published_date() -> None:
    """Missing published_date must not raise and recency defaults to 0."""
    now = datetime.datetime.now()
    entry = {
        "title": "wood density species",
        "abstract": "CITES timber",
        "published_date": None,
        "citation_count": 0,
    }
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    check("score_missing_pubdate", 0.0 <= score <= 10.0, f"score={score}")


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------
def test_format_entry_has_required_fields() -> None:
    """Rendered entry contains all required markdown fields."""
    entry = {
        "title": "Test Paper on Wood Anatomy",
        "authors": ["Smith, J.", "Jones, K."],
        "year": 2026,
        "venue": "IAWA Journal",
        "doi_or_url": "https://doi.org/10.1234/test",
        "abstract": "This study examines wood anatomical features in commercial timbers.",
    }
    text = ku.format_entry(entry, 7.5)
    required = ["DOI/URL:", "Relevance Score:", "Authors:", "Year:", "Venue:", "Key Finding:"]
    missing = [f for f in required if f not in text]
    check("format_required_fields", not missing, f"missing: {missing}")


def test_format_entry_score_display() -> None:
    """The score value is rendered into the markdown block."""
    entry = {
        "title": "T",
        "authors": ["A"],
        "year": 2026,
        "venue": "V",
        "doi_or_url": "https://x",
        "abstract": "ab",
    }
    text = ku.format_entry(entry, 5.0)
    check(
        "format_score_display",
        "Relevance Score:" in text and "5.0" in text,
        "score not found in output",
    )


# --------------------------------------------------------------------------
# Dedup loading
# --------------------------------------------------------------------------
def test_load_existing_hashes_empty() -> None:
    """A missing brain file yields an empty hash set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = ku.BRAIN_PATH
        try:
            ku.BRAIN_PATH = Path(tmpdir) / "NONEXISTENT.md"
            hashes = ku.load_existing_hashes()
            check("hashes_empty_on_missing", len(hashes) == 0, f"got {len(hashes)}")
        finally:
            ku.BRAIN_PATH = old_path


def test_load_existing_hashes_with_entries() -> None:
    """Duplicate DOI/URLs in the brain collapse to 2 unique hashes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = ku.BRAIN_PATH
        try:
            brain = Path(tmpdir) / "test_brain.md"
            brain.write_text(
                """
**DOI/URL:** https://doi.org/10.1000/test1
**DOI/URL:** https://doi.org/10.1000/test2
**DOI/URL:** https://doi.org/10.1000/test1
""",
                encoding="utf-8",
            )
            ku.BRAIN_PATH = brain
            hashes = ku.load_existing_hashes()
            check("hashes_count", len(hashes) == 2, f"expected 2 unique, got {len(hashes)}")
        finally:
            ku.BRAIN_PATH = old_path


# --------------------------------------------------------------------------
# Config validation
# --------------------------------------------------------------------------
def test_config_valid() -> None:
    """The KNOWLEDGE_CONFIG schema satisfies the invariants the pipeline relies on."""
    cfg = ku.KNOWLEDGE_CONFIG
    check("config_domain_not_empty", len(cfg["domain"]) > 0)
    check("config_keywords_count", len(cfg["keywords"]) >= 4, str(len(cfg["keywords"])))
    check(
        "config_scoring_weights",
        abs(sum(cfg["scoring_weights"].values()) - 1.0) < 0.001,
        str(cfg["scoring_weights"]),
    )
    check(
        "config_max_entries",
        cfg["max_new_entries_per_run"] > 0,
        str(cfg["max_new_entries_per_run"]),
    )


# --------------------------------------------------------------------------
# Append robustness
# --------------------------------------------------------------------------
def test_append_to_brain_missing() -> None:
    """append_to_brain returns 0 (not an exception) when the brain is missing."""
    old_path = ku.BRAIN_PATH
    try:
        ku.BRAIN_PATH = Path("/nonexistent/path/to/brain.md")
        result = ku.append_to_brain([], dry_run=True)
        check("append_missing_brain", result == 0, f"got {result}")
    finally:
        ku.BRAIN_PATH = old_path


def test_append_to_brain_dedups(tmp_brain=None) -> None:
    """Entries already present in the brain are not appended again."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = ku.BRAIN_PATH
        try:
            brain = Path(tmpdir) / "dedup_brain.md"
            brain.write_text("**DOI/URL:** https://doi.org/10.1000/already\n", encoding="utf-8")
            ku.BRAIN_PATH = brain
            entries = [
                {
                    "title": "Already in brain",
                    "doi_or_url": "https://doi.org/10.1000/already",
                    "authors": ["X"],
                    "year": 2026,
                    "venue": "V",
                    "abstract": "a",
                },
                {
                    "title": "Brand new",
                    "doi_or_url": "https://doi.org/10.1000/new",
                    "authors": ["Y"],
                    "year": 2026,
                    "venue": "W",
                    "abstract": "b",
                    "published_date": datetime.datetime.now(),
                    "citation_count": 0,
                },
            ]
            n = ku.append_to_brain(entries, dry_run=True)
            check("append_dedups_existing", n == 1, f"expected 1 new, got {n}")
        finally:
            ku.BRAIN_PATH = old_path


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------
def run_all() -> bool:
    """Run every test_* function and return True iff all passed."""
    global _TESTS_PASSED, _TESTS_FAILED
    _TESTS_PASSED = 0
    _TESTS_FAILED = 0

    tests = [
        test_hash_deterministic,
        test_hash_case_insensitive,
        test_hash_whitespace_insensitive,
        test_compute_hash_types,
        test_score_max_recent,
        test_score_zero,
        test_score_in_range,
        test_score_missing_published_date,
        test_format_entry_has_required_fields,
        test_format_entry_score_display,
        test_load_existing_hashes_empty,
        test_load_existing_hashes_with_entries,
        test_config_valid,
        test_append_to_brain_missing,
        test_append_to_brain_dedups,
    ]
    for t in tests:
        t()

    total = _TESTS_PASSED + _TESTS_FAILED
    print(f"\n{'=' * 50}")
    print(f"Results: {_TESTS_PASSED}/{total} passed, {_TESTS_FAILED} failed")
    print(f"{'=' * 50}")
    return _TESTS_FAILED == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
