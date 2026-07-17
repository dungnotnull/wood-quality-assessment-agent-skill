"""Wood Quality Assessment - Reference Data Layer.

Loads the curated grounding datasets (``references/species_database.json``,
``references/cites_listings.json``, ``references/iucn_status.json``) generated
by ``scripts/seed_reference_data.py`` and exposes type-safe, fuzzy-tolerant
lookup helpers used by the evidence-collector, physical-property and
authenticity-compliance sub-skills and by the offline tools registry.

The module is deliberately dependency-light (stdlib only) and fully
offline-safe: it never touches the network. All lookups are cached and
thread-safe.

Public API
----------
ReferenceData ........... singleton loader / query facade
normalize_species_name .. canonicalize a free-form species string
resolve_species ......... best-effort species resolution with fuzzy matching
get_species ............. exact scientific-name lookup
get_cites ............... CITES appendix lookup (genus-aware)
get_iucn ................ IUCN category lookup
compare_density ......... measured vs benchmark density comparison
classify_moisture ....... moisture-content state classification
substitution_risk ....... claimed-vs-candidate substitution risk scoring
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = ROOT / "references"

logger = logging.getLogger("wqa.reference_data")

# IUCN category severity ordering (LC -> CR/EX).
_IUCN_SEVERITY = {"LC": 0, "NT": 1, "VU": 2, "EN": 3, "CR": 4, "EW": 5, "EX": 6, "DD": -1}


def _levenshtein(a: str, b: str) -> int:
    """Standard iterative Levenshtein edit distance."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur[j] = min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[-1]


def normalize_species_name(name: str) -> str:
    """Canonicalize a free-form species string.

    Lower-cases the genus, collapses internal whitespace, strips authority
    text in parentheses, and normalizes common synonyms ("spp", "sp.") to
    "spp.". Returns an empty string for falsy input.
    """
    if not name or not name.strip():
        return ""
    cleaned = name.strip()
    # Drop parenthetical authorities / annotations: "Dalbergia latifolia Roxb." -> genus+epithet
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Normalize "sp."/"spp"/"spp." tokens.
    cleaned = re.sub(r"\b(spp|sp)\b\.?", "spp.", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\.{2,}", ".", cleaned)  # collapse accidental double dots
    parts = cleaned.split(" ")
    if not parts:
        return ""
    parts[0] = parts[0].capitalize()
    return " ".join(p for p in parts if p).strip()


@dataclass(frozen=True)
class DensityComparison:
    """Result of comparing a measured density against a species benchmark."""

    measured: float | None
    benchmark_typical: float
    benchmark_min: float
    benchmark_max: float
    deviation_percent: float | None
    within_range: bool
    assessment: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "measured": self.measured,
            "benchmark_typical": self.benchmark_typical,
            "benchmark_min": self.benchmark_min,
            "benchmark_max": self.benchmark_max,
            "deviation_percent": self.deviation_percent,
            "within_range": self.within_range,
            "assessment": self.assessment,
        }


@dataclass(frozen=True)
class MoistureClassification:
    """Result of classifying a moisture reading against species benchmarks."""

    moisture_pct: float
    condition: str
    kd_target: float
    adequacy: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "moisture_pct": self.moisture_pct,
            "condition": self.condition,
            "kd_target": self.kd_target,
            "adequacy": self.adequacy,
            "notes": self.notes,
        }


@dataclass
class SubstitutionRiskResult:
    """Claimed-vs-candidate substitution risk verdict."""

    risk_level: str  # none | low | medium | high
    species_match: bool
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "species_match": self.species_match,
            "reasons": self.reasons,
        }


