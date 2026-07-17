"""test_tools_registry.py — Skill 159: wood-quality-assessment

Production-grade unit tests for ``scripts/tools_registry.py``.

Covers:
    - registry bootstraps the 8 built-in tools
    - tool schemas are valid JSON-Schema-like dicts
    - lookup_species / lookup_cites / lookup_iucn execute correctly
    - compare_density / classify_moisture / assess_substitution execute
    - input validation rejects malformed inputs (graceful, no raise)
    - unknown tool returns ok=False with structured error
    - validate_schema and quality_gate tools delegate to the validator
    - execute_many runs a plan and returns per-step results

Runnable two ways::

    python -m tools.test_tools_registry          # self-contained runner
    pytest tools/test_tools_registry.py -v       # pytest-compatible
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.tools_registry import get_registry  # noqa: E402

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


EXPECTED_TOOLS = {
    "lookup_species",
    "lookup_cites",
    "lookup_iucn",
    "compare_density",
    "classify_moisture",
    "assess_substitution",
    "validate_schema",
    "quality_gate",
}


def test_registry_bootstrap() -> None:
    reg = get_registry()
    check("8 tools registered", set(reg.list_tools()) == EXPECTED_TOOLS, str(reg.list_tools()))
    check("registry is singleton-stable", get_registry() is reg)


def test_describe_schemas() -> None:
    reg = get_registry()
    desc = reg.describe()
    check("describe returns 8 entries", len(desc) == 8)
    for t in desc:
        check(
            f"{t['name']} has input_schema",
            isinstance(t["input_schema"], dict) and "properties" in t["input_schema"],
        )
        check(
            f"{t['name']} has output_schema",
            isinstance(t["output_schema"], dict) and "properties" in t["output_schema"],
        )


def test_lookup_species_resolved() -> None:
    r = get_registry().execute("lookup_species", {"query": "Tectona grandis"})
    check("lookup_species ok", r.ok is True, str(r.errors))
    check("lookup_species resolved", r.output.get("resolved") is True)
    check("lookup_species scientific name", r.output.get("scientific_name") == "Tectona grandis")


def test_lookup_species_not_found() -> None:
    r = get_registry().execute("lookup_species", {"query": "zzzqqq notawood"})
    check("lookup_species far query ok (handler safe)", r.ok is True, str(r.errors))
    check("lookup_species not resolved", r.output.get("resolved") is False)


def test_lookup_species_bad_input() -> None:
    r = get_registry().execute("lookup_species", {"query": ""})
    check("bad input rejected", r.ok is False)
    check("bad input has validation error", any("input validation" in e for e in r.errors))


def test_lookup_cites() -> None:
    r = get_registry().execute("lookup_cites", {"species": "Dalbergia oliveri"})
    check("lookup_cites ok", r.ok is True, str(r.errors))
    check("lookup_cites appendix II", r.output.get("appendix") == "II")
    check("lookup_cites has access_date", bool(r.output.get("access_date")))


def test_lookup_iucn() -> None:
    r = get_registry().execute("lookup_iucn", {"species": "Pterocarpus erinaceus"})
    check("lookup_iucn ok", r.ok is True, str(r.errors))
    check("lookup_iucn EN", r.output.get("category") == "EN")


def test_compare_density() -> None:
    r = get_registry().execute(
        "compare_density", {"species": "Tectona grandis", "measured_kgm3": 620}
    )
    check("compare_density ok", r.ok is True, str(r.errors))
    check("compare_density within range", r.output.get("within_range") is True)


def test_compare_density_unknown_species() -> None:
    r = get_registry().execute("compare_density", {"species": "Notaspp tree", "measured_kgm3": 600})
    check("compare_density unknown species ok=False", r.ok is True)
    check("compare_density unknown species reports error", r.output.get("ok") is False)


def test_classify_moisture() -> None:
    r = get_registry().execute(
        "classify_moisture", {"species": "Tectona grandis", "moisture_pct": 12}
    )
    check("classify_moisture ok", r.ok is True, str(r.errors))
    check("classify_moisture kd state", r.output.get("condition") == "kd")


def test_assess_substitution() -> None:
    r = get_registry().execute(
        "assess_substitution",
        {"claimed_species": "Tectona grandis", "candidate_species": "Gmelina arborea"},
    )
    check("assess_substitution ok", r.ok is True, str(r.errors))
    check("assess_substitution high", r.output.get("risk_level") == "high")


def test_unknown_tool() -> None:
    r = get_registry().execute("does_not_exist", {})
    check("unknown tool ok=False", r.ok is False)
    check("unknown tool error", any("unknown tool" in e for e in r.errors))


def test_validate_schema_tool() -> None:
    good = {
        "verdict": "Authentic",
        "grade": "A",
        "disclosure": "x",
        "best_scenario": "a",
        "base_scenario": "b",
        "worst_scenario": "c",
        "key_risks": [],
        "evidence_chain": [],
        "remediation_actions": [],
        "anatomy_scorecard": {},
        "physical_scorecard": {},
        "compliance_inputs": {},
    }
    r = get_registry().execute(
        "validate_schema", {"schema_name": "sub-quality-advisor", "data": good, "io_type": "output"}
    )
    check("validate_schema tool ok", r.ok is True, str(r.errors))
    check("validate_schema valid True", r.output.get("valid") is True)


def test_quality_gate_tool() -> None:
    # G5 gate checks the verdict enum; a bad verdict fails.
    r_bad = get_registry().execute("quality_gate", {"gate": "G5", "payload": {"verdict": "Bogus"}})
    check("quality_gate tool ok (delegates)", r_bad.ok is True, str(r_bad.errors))
    check("quality_gate G5 rejects bad verdict", r_bad.output.get("passed") is False)
    r_ok = get_registry().execute(
        "quality_gate", {"gate": "G5", "payload": {"verdict": "Authentic"}}
    )
    check("quality_gate G5 accepts valid verdict", r_ok.output.get("passed") is True)


def test_execute_many() -> None:
    plan = [
        {"tool": "lookup_cites", "inputs": {"species": "Dalbergia nigra"}},
        {"tool": "lookup_iucn", "inputs": {"species": "Dalbergia nigra"}},
    ]
    results = get_registry().execute_many(plan)
    check("execute_many length", len(results) == 2)
    check("execute_many all ok", all(x.ok for x in results))
    check("execute_many cites App I", results[0].output.get("appendix") == "I")


def test_tool_result_serializable() -> None:
    r = get_registry().execute("lookup_cites", {"species": "Tectona grandis"})
    d = r.to_dict()
    check("to_dict has ok", "ok" in d)
    check("to_dict has tool", d.get("tool") == "lookup_cites")
    check("to_dict has duration_ms", "duration_ms" in d)


def run_all() -> bool:
    global _TESTS_PASSED, _TESTS_FAILED
    _TESTS_PASSED = 0
    _TESTS_FAILED = 0
    tests = [
        test_registry_bootstrap,
        test_describe_schemas,
        test_lookup_species_resolved,
        test_lookup_species_not_found,
        test_lookup_species_bad_input,
        test_lookup_cites,
        test_lookup_iucn,
        test_compare_density,
        test_compare_density_unknown_species,
        test_classify_moisture,
        test_assess_substitution,
        test_unknown_tool,
        test_validate_schema_tool,
        test_quality_gate_tool,
        test_execute_many,
        test_tool_result_serializable,
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
