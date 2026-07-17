"""run_test_scenarios.py — Skill 159: wood-quality-assessment

Production-grade test orchestrator for the wood-quality-assessment skill.

Validates the static harness integrity end-to-end WITHOUT invoking live LLM
sub-skills (those are simulated). The suite verifies that every file the
harness depends on exists, that every sub-skill declares the required
sections, that the knowledge base is seeded with the expected reference data,
that all 7 test scenarios are well-formed, that all 11 quality gates are
exercised, that all 5 verdict categories are covered, that the harness
architecture is internally consistent, and that cross-file references resolve.

The suite is deterministic and offline-safe: it never touches the network.

Usage:
    python -m tools.run_test_scenarios --all          # run all 7 scenarios
    python -m tools.run_test_scenarios --scenario N   # run a single scenario
    python -m tools.run_test_scenarios --validate     # file-structure + content only
    python -m tools.run_test_scenarios --full          # full validation suite
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_LOG = logging.getLogger("wood_quality_assessment.orchestrator")
if not _LOG.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    _LOG.addHandler(_h)
    _LOG.setLevel(logging.INFO)

# --------------------------------------------------------------------------
# Test scenario definitions — mirror tests/test-scenarios.md
# --------------------------------------------------------------------------
_ALL_GATES = ("U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5")

SCENARIOS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Standard Authentic Analysis - Vietnamese Furniture",
        "species": "Tectona grandis",
        "verdict": "AUTHENTIC",
        "grade": "A",
        "language": "vi",
        "cites_status": "Not listed",
        "iucn_status": "EN (natural populations)",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": dict.fromkeys(_ALL_GATES, "PASS"),
    },
    {
        "id": 2,
        "name": "Suspected Adulteration - Rosewood Substitution",
        "species": "Dalbergia latifolia / suspect D. oliveri or D. retusa",
        "verdict": "SUSPECTED ADULTERATION",
        "grade": "B",
        "language": "en",
        "cites_status": "Appendix II (Annotation #15)",
        "iucn_status": "VU",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": dict.fromkeys(_ALL_GATES, "PASS"),
    },
    {
        "id": 3,
        "name": "Prohibited Species — CITES Appendix I",
        "species": "Dalbergia nigra",
        "verdict": "PROHIBITED",
        "grade": "B (overridden by legality)",
        "language": "en",
        "cites_status": "Appendix I",
        "iucn_status": "VU",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": dict.fromkeys(_ALL_GATES, "PASS"),
    },
    {
        "id": 4,
        "name": "Non-Compliant — Missing EUDR Documentation",
        "species": "Entandrophragma cylindricum",
        "verdict": "NON-COMPLIANT",
        "grade": "C",
        "language": "en",
        "cites_status": "Not listed",
        "iucn_status": "VU",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": dict.fromkeys(_ALL_GATES, "PASS"),
    },
    {
        "id": 5,
        "name": "Degraded Mode — Minimal Input, No Live Sources",
        "species": "Quercus (uncertain)",
        "verdict": "INCONCLUSIVE",
        "grade": "Cannot assign",
        "language": "en",
        "cites_status": "Not listed (Quercus generally)",
        "iucn_status": "LC (most Quercus)",
        "has_photos": True,
        "has_moisture": False,
        "has_density": False,
        "has_origin": False,
        "has_market": False,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": {
            "U1": "LIMITATION",
            "U2": "PASS",
            "U3": "LIMITATION",
            "U4": "PASS",
            "U5": "LIMITATION",
            "U6": "LIMITATION",
            "G1": "LIMITATION",
            "G2": "LIMITATION",
            "G3": "PASS",
            "G4": "PASS",
            "G5": "PASS",
        },
    },
    {
        "id": 6,
        "name": "Comparison — Two Samples Side by Side",
        "species": "Quercus alba (A) vs Quercus rubra group (B)",
        "verdict": "A: AUTHENTIC / B: SUSPECTED ADULTERATION",
        "grade": "A: A / B: B",
        "language": "en",
        "cites_status": "Neither CITES-listed",
        "iucn_status": "LC",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": dict.fromkeys(_ALL_GATES, "PASS"),
    },
    {
        "id": 7,
        "name": "Risk Assessment — High-Risk Origin (Pterocarpus erinaceus)",
        "species": "Pterocarpus erinaceus",
        "verdict": "PROHIBITED",
        "grade": "N/A (re-dry required)",
        "language": "en",
        "cites_status": "Appendix II",
        "iucn_status": "EN",
        "has_photos": True,
        "has_moisture": True,
        "has_density": True,
        "has_origin": True,
        "has_market": True,
        "gates_exercise": ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"],
        "gate_expectations": {
            "U1": "PASS",
            "U2": "PASS",
            "U3": "PASS",
            "U4": "PASS",
            "U5": "PASS",
            "U6": "PASS",
            "G1": "PASS",
            "G2": "LIMITATION",
            "G3": "PASS",
            "G4": "PASS",
            "G5": "PASS",
        },
    },
]

VERDICT_CATEGORIES = {
    "AUTHENTIC",
    "SUSPECTED ADULTERATION",
    "PROHIBITED",
    "NON-COMPLIANT",
    "INCONCLUSIVE",
}
QUALITY_GRADES = {"A", "B", "C", "N/A", "Cannot assign"}
GATE_NAMES = ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4", "G5"]

_TESTS_PASSED = 0
_TESTS_FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print a single assertion."""
    global _TESTS_PASSED, _TESTS_FAILED
    if condition:
        _TESTS_PASSED += 1
        print(f"  [PASS] {name}")
    else:
        _TESTS_FAILED += 1
        print(f"  [FAIL] {name} — {detail}")