class ReferenceData:
    """Singleton-style facade over the three reference JSON datasets.

    Loads lazily on first access and is safe to instantiate multiple times;
    the underlying datasets are cached at the class level behind a re-entrant
    lock so concurrent callers share the parsed payloads.
    """

    _lock = RLock()
    _species: dict[str, dict[str, Any]] = {}
    _cites: list[dict[str, Any]] = []
    _iucn: list[dict[str, Any]] = []
    _loaded: bool = False

    # Fuzzy-match acceptance threshold (edit distance over the binomial name).
    FUZZY_THRESHOLD: int = 2

    def __init__(self, references_dir: Path | None = None) -> None:
        self._dir = references_dir or REFERENCES_DIR
        self._ensure_loaded()

    # -- loading -----------------------------------------------------------
    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._loaded:
            return
        with cls._lock:
            if cls._loaded:
                return
            cls._load(REFERENCES_DIR)
            cls._loaded = True

    @classmethod
    def reload(cls, references_dir: Path | None = None) -> None:
        """Force a reload from disk (e.g. after the seed script runs)."""
        with cls._lock:
            cls._load(references_dir or REFERENCES_DIR)
            cls._loaded = True

    @staticmethod
    def _load(d: Path) -> None:
        sp_path = d / "species_database.json"
        cites_path = d / "cites_listings.json"
        iucn_path = d / "iucn_status.json"
        if not sp_path.exists():
            logger.warning("species database not found at %s", sp_path)
            ReferenceData._species = {}
            ReferenceData._cites = []
            ReferenceData._iucn = []
            return
        ReferenceData._species = json.loads(sp_path.read_text(encoding="utf-8"))
        ReferenceData._cites = (
            json.loads(cites_path.read_text(encoding="utf-8")) if cites_path.exists() else []
        )
        ReferenceData._iucn = (
            json.loads(iucn_path.read_text(encoding="utf-8")) if iucn_path.exists() else []
        )
        logger.info(
            "Loaded reference data: %d species, %d CITES listings, %d IUCN assessments",
            len(ReferenceData._species),
            len(ReferenceData._cites),
            len(ReferenceData._iucn),
        )

    # -- species -----------------------------------------------------------
    def list_species(self) -> list[str]:
        """Return all registered scientific names (sorted)."""
        return sorted(self._species.keys())

    def get_species(self, scientific_name: str) -> dict[str, Any] | None:
        """Exact scientific-name lookup (after normalization)."""
        key = normalize_species_name(scientific_name)
        if not key:
            return None
        if key in self._species:
            return self._species[key]
        # try a case-insensitive exact match as a fallback
        for k, v in self._species.items():
            if k.lower() == key.lower():
                return v
        return None

    def _candidate_keys(self) -> list[str]:
        return list(self._species.keys())

    def _common_name_index(self) -> dict[str, str]:
        index: dict[str, str] = {}
        for sci, entry in self._species.items():
            names = entry.get("common_names", {})
            for lang_names in names.values():
                for nm in lang_names:
                    index.setdefault(nm.lower(), sci)
        return index

    def resolve_species(self, query: str) -> tuple[str, dict[str, Any], int] | None:
        """Best-effort species resolution.

        Tries (in order): exact scientific name, exact common name, then
        fuzzy Levenshtein matching over scientific names (threshold
        ``FUZZY_THRESHOLD``). Returns ``(scientific_name, entry, distance)``
        on success or ``None``.
        """
        if not query or not query.strip():
            return None
        norm = normalize_species_name(query)
        entry = self.get_species(norm)
        if entry:
            # find the canonical key matching norm case-insensitively
            for k in self._species:
                if k.lower() == norm.lower():
                    return k, entry, 0
        # common-name exact match
        cidx = self._common_name_index()
        q_low = query.strip().lower()
        if q_low in cidx:
            sci = cidx[q_low]
            return sci, self._species[sci], 0
        # fuzzy over scientific names
        best: tuple[str, int] | None = None
        for k in self._candidate_keys():
            # compare on the joined binomial to keep distance meaningful
            dist = _levenshtein(norm.lower(), k.lower())
            if best is None or dist < best[1]:
                best = (k, dist)
                if dist == 0:
                    break
        if best and best[1] <= self.FUZZY_THRESHOLD:
            k, dist = best
            return k, self._species[k], dist
        return None

    # -- CITES -------------------------------------------------------------
    def get_cites(self, scientific_name: str) -> dict[str, Any] | None:
        """CITES appendix lookup, genus-aware.

        Resolves an exact match first, then a ``"<Genus> spp."`` listing,
        then a listing whose ``scientific_name`` shares the same genus.
        """
        norm = normalize_species_name(scientific_name)
        if not norm:
            return None
        # exact
        for entry in self._cites:
            if entry["scientific_name"].lower() == norm.lower():
                return entry
        genus = norm.split(" ")[0]
        spp_key = f"{genus} spp."
        for entry in self._cites:
            if entry["scientific_name"].lower() == spp_key.lower():
                return entry
        for entry in self._cites:
            if entry["scientific_name"].lower().startswith(genus.lower() + " "):
                return entry
        return None

    # -- IUCN --------------------------------------------------------------
    def get_iucn(self, scientific_name: str) -> dict[str, Any] | None:
        """IUCN assessment lookup, genus-aware (prefers exact, then genus)."""
        norm = normalize_species_name(scientific_name)
        if not norm:
            return None
        for entry in self._iucn:
            if entry["scientific_name"].lower() == norm.lower():
                return entry
        genus = norm.split(" ")[0]
        # Prefer the most severe assessment within the same genus as a signal.
        genus_entries = [
            e for e in self._iucn if e["scientific_name"].lower().startswith(genus.lower() + " ")
        ]
        if genus_entries:
            genus_entries.sort(key=lambda e: _IUCN_SEVERITY.get(e["category"], -1), reverse=True)
            return genus_entries[0]
        return None

    # -- analytical helpers ----------------------------------------------
    def compare_density(
        self, measured: float | None, species_entry: dict[str, Any]
    ) -> DensityComparison:
        """Compare a measured air-dry density (kg/m^3) against the species benchmark."""
        bench = species_entry.get("density_kgm3", {})
        typical = float(bench.get("typical", 0))
        bmin = float(bench.get("min", 0))
        bmax = float(bench.get("max", 0))
        if measured is None:
            return DensityComparison(
                measured=None,
                benchmark_typical=typical,
                benchmark_min=bmin,
                benchmark_max=bmax,
                deviation_percent=None,
                within_range=False,
                assessment="No density provided; benchmark comparison skipped (LIMITATION).",
            )
        if typical <= 0:
            return DensityComparison(
                measured=float(measured),
                benchmark_typical=typical,
                benchmark_min=bmin,
                benchmark_max=bmax,
                deviation_percent=None,
                within_range=False,
                assessment="Benchmark unavailable for this species.",
            )
        deviation = ((measured - typical) / typical) * 100.0
        within = bool(bmin <= measured <= bmax) if (bmin and bmax) else False
        if within:
            assessment = "Within expected species density range."
        elif measured < bmin:
            assessment = (
                f"Below species minimum ({bmin} kg/m^3); "
                f"possible lower-density substitute or misidentification."
            )
        else:
            assessment = (
                f"Above species maximum ({bmax} kg/m^3); "
                f"possible denser substitute or measurement basis mismatch."
            )
        return DensityComparison(
            measured=float(measured),
            benchmark_typical=typical,
            benchmark_min=bmin,
            benchmark_max=bmax,
            deviation_percent=round(deviation, 1),
            within_range=within,
            assessment=assessment,
        )

    def classify_moisture(
        self, moisture_pct: float | None, species_entry: dict[str, Any]
    ) -> MoistureClassification:
        """Classify a moisture reading into a drying-state category and assess adequacy."""
        mb = species_entry.get("moisture_benchmarks", {})
        kd_target = float(mb.get("kd_target", 12))
        if moisture_pct is None:
            return MoistureClassification(
                moisture_pct=float("nan"),
                condition="unknown",
                kd_target=kd_target,
                adequacy="Not assessable (no moisture reading).",
                notes="G2 LIMITATION.",
            )
        mc = float(moisture_pct)
        green_max = float(mb.get("green_max", 75))
        fad = float(mb.get("fad_typical", 30))
        if mc >= green_max:
            condition, adequacy = "green", "Not dried; unsuitable for finished solid-wood use."
        elif mc > fad:
            condition = "above_fad"
            adequacy = "Partially air-dried; above FAD target - re-dry required for indoor use."
        elif mc > kd_target + 2:
            condition = "fad"
            adequacy = (
                "Air-dry range; acceptable for outdoor/seasoned use, re-dry for interior furniture."
            )
        elif mc >= kd_target - 2:
            condition = "kd"
            adequacy = "Kiln-dry range; adequate for interior furniture and joinery."
        else:
            condition = "overdried"
            adequacy = "Below KD target; monitor for re-adsorption and machining brittleness."
        notes = f"Species KD target: {kd_target}%"
        return MoistureClassification(
            moisture_pct=mc,
            condition=condition,
            kd_target=kd_target,
            adequacy=adequacy,
            notes=notes,
        )

    def substitution_risk(self, claimed: str, candidate: str) -> SubstitutionRiskResult:
        """Score substitution risk between claimed and candidate species.

        Considers exact match, genus match, known substitution lists, and
        whether the candidate appears in the claimed species' documented
        substitution-risk list.
        """
        cn = normalize_species_name(claimed) or claimed.strip()
        an = normalize_species_name(candidate) or candidate.strip()
        if not cn or not an:
            return SubstitutionRiskResult(
                risk_level="low", species_match=False, reasons=["One or both species unspecified."]
            )
        if cn.lower() == an.lower():
            return SubstitutionRiskResult(
                risk_level="none",
                species_match=True,
                reasons=["Claimed and candidate species match exactly."],
            )
        claimed_entry = self.get_species(cn)
        candidate_entry = self.get_species(an)
        reasons: list[str] = []
        cgenus = cn.split(" ")[0].lower()
        agenus = an.split(" ")[0].lower()
        if claimed_entry:
            # Detect documented substitutes by matching the candidate's binomial
            # (or genus for spp.-level entries) against the leading Latin name
            # of each documented substitution-risk entry.
            binom_re = re.compile(r"[A-Z][a-z]+(?:\s+(?:spp\.|[a-z-]+))?")
            cand_binomial = an
            cand_genus = agenus
            documented = False
            for risk in claimed_entry.get("common_substitution_risks", []):
                m = binom_re.search(risk)
                if not m:
                    continue
                rb = m.group(0).lower()
                parts = rb.split(" ")
                if len(parts) >= 2:
                    if rb == cand_binomial.lower():
                        documented = True
                        break
                else:
                    # genus-level risk entry ("other Dalbergia spp.", "treated Catalpa")
                    if parts[0] == cand_genus:
                        documented = True
                        break
            if documented:
                reasons.append(f"Candidate '{an}' is a documented substitute for '{cn}'.")
                return SubstitutionRiskResult(
                    risk_level="high", species_match=False, reasons=reasons
                )
        if cgenus == agenus:
            reasons.append(
                f"Same genus ({cgenus.title()}) but different species - "
                f"cross-species substitution possible."
            )
            level = "medium"
        else:
            reasons.append(
                f"Different genus: claimed {cgenus.title()} vs candidate {agenus.title()}."
            )
            # heavier woods / protected groups often substituted with look-alikes
            level = "medium"
            if claimed_entry and candidate_entry:
                cd = claimed_entry.get("density_kgm3", {}).get("typical", 0)
                ad = candidate_entry.get("density_kgm3", {}).get("typical", 0)
                if cd and ad and abs(cd - ad) / max(cd, 1) > 0.25:
                    reasons.append(f"Material density gap (claimed {cd} vs candidate {ad} kg/m^3).")
                    level = "high"
        return SubstitutionRiskResult(risk_level=level, species_match=False, reasons=reasons)


