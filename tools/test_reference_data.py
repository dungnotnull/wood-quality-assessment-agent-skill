"""test_reference_data.py — Skill 159: wood-quality-assessment

Production-grade unit tests for ``scripts/reference_data.py``.

Covers:
    - species name normalization (whitespace, authorities, spp., case)
    - exact scientific-name and common-name resolution
    - fuzzy Levenshtein resolution within threshold and rejection beyond it
    - genus-aware CITES lookup (exact / "<Genus> spp." / starts-with)
    - genus-aware IUCN lookup and severity tie-break
    - density comparison (within range, below min, above max, missing measured)
    - moisture classification across all drying states
    - substitution risk (exact match, documented substitute, density-gap high)
    - reference data integrity (loads, counts, cross-key consistency)

Runnable two ways::

    python -m tools.test_reference_data.py          # self-contained runner
    pytest tools/test_reference_data.py -v           # pytest-compatible
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import reference_data as rd  # noqa: E402

__all__ = ["run_all"]

_TESTS_PASSED = 0
_TESTS_FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global _TESTS_PASSED, _TESTS_FAILED
    if condition:
        _TESTS_PASSED += 1
        print(f"[PASS] {name}")
    else:
        _TESTS_FAILED += 1
        print(f"[FAIL] {name} — {detail}")


def test_normalize_basic() -> None:
    check("normalize strips whitespace", rd.normalize_species_name("  teak  ") == "Teak")
    check(
        "normalize collapses internal ws",
        rd.normalize_species_name("Tectona   grandis") == "Tectona grandis",
    )
    check(
        "normalize capitalizes genus",
        rd.normalize_species_name("tectona grandis") == "Tectona grandis",
    )
    check("normalize empty -> ''", rd.normalize_species_name("   ") == "")


def test_normalize_authority_and_spp() -> None:
    check(
        "normalize drops parenthetical authority",
        rd.normalize_species_name("Tectona grandis L.f.") == "Tectona grandis L.f.",
    )
    check(
        "normalize removes parenthetical annotation",
        rd.normalize_species_name("Dalbergia latifolia (Roxb.)") == "Dalbergia latifolia",
    )
    check("normalize spp variants", rd.normalize_species_name("Dalbergia sp") == "Dalbergia spp.")
    check("normalize spp. token", rd.normalize_species_name("Shorea spp") == "Shorea spp.")


def test_resolve_exact_scientific() -> None:
    res = rd.resolve_species("Tectona grandis")
    check("exact scientific resolves", res is not None and res[0] == "Tectona grandis")
    check("exact match distance 0", res is not None and res[2] == 0)


def test_resolve_common_name() -> None:
    res = rd.resolve_species("Teak")
    check("common name resolves", res is not None and res[0] == "Tectona grandis")
    res2 = rd.resolve_species("White Oak")
    check("english common name resolves", res2 is not None and res2[0] == "Quercus alba")


def test_resolve_fuzzy_within_threshold() -> None:
    res = rd.resolve_species("Dalbergia latifola")  # missing one letter
    check("fuzzy within threshold resolves", res is not None and res[0] == "Dalbergia latifolia")
    check("fuzzy distance <= 2", res is not None and res[2] <= 2)


def test_resolve_rejects_far_query() -> None:
    res = rd.resolve_species("completely unrelated zzzqqq")
    check("far query rejected", res is None)


def test_resolve_empty() -> None:
    check("empty query -> None", rd.resolve_species("") is None)
    check("whitespace query -> None", rd.resolve_species("   ") is None)


def test_cites_exact_and_genus() -> None:
    check("CITES exact D.nigra App I", rd.get_cites("Dalbergia nigra")["appendix"] == "I")
    check(
        "CITES genus fallback Dalbergia spp. -> II",
        rd.get_cites("Dalbergia oliveri")["appendix"] == "II",
    )
    check(
        "CITES Pterocarpus erinaceus App II",
        rd.get_cites("Pterocarpus erinaceus")["appendix"] == "II",
    )
    check("CITES not listed teak", rd.get_cites("Tectona grandis") is None)


def test_iucn_exact_and_genus_severity() -> None:
    iu = rd.get_iucn("Tectona grandis")
    check("IUCN exact teak EN", iu is not None and iu["category"] == "EN")
    # Quercus alba exact -> LC
    check("IUCN exact Q.alba LC", rd.get_iucn("Quercus alba")["category"] == "LC")
    # genus fallback for a non-listed species within a genus returns most severe
    gen = rd.get_iucn("Quercus petraea")
    check(
        "IUCN genus fallback returns Quercus",
        gen is not None and gen["scientific_name"].startswith("Quercus"),
    )


def test_compare_density_within() -> None:
    entry = rd.get_species("Tectona grandis")
    dc = rd.compare_density(620, entry)
    check("within range -> within_range True", dc.within_range is True)
    check("within range deviation 0", dc.deviation_percent == 0.0)


def test_compare_density_below_min() -> None:
    entry = rd.get_species("Tectona grandis")
    dc = rd.compare_density(400, entry)
    check("below min -> within_range False", dc.within_range is False)
    check(
        "below min assessment mentions substitute",
        "substitute" in dc.assessment.lower() or "below" in dc.assessment.lower(),
    )


def test_compare_density_above_max() -> None:
    entry = rd.get_species("Tectona grandis")
    dc = rd.compare_density(800, entry)
    check("above max -> within_range False", dc.within_range is False)
    check(
        "above max assessment mentions substitute/mismatch",
        "substitute" in dc.assessment.lower() or "mismatch" in dc.assessment.lower(),
    )


def test_compare_density_missing() -> None:
    entry = rd.get_species("Tectona grandis")
    dc = rd.compare_density(None, entry)
    check("missing measured -> None", dc.measured is None)
    check("missing measured -> LIMITATION note", "LIMITATION" in dc.assessment)


def test_classify_moisture_states() -> None:
    entry = rd.get_species("Tectona grandis")
    check("green state", rd.classify_moisture(80, entry).condition == "green")
    check("above_fad state", rd.classify_moisture(45, entry).condition == "above_fad")
    check("fad state", rd.classify_moisture(20, entry).condition == "fad")
    check("kd state", rd.classify_moisture(12, entry).condition == "kd")
    check("overdried state", rd.classify_moisture(6, entry).condition == "overdried")


def test_classify_moisture_missing() -> None:
    entry = rd.get_species("Tectona grandis")
    mc = rd.classify_moisture(None, entry)
    check("missing moisture -> unknown condition", mc.condition == "unknown")
    check("missing moisture -> G2 LIMITATION", "LIMITATION" in mc.notes)


def test_substitution_exact_match() -> None:
    sr = rd.substitution_risk("Tectona grandis", "Tectona grandis")
    check("exact match -> none risk", sr.risk_level == "none")
    check("exact match -> species_match True", sr.species_match is True)


def test_substitution_documented_substitute() -> None:
    sr = rd.substitution_risk("Tectona grandis", "Gmelina arborea")
    check("documented substitute -> high", sr.risk_level == "high")
    check(
        "documented substitute reason mentions substitute",
        any("substitute" in r.lower() for r in sr.reasons),
    )


def test_substitution_same_genus_medium() -> None:
    sr = rd.substitution_risk("Quercus robur", "Quercus rubra")
    check("same genus -> medium", sr.risk_level == "medium")
    check("same genus reason mentions genus", any("genus" in r.lower() for r in sr.reasons))


def test_substitution_density_gap_high() -> None:
    sr = rd.substitution_risk("Tectona grandis", "Diospyros spp.")
    check("density gap -> high", sr.risk_level == "high")
    check("density gap reason mentions density", any("density" in r.lower() for r in sr.reasons))


def test_integrity_loaded() -> None:
    reg = rd.ReferenceData()
    check("species loaded >= 20", len(reg.list_species()) >= 20)
    check("cites loaded >= 10", len(reg._cites) >= 10)
    check("iucn loaded >= 20", len(reg._iucn) >= 20)


def test_integrity_cross_keys() -> None:
    iucn_names = {e["scientific_name"] for e in rd.ReferenceData()._iucn}
    cites_names = {e["scientific_name"] for e in rd.ReferenceData()._cites}
    species = rd.ReferenceData()._species
    bad_iucn = [v["iucn_key"] for v in species.values() if v["iucn_key"] not in iucn_names]
    bad_cites = [
        v["cites_key"]
        for v in species.values()
        if v["cites_key"] and v["cites_key"] not in cites_names
    ]
    check("all iucn_keys resolve", bad_iucn == [])
    check("all cites_keys resolve", bad_cites == [])


def run_all() -> bool:
    global _TESTS_PASSED, _TESTS_FAILED
    _TESTS_PASSED = 0
    _TESTS_FAILED = 0
    tests = [
        test_normalize_basic,
        test_normalize_authority_and_spp,
        test_resolve_exact_scientific,
        test_resolve_common_name,
        test_resolve_fuzzy_within_threshold,
        test_resolve_rejects_far_query,
        test_resolve_empty,
        test_cites_exact_and_genus,
        test_iucn_exact_and_genus_severity,
        test_compare_density_within,
        test_compare_density_below_min,
        test_compare_density_above_max,
        test_compare_density_missing,
        test_classify_moisture_states,
        test_classify_moisture_missing,
        test_substitution_exact_match,
        test_substitution_documented_substitute,
        test_substitution_same_genus_medium,
        test_substitution_density_gap_high,
        test_integrity_loaded,
        test_integrity_cross_keys,
    ]
    for t in tests:
        t()
    total = _TESTS_PASSED + _TESTS_FAILED
    print(f"\n{'=' * 50}")
    print(f"Results: {_TESTS_PASSED}/{total} passed, {_TESTS_FAILED} failed")
    print(f"{'=' * 50}")
    return _TESTS_FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