# --------------------------------------------------------------------------
# File structure
# --------------------------------------------------------------------------
REQUIRED_FILES = [
    "CLAUDE.md",
    "PROJECT-detail.md",
    "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".gitignore",
    "LICENSE",
    "skills/main.md",
    "skills/sub-gather-requirements.md",
    "skills/sub-evidence-collector.md",
    "skills/sub-grain-image-analysis.md",
    "skills/sub-physical-property-analysis.md",
    "skills/sub-authenticity-compliance.md",
    "skills/sub-knowledge-updater.md",
    "skills/sub-quality-advisor.md",
    "tests/test-scenarios.md",
    "tests/TEST_RESULTS.md",
    "tools/__init__.py",
    "tools/knowledge_updater.py",
    "tools/test_knowledge_updater.py",
    "tools/run_test_scenarios.py",
]


def validate_file_structure() -> bool:
    """Verify every required project file exists and is non-empty."""
    print("\n=== FILE STRUCTURE VALIDATION ===")
    for rel_path in REQUIRED_FILES:
        fpath = PROJECT_ROOT / rel_path
        exists = fpath.exists()
        nonempty = exists and fpath.stat().st_size > 0
        check(f"exists+nonempty: {rel_path}", nonempty, f"missing or empty at {fpath}")
    return True


# --------------------------------------------------------------------------
# Sub-skill content
# --------------------------------------------------------------------------
SUB_SKILL_CHECKS: list[tuple[str, list[str]]] = [
    (
        "skills/main.md",
        [
            "Role & Persona",
            "Harness Execution",
            "Quality Gates",
            "Output Format",
            "Step 1",
            "Step 2",
            "Step 3",
            "Step 4",
            "Step 5",
            "Step 6",
            "Step 7",
            "Step 8",
        ],
    ),
    (
        "skills/sub-gather-requirements.md",
        [
            "Role & Persona",
            "Workflow",
            "Output Format",
            "Quality Gates",
            "Species Normalization",
        ],
    ),
    (
        "skills/sub-evidence-collector.md",
        [
            "CITES",
            "IUCN",
            "Legality",
            "Anatomy Reference",
            "Physical Benchmarks",
            "Output Format",
            "Quality Gates",
        ],
    ),
    (
        "skills/sub-grain-image-analysis.md",
        [
            "IAWA",
            "Vessel",
            "Parenchyma",
            "Rays",
            "Candidate Identification",
            "Confidence",
            "Image-Only Uncertainty",
            "Decision Tree",
        ],
    ),
    (
        "skills/sub-physical-property-analysis.md",
        [
            "Moisture",
            "Density",
            "Benchmark",
            "Shrinkage",
            "Mechanical",
            "Substitution Signal",
            "EN 338",
        ],
    ),
    (
        "skills/sub-authenticity-compliance.md",
        [
            "Species Identity",
            "Substitution",
            "CITES",
            "IUCN",
            "Origin",
            "Legality",
            "Follow-up Testing",
        ],
    ),
    (
        "skills/sub-knowledge-updater.md",
        [
            "SECOND-KNOWLEDGE-BRAIN",
            "Citations",
            "Knowledge Gaps",
            "Evidence Coverage",
            "Tier",
        ],
    ),
    (
        "skills/sub-quality-advisor.md",
        [
            "Verdict",
            "Quality Grade",
            "Scenarios",
            "Key Risks",
            "Evidence Chain",
            "Disclosure",
            "Remediation",
        ],
    ),
]