# Module-level convenience facade -----------------------------------------
_default: ReferenceData | None = None


def _facade() -> ReferenceData:
    global _default
    if _default is None:
        _default = ReferenceData()
    return _default


def list_species() -> list[str]:
    return _facade().list_species()


def get_species(name: str) -> dict[str, Any] | None:
    return _facade().get_species(name)


def resolve_species(query: str) -> tuple[str, dict[str, Any], int] | None:
    return _facade().resolve_species(query)


def get_cites(name: str) -> dict[str, Any] | None:
    return _facade().get_cites(name)


def get_iucn(name: str) -> dict[str, Any] | None:
    return _facade().get_iucn(name)


def compare_density(measured: float | None, species_entry: dict[str, Any]) -> DensityComparison:
    return _facade().compare_density(measured, species_entry)


def classify_moisture(
    moisture_pct: float | None, species_entry: dict[str, Any]
) -> MoistureClassification:
    return _facade().classify_moisture(moisture_pct, species_entry)


def substitution_risk(claimed: str, candidate: str) -> SubstitutionRiskResult:
    return _facade().substitution_risk(claimed, candidate)


# CLI --------------------------------------------------------------------
def _cli() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="wood-quality-assessment reference data lookup")
    ap.add_argument("query", nargs="?", help="species name to resolve")
    ap.add_argument("--cites", action="store_true", help="show CITES status")
    ap.add_argument("--iucn", action="store_true", help="show IUCN status")
    ap.add_argument(
        "--density",
        type=float,
        help="compare a measured density (kg/m^3) to the resolved species benchmark",
    )
    ap.add_argument(
        "--moisture",
        type=float,
        help="classify a moisture reading (%%) against the resolved species benchmark",
    )
    ap.add_argument("--list", action="store_true", help="list all registered species and exit")
    args = ap.parse_args()
    rd = ReferenceData()
    if args.list:
        for s in rd.list_species():
            print(s)
        return 0
    if not args.query:
        ap.print_help()
        return 0
    res = rd.resolve_species(args.query)
    if not res:
        print(
            f"No species matched '{args.query}' (fuzzy threshold={ReferenceData.FUZZY_THRESHOLD})."
        )
        return 1
    sci, entry, dist = res
    print(f"Resolved: {sci}  (edit distance {dist})")
    print(f"  Family: {entry.get('family')}; {entry.get('wood_type')}; {entry.get('porosity')}")
    print(f"  Density: {entry.get('density_kgm3')} kg/m^3")
    print(f"  Heartwood: {entry.get('heartwood_color')}")
    if args.cites:
        c = rd.get_cites(sci)
        print(
            f"  CITES: {c['appendix'] if c else 'Not listed'}"
            + (f" - {c['annotation']}" if c else "")
        )
    if args.iucn:
        iu = rd.get_iucn(sci)
        print(f"  IUCN: {iu['category']} ({iu['category_full']})" if iu else "  IUCN: not assessed")
    if args.density is not None:
        dc = rd.compare_density(args.density, entry)
        print(f"  Density comparison: {dc.to_dict()}")
    if args.moisture is not None:
        mc = rd.classify_moisture(args.moisture, entry)
        print(f"  Moisture classification: {mc.to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
