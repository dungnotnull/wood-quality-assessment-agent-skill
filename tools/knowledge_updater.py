"""knowledge_updater.py — Skill 159: wood-quality-assessment

Production-grade crawl pipeline for the SECOND-KNOWLEDGE-BRAIN knowledge base.

Fetches the latest academic papers (Semantic Scholar, ArXiv when configured)
and authoritative news feeds (CITES, ITTO), scores each candidate against a
recency/relevance/citation composite, deduplicates by SHA-256 of the
DOI/URL, and appends vetted entries to ``SECOND-KNOWLEDGE-BRAIN.md``.

The module is designed for resilient, unattended scheduled execution (cron /
CI) and degrades gracefully when optional dependencies are unavailable or
network sources are unreachable — it never raises on a single source failure.

Dependencies:
    pip install requests feedparser python-dateutil

Usage:
    python -m tools.knowledge_updater [--dry-run] [--news-only] [--keywords ...]

Exit codes:
    0  — run completed (entries may or may not have been appended)
    2  — fatal configuration / filesystem error before crawling
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import math
import re
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:  # requests is optional at import time so the module can be unit-tested
    import requests
except ImportError:  # pragma: no cover - exercised when requests not installed
    requests = None  # type: ignore[assignment]

try:
    import feedparser
except ImportError:  # pragma: no cover
    feedparser = None  # type: ignore[assignment]

__all__ = [
    "KNOWLEDGE_CONFIG",
    "BRAIN_PATH",
    "KnowledgeEntry",
    "compute_hash",
    "score_entry",
    "format_entry",
    "load_existing_hashes",
    "append_to_brain",
    "main",
]

# --------------------------------------------------------------------------
# Logging — structured, stderr-bound, configurable via env LOG_LEVEL.
# --------------------------------------------------------------------------
_LOG = logging.getLogger("wood_quality_assessment.updater")
if not _LOG.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    _LOG.addHandler(_handler)
    _LOG.setLevel(logging.INFO)


# --------------------------------------------------------------------------
# Project configuration — per-project crawl targets and scoring weights.
# --------------------------------------------------------------------------
KNOWLEDGE_CONFIG: dict[str, Any] = {
    "domain": "Wood Quality & Forestry-Standards Compliance",
    "keywords": [
        "wood anatomy identification",
        "wood density species",
        "CITES timber",
        "wood moisture content kiln drying",
        "solid wood handicraft quality",
        "timber legality due diligence",
    ],
    "arxiv_categories": [],
    "arxiv_base": "https://export.arxiv.org/api/query",
    "semantic_scholar_base": "https://api.semanticscholar.org/graph/v1/paper/search",
    "rss_feeds": [
        "https://www.cites.org/eng/news/rss",
        "https://www.itto.int/rss/",
    ],
    "authoritative_docs": [
        "IAWA Journal — wood anatomy & identification (Oxford)",
        "Wood Science and Technology — Springer",
        "Holzforschung — De Gruyter (wood chemistry & physics)",
        "European Journal of Wood and Wood Products — Springer",
        "Semantic Scholar — 'wood anatomy identification', 'wood density species'",
        "InsideWood anatomy database — coded reference atlas",
    ],
    "scoring_weights": {
        "recency": 0.4,
        "keyword_relevance": 0.4,
        "citation_count": 0.2,
    },
    "max_results_per_source": 10,
    "max_new_entries_per_run": 20,
}

BRAIN_PATH: Path = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

# Regex used to locate previously-appended DOI/URL identifiers in the brain.
_DOI_URL_RE = re.compile(r"\*\*DOI/URL:\*\*\s*(\S+)")


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------
@dataclass
class KnowledgeEntry:
    """Normalized representation of a crawled paper or news item."""

    title: str
    authors: list[str] = field(default_factory=list)
    year: int = field(default_factory=lambda: datetime.now().year)
    venue: str = "Unknown"
    doi_or_url: str = ""
    abstract: str = ""
    published_date: datetime | None = None
    citation_count: int = 0
    source: str = "unknown"
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "doi_or_url": self.doi_or_url,
            "abstract": self.abstract,
            "published_date": self.published_date,
            "citation_count": self.citation_count,
            "source": self.source,
        }


# --------------------------------------------------------------------------
# Network layer
# --------------------------------------------------------------------------
def fetch_with_retry(
    url: str,
    params: dict[str, Any] | None = None,
    max_retries: int = 3,
    base_delay: float = 2.0,
    timeout: float = 30.0,
) -> Any:
    """GET *url* with exponential backoff.

    Returns the ``requests.Response`` on success or ``None`` after exhausting
    retries. Safe to call when ``requests`` is not installed (returns ``None``).
    """
    if requests is None:
        _LOG.warning("requests not installed — skipping fetch of %s", url)
        return None
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                time.sleep(base_delay * (2 ** (attempt - 1)))
            resp = requests.get(url, params=params or {}, timeout=timeout)
            if resp.status_code == 429:
                _LOG.warning("429 Too Many Requests on attempt %d for %s", attempt, url)
                if attempt < max_retries:
                    continue
                return None
            if resp.status_code >= 500:
                _LOG.warning("server error %d on attempt %d for %s", resp.status_code, attempt, url)
                if attempt < max_retries:
                    continue
                return None
            resp.raise_for_status()
            return resp
        except Exception as ex:  # noqa: BLE001 - surface to log, continue retrying
            _LOG.warning("request failed attempt %d for %s: %s", attempt, url, ex)
            if attempt < max_retries:
                time.sleep(base_delay)
            else:
                return None
    return None


# --------------------------------------------------------------------------
# Hashing & deduplication
# --------------------------------------------------------------------------
def compute_hash(identifier: str) -> str:
    """SHA-256 of the lowercased, stripped identifier.

    The normalization makes the hash deterministic across case/whitespace
    variants so ``HTTPS://Example.COM/Doc`` and ``https://example.com/doc``
    resolve to the same dedup key.
    """
    return hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()


def load_existing_hashes(brain_path: Path | None = None) -> set[str]:
    """Return the set of SHA-256 hashes for DOI/URLs already in the brain.

    Reads the file once and returns an empty set if the file is missing.
    Accepts an optional *brain_path* (used by the unit tests to isolate state).
    """
    path = brain_path if brain_path is not None else BRAIN_PATH
    if not path.exists():
        return set()
    hashes: set[str] = set()
    for m in _DOI_URL_RE.finditer(path.read_text(encoding="utf-8")):
        hashes.add(compute_hash(m.group(1)))
    return hashes


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
def score_entry(entry: dict[str, Any], keywords: list[str], now: datetime) -> float:
    """Composite score in [0, 10] from recency, relevance, and citations.

    Weights come from ``KNOWLEDGE_CONFIG["scoring_weights"]``. Missing fields
    degrade gracefully to zero rather than raising.
    """
    w = KNOWLEDGE_CONFIG["scoring_weights"]

    pub = entry.get("published_date")
    recency = 0.0
    if pub is not None:
        try:
            age_days = (now - pub).days
            recency = max(0.0, 1.0 - age_days / 730.0)
        except Exception:  # noqa: BLE001 - bad date should not abort scoring
            recency = 0.0

    text = f"{entry.get('title') or ''} {entry.get('abstract') or ''}".lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    relevance = min(hits / max(len(keywords), 1), 1.0)

    cit = entry.get("citation_count", 0) or 0
    cit_score = min(math.log1p(cit) / math.log1p(1000), 1.0)

    return round(
        (
            recency * w["recency"]
            + relevance * w["keyword_relevance"]
            + cit_score * w["citation_count"]
        )
        * 10.0,
        2,
    )


# --------------------------------------------------------------------------
# Source fetchers — each returns a list of entry dicts (never raises)
# --------------------------------------------------------------------------
def fetch_arxiv(keywords: list[str]) -> list[dict[str, Any]]:
    """Fetch ArXiv results. Returns [] if requests is unavailable or no
    categories are configured (ArXiv has no wood-science category, so this
    is typically a no-op kept for completeness)."""
    if requests is None or not KNOWLEDGE_CONFIG["arxiv_categories"]:
        return []
    cats = KNOWLEDGE_CONFIG["arxiv_categories"]
    query = (
        "("
        + " OR ".join("cat:" + c for c in cats)
        + ") AND ("
        + " OR ".join('"' + k + '"' for k in keywords[:5])
        + ")"
    )
    resp = fetch_with_retry(
        KNOWLEDGE_CONFIG["arxiv_base"],
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": KNOWLEDGE_CONFIG["max_results_per_source"],
        },
    )
    if resp is None:
        return []
    import xml.etree.ElementTree as ET

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(resp.content)
    except Exception as ex:  # noqa: BLE001
        _LOG.warning("ArXiv XML parse failed: %s", ex)
        return []
    out: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        t = entry.find("atom:title", ns)
        s = entry.find("atom:summary", ns)
        i = entry.find("atom:id", ns)
        p = entry.find("atom:published", ns)
        title = (t.text or "").strip().replace("\n", " ") if t is not None else ""
        url = (i.text or "").strip() if i is not None else ""
        if not title or not url:
            continue
        pub: datetime | None = None
        if p is not None:
            try:
                from dateutil import parser as dp

                pub = dp.parse(p.text).replace(tzinfo=None)
            except Exception:  # noqa: BLE001
                pass
        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ][:3]
        out.append(
            {
                "title": title,
                "authors": authors,
                "year": pub.year if pub else datetime.now().year,
                "venue": "ArXiv",
                "doi_or_url": url,
                "abstract": (s.text or "")[:300] if s is not None else "",
                "published_date": pub,
                "citation_count": 0,
                "source": "arxiv",
            }
        )
    _LOG.info("ArXiv: %d entries", len(out))
    return out


def fetch_semantic_scholar(keywords: list[str]) -> list[dict[str, Any]]:
    """Fetch Semantic Scholar paper-search results."""
    if requests is None:
        return []
    resp = fetch_with_retry(
        KNOWLEDGE_CONFIG["semantic_scholar_base"],
        {
            "query": " ".join(keywords[:4]),
            "fields": "title,authors,year,venue,externalIds,abstract,citationCount",
            "limit": KNOWLEDGE_CONFIG["max_results_per_source"],
        },
    )
    if resp is None:
        return []
    try:
        data = resp.json()
    except Exception as ex:  # noqa: BLE001
        _LOG.warning("Semantic Scholar JSON parse failed: %s", ex)
        return []
    out: list[dict[str, Any]] = []
    for p in data.get("data", []):
        title = p.get("title", "")
        if not title:
            continue
        year = p.get("year") or datetime.now().year
        ext = p.get("externalIds", {}) or {}
        doi = ext.get("DOI") or (
            f"https://arxiv.org/abs/{ext['ArXiv']}" if ext.get("ArXiv") else ""
        )
        if not doi:
            doi = "https://www.semanticscholar.org/paper/" + str(p.get("paperId", ""))
        out.append(
            {
                "title": title,
                "authors": [a.get("name", "") for a in (p.get("authors") or [])[:3]],
                "year": year,
                "venue": p.get("venue") or "Unknown",
                "doi_or_url": doi,
                "abstract": (p.get("abstract") or "")[:300],
                "published_date": datetime(year, 1, 1),
                "citation_count": p.get("citationCount", 0) or 0,
                "source": "semantic_scholar",
            }
        )
    _LOG.info("Semantic Scholar: %d entries", len(out))
    return out


def fetch_rss() -> list[dict[str, Any]]:
    """Fetch news items from configured RSS feeds."""
    if feedparser is None or not KNOWLEDGE_CONFIG["rss_feeds"]:
        return []
    out: list[dict[str, Any]] = []
    for url in KNOWLEDGE_CONFIG["rss_feeds"]:
        try:
            feed = feedparser.parse(url)
        except Exception as ex:  # noqa: BLE001
            _LOG.warning("RSS %s failed: %s", url, ex)
            continue
        for item in feed.entries[:10]:
            title = item.get("title", "")
            link = item.get("link", "")
            if not title or not link:
                continue
            pp = item.get("published_parsed")
            pub = datetime(*pp[:6]) if pp else datetime.now()
            out.append(
                {
                    "title": title,
                    "authors": ["Editorial"],
                    "year": pub.year,
                    "venue": "RSS",
                    "doi_or_url": link,
                    "abstract": (item.get("summary", ""))[:200],
                    "published_date": pub,
                    "citation_count": 0,
                    "source": "rss",
                }
            )
    _LOG.info("RSS: %d entries", len(out))
    return out


# --------------------------------------------------------------------------
# Formatting & append
# --------------------------------------------------------------------------
def format_entry(entry: dict[str, Any], score: float) -> str:
    """Render an entry as the markdown block appended to the brain."""
    d = datetime.now().strftime("%Y-%m-%d")
    authors = ", ".join(entry.get("authors") or []) or "Unknown"
    return (
        "\n### " + d + " — " + entry.get("title", "Untitled") + "\n"
        "- **Authors:** " + authors + "\n"
        "- **Year:** " + str(entry.get("year", "")) + "\n"
        "- **Venue:** " + entry.get("venue", "Unknown") + "\n"
        "- **DOI/URL:** " + entry.get("doi_or_url", "") + "\n"
        "- **Relevance Score:** " + str(score) + "/10\n"
        "- **Key Finding:** " + entry.get("abstract", "No abstract available.") + "\n"
    )


def append_to_brain(
    entries: Iterable[dict[str, Any]],
    dry_run: bool = False,
    brain_path: Path | None = None,
) -> int:
    """Dedup, score, and append *entries* to the knowledge brain.

    Returns the number of newly appended entries. In dry-run mode the brain
    file is not modified. Raises ``FileNotFoundError``-equivalent behavior is
    avoided: if the brain is missing the function returns 0.
    """
    path = brain_path if brain_path is not None else BRAIN_PATH
    if not path.exists():
        _LOG.error("brain not found: %s", path)
        return 0

    existing = load_existing_hashes(path)
    now = datetime.now(UTC).replace(tzinfo=None)
    new: list[dict[str, Any]] = []
    for e in entries:
        doi = e.get("doi_or_url", "")
        if not doi:
            continue
        h = compute_hash(doi)
        if h in existing:
            continue
        existing.add(h)
        new.append(e)

    if not new:
        _LOG.info("no new entries")
        return 0

    for e in new:
        e["_score"] = score_entry(e, KNOWLEDGE_CONFIG["keywords"], now)
    new.sort(key=lambda x: x["_score"], reverse=True)
    new = new[: KNOWLEDGE_CONFIG["max_new_entries_per_run"]]

    text = "".join(format_entry(e, e["_score"]) for e in new)
    if dry_run:
        _LOG.info("[DRY] would append %d entries", len(new))
        return len(new)

    content = path.read_text(encoding="utf-8")
    if "## 7. Knowledge Update Log" in content:
        content += text
    else:
        content += "\n## 7. Knowledge Update Log\n" + text
    path.write_text(content, encoding="utf-8")
    _LOG.info("appended %d entries", len(new))
    return len(new)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns process exit code."""
    ap = argparse.ArgumentParser(
        prog="knowledge_updater",
        description="Crawl and append vetted entries to SECOND-KNOWLEDGE-BRAIN.md.",
    )
    ap.add_argument("--dry-run", action="store_true", help="score and print counts without writing")
    ap.add_argument(
        "--news-only", action="store_true", help="skip academic sources, fetch RSS only"
    )
    ap.add_argument(
        "--keywords",
        nargs="+",
        default=KNOWLEDGE_CONFIG["keywords"],
        help="override the default keyword set",
    )
    ap.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="logging verbosity",
    )
    args = ap.parse_args(argv)
    _LOG.setLevel(getattr(logging, args.log_level))

    _LOG.info(
        "start %s dry=%s news=%s",
        datetime.now().isoformat(),
        args.dry_run,
        args.news_only,
    )

    all_entries: list[dict[str, Any]] = []
    if not args.news_only:
        all_entries += fetch_arxiv(args.keywords)
        time.sleep(1)
        all_entries += fetch_semantic_scholar(args.keywords)
        time.sleep(1)
    all_entries += fetch_rss()
    _LOG.info("candidates: %d", len(all_entries))

    n = append_to_brain(all_entries, args.dry_run)
    _LOG.info("done — appended %d", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