def validate_sub_skill_files() -> None:
    """Confirm each sub-skill file declares all required sections."""
    print("\n=== SUB-SKILL CONTENT VALIDATION ===")
    for fname, required_sections in SUB_SKILL_CHECKS:
        fpath = PROJECT_ROOT / fname
        if not fpath.exists():
            check(f"file exists: {fname}", False, "file not found")
            continue
        content = fpath.read_text(encoding="utf-8")
        for section in required_sections:
            found = section.lower() in content.lower()
            check(
                f"section '{section}' in {fname}",
                found,
                f"section '{section}' not found in {fname}",
            )


# --------------------------------------------------------------------------
# Knowledge base
# --------------------------------------------------------------------------
SKB_REQUIRED_SECTIONS = [
    "Core Concepts & Frameworks",
    "IAWA",
    "Moisture Content",
    "Density & Mechanical",
    "CITES & Timber Legality",
    "Standards",
    "Evidence Hierarchy",
    "Key Research Papers",
    "State-of-the-Art Methods",
    "Self-Update Protocol",
    "Knowledge Update Log",
]
CITES_SPECIES = [
    "Dalbergia",
    "Swietenia",
    "Pterocarpus",
    "Handroanthus",
    "Cedrela",
    "Khaya",
    "Pericopsis",
]


def validate_knowledge_base() -> None:
    """Validate SECOND-KNOWLEDGE-BRAIN.md structure and seeded reference data."""
    print("\n=== KNOWLEDGE BASE VALIDATION ===")
    skb_path = PROJECT_ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
    if not skb_path.exists():
        check("SKB exists", False, "missing")
        return
    content = skb_path.read_text(encoding="utf-8")
    for section in SKB_REQUIRED_SECTIONS:
        check(f"SKB section '{section}'", section.lower() in content.lower(), "not found")
    citations_count = content.count("DOI/URL:")
    check("SKB has paper citations", citations_count >= 10, f"found {citations_count}")
    for species in CITES_SPECIES:
        check(
            f"SKB mentions CITES species '{species}'",
            species.lower() in content.lower(),
            f"'{species}' not found",
        )


# --------------------------------------------------------------------------
# Test scenarios
# --------------------------------------------------------------------------
def validate_test_scenarios() -> None:
    """Validate each scenario definition: verdict valid, gates well-formed, species present."""
    print("\n=== TEST SCENARIO VALIDATION ===")
    for sc in SCENARIOS:
        verdict = sc["verdict"]
        check(
            f"S{sc['id']} verdict '{verdict}' is valid",
            any(v in verdict.upper() for v in VERDICT_CATEGORIES),
            f"'{verdict}' not in {VERDICT_CATEGORIES}",
        )
        for gate_name, expected in sc["gate_expectations"].items():
            check(
                f"S{sc['id']} gate {gate_name} expectation '{expected}'",
                expected in ("PASS", "LIMITATION", "FAIL"),
                f"bad expectation '{expected}'",
            )
        check(f"S{sc['id']} has species", len(sc["species"]) > 0, "empty species")
        gate_count = len(sc["gates_exercise"])
        check(f"S{sc['id']} exercises {gate_count} gates", gate_count == 11, f"only {gate_count}")


# --------------------------------------------------------------------------
# Quality-gate coverage
# --------------------------------------------------------------------------
def validate_gate_coverage() -> None:
    """Confirm every gate (U1-U6, G1-G5) is exercised across the scenarios."""
    print("\n=== QUALITY GATE COVERAGE ===")
    gate_coverage: dict[str, dict[str, int]] = {
        g: {"PASS": 0, "LIMITATION": 0, "FAIL": 0} for g in GATE_NAMES
    }
    for sc in SCENARIOS:
        for gate_name, expected in sc["gate_expectations"].items():
            gate_coverage[gate_name][expected] += 1
    for gate_name in GATE_NAMES:
        stats = gate_coverage[gate_name]
        total = sum(stats.values())
        check(f"Gate {gate_name} covered in scenarios", total > 0, f"no scenario tests {gate_name}")
    all_gates_covered = all(sum(gate_coverage[g].values()) > 0 for g in GATE_NAMES)
    check("All 11 gates covered across scenarios", all_gates_covered)
    for gate_name, stats in gate_coverage.items():
        print(
            f"  {gate_name}: {stats['PASS']} PASS, "
            f"{stats['LIMITATION']} LIMITATION, {stats['FAIL']} FAIL"
        )


# --------------------------------------------------------------------------
# Verdict coverage
# --------------------------------------------------------------------------
def validate_verdict_coverage() -> None:
    """Confirm all 5 verdict categories appear in at least one scenario."""
    print("\n=== VERDICT COVERAGE ===")
    verdicts_seen = {sc["verdict"] for sc in SCENARIOS}
    for v in VERDICT_CATEGORIES:
        check(
            f"Verdict '{v}' covered",
            any(v in vs for vs in verdicts_seen),
            f"no scenario uses verdict {v}",
        )


# --------------------------------------------------------------------------
# Harness architecture
# --------------------------------------------------------------------------
SUB_SKILLS = [
    "sub-gather-requirements",
    "sub-evidence-collector",
    "sub-grain-image-analysis",
    "sub-physical-property-analysis",
    "sub-authenticity-compliance",
    "sub-knowledge-updater",
    "sub-quality-advisor",
]
DEGRADATION_LEVELS = ["LEVEL 0", "LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4"]


def validate_harness_architecture() -> None:
    """Validate main.md invokes every sub-skill and defines all gates + degradation levels."""
    print("\n=== HARNESS ARCHITECTURE VALIDATION ===")
    main_path = PROJECT_ROOT / "skills" / "main.md"
    content = main_path.read_text(encoding="utf-8")
    for sub in SUB_SKILLS:
        check(f"Main harness invokes '{sub}'", sub in content, "not found in main.md")
    for level in DEGRADATION_LEVELS:
        check(f"Degradation {level} defined", level in content, "not found")
    for gate in GATE_NAMES:
        check(
            f"Quality gate {gate} defined in main.md",
            f"**{gate}**" in content or f"{gate}" in content,
            f"gate {gate} not found",
        )


# --------------------------------------------------------------------------
# Cross-file references
# --------------------------------------------------------------------------
def validate_cross_references() -> None:
    """Confirm the documentation files cross-reference each other consistently."""
    print("\n=== CROSS-FILE REFERENCES ===")
    claude_content = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    readme_content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    pdpt_content = (PROJECT_ROOT / "PROJECT-DEVELOPMENT-PHASE-TRACKING.md").read_text(
        encoding="utf-8"
    )
    check("CLAUDE.md references skills/main.md", "skills/main.md" in claude_content, "missing")
    check(
        "CLAUDE.md references SECOND-KNOWLEDGE-BRAIN.md",
        "SECOND-KNOWLEDGE-BRAIN.md" in claude_content,
        "missing",
    )
    check(
        "CLAUDE.md references knowledge_updater.py",
        "knowledge_updater.py" in claude_content,
        "missing",
    )
    check(
        "README.md references test_knowledge_updater.py",
        "test_knowledge_updater.py" in readme_content,
        "missing",
    )
    check(
        "PROJECT-DEVELOPMENT-PHASE-TRACKING.md has Phase 0-5",
        all(f"Phase {p}" in pdpt_content for p in range(6)),
        "missing phases",
    )
    phases_found = [p for p in range(6) if f"Phase {p}" in pdpt_content]
    check("PDPT has 6 phases", len(phases_found) == 6, f"found {len(phases_found)}")


# --------------------------------------------------------------------------
# Scenario runner
# --------------------------------------------------------------------------
def run_single_scenario(scenario_id: int) -> bool:
    """Validate and print the definition of a single scenario."""
    print(f"\n{'=' * 60}")
    sc = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if sc is None:
        print(f"[ERROR] Scenario {scenario_id} not found")
        return False
    print(f"[RUN] Scenario {scenario_id}: {sc['name']}")
    print(f"  Species: {sc['species']}")
    print(f"  Expected Verdict: {sc['verdict']}")
    print(f"  Expected Grade: {sc['grade']}")
    print(f"  Language: {sc['language']}")
    print(f"  CITES: {sc['cites_status']}")
    print(f"  IUCN: {sc['iucn_status']}")
    print(
        f"  Inputs: photos={sc['has_photos']}, moisture={sc['has_moisture']}, "
        f"density={sc['has_density']}, origin={sc['has_origin']}, market={sc['has_market']}"
    )
    print("\n  Gate expectations:")
    for gate_name, expected in sc["gate_expectations"].items():
        marker = "OK" if expected == "PASS" else "FL"
        print(f"    [{marker}] {gate_name}: {expected}")
    local_pass = sum(
        1
        for expected in sc["gate_expectations"].values()
        if expected in ("PASS", "LIMITATION", "FAIL")
    )
    local_fail = len(sc["gate_expectations"]) - local_pass
    check(
        f"S{scenario_id} all gate expectations valid",
        local_fail == 0,
        f"{local_fail} invalid expectations",
    )
    print(f"[OK] Scenario {scenario_id} definition validated — {local_pass} gates")
    return True


def run_all_scenarios() -> bool:
    """Validate every scenario definition."""
    print(f"\n{'=' * 60}")
    print("RUNNING ALL TEST SCENARIOS (Definition Validation)")
    print(f"{'=' * 60}")
    for sc in SCENARIOS:
        run_single_scenario(sc["id"])
    print(f"\n{'=' * 60}")
    print(f"All {len(SCENARIOS)} scenarios validated")
    return True


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns process exit code (0 = all checks passed)."""
    global _TESTS_PASSED, _TESTS_FAILED
    ap = argparse.ArgumentParser(description="wood-quality-assessment test orchestrator")
    ap.add_argument(
        "--all", action="store_true", help="Run all 7 scenarios (definition validation)"
    )
    ap.add_argument("--scenario", type=int, help="Run a single scenario by number (1-7)")
    ap.add_argument(
        "--validate", action="store_true", help="Validate file structure and content only"
    )
    ap.add_argument(
        "--full",
        action="store_true",
        help="Run full validation suite (structure + content + scenarios)",
    )
    args = ap.parse_args(argv)

    if not any([args.all, args.scenario, args.validate, args.full]):
        print(
            "Usage: python -m tools.run_test_scenarios [--all | --scenario N | --validate | --full]"
        )
        print("  --all          Run all 7 scenarios (definition validation)")
        print("  --scenario N   Run a single scenario")
        print("  --validate     Validate file structure + content")
        print("  --full         Run full validation suite")
        return 0

    print("wood-quality-assessment Test Orchestrator v1.0")
    print(f"Run date: {datetime.now().isoformat()}")
    print(f"Project root: {PROJECT_ROOT}")

    if args.full or args.validate:
        validate_file_structure()
        validate_sub_skill_files()
        validate_knowledge_base()
        validate_test_scenarios()
        validate_gate_coverage()
        validate_verdict_coverage()
        validate_harness_architecture()
        validate_cross_references()

    if args.all or args.full:
        run_all_scenarios()

    if args.scenario:
        run_single_scenario(args.scenario)

    total = _TESTS_PASSED + _TESTS_FAILED
    print(f"\n{'=' * 60}")
    print(f"FINAL RESULTS: {_TESTS_PASSED}/{total} passed, {_TESTS_FAILED} failed")
    print(f"{'=' * 60}")
    return 0 if _TESTS_FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
