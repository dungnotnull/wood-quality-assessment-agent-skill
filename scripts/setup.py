"""
Wood Quality Assessment - Project Setup & Initialization
Handles project initialization, integrity validation, and environment seeding.

Performs real, functional work:
  - Validates that all required project files and directories exist
  - Creates missing runtime directories (.state, logs)
  - Validates config/settings.yaml parses correctly
  - Validates config/schemas/tool_schemas.json parses correctly
  - Discovers and reports all registered skills via the skill loader
  - Verifies the knowledge base is present and seeded
  - Reports a structured health summary with exit code

Usage:
    python -m scripts.setup init       # initialize dirs + validate
    python -m scripts.setup validate  # validate only (no writes)
    python -m scripts.setup status     # print health summary
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a runtime dep
    yaml = None  # type: ignore[assignment]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("wqa.setup")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "skills",
    "tools",
    "scripts",
    "config",
    "config/schemas",
    "references",
    "references/templates",
    "assets",
    "assets/diagrams",
    "assets/examples",
    "tests",
    "logs",
]

RUNTIME_DIRS = [
    ".state",
    "logs",
]

REQUIRED_FILES = [
    "skills/main.md",
    "skills/sub-gather-requirements.md",
    "skills/sub-evidence-collector.md",
    "skills/sub-grain-image-analysis.md",
    "skills/sub-physical-property-analysis.md",
    "skills/sub-authenticity-compliance.md",
    "skills/sub-knowledge-updater.md",
    "skills/sub-quality-advisor.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "config/settings.yaml",
    "config/schemas/tool_schemas.json",
    "scripts/hooks_system.py",
    "scripts/skill_loader.py",
    "scripts/validator.py",
    "scripts/setup.py",
    "scripts/__init__.py",
    "tools/knowledge_updater.py",
    "tools/run_test_scenarios.py",
    "tools/test_knowledge_updater.py",
    "tools/__init__.py",
    "references/templates/output_template.md",
    "references/species_database.json",
    "references/cites_listings.json",
    "references/iucn_status.json",
    "assets/diagrams/system_architecture.md",
    "assets/examples/sample_input.json",
    "assets/examples/sample_output.md",
    "scripts/reference_data.py",
    "scripts/tools_registry.py",
    "scripts/seed_reference_data.py",
    "skills/sub-router.md",
    "tools/test_reference_data.py",
    "tools/test_tools_registry.py",
    "pyproject.toml",
    "requirements.txt",
]


@dataclass
class HealthReport:
    """Structured health report for the project."""

    checks_passed: int = 0
    checks_failed: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skills_discovered: int = 0
    config_valid: bool = False
    schemas_valid: bool = False
    knowledge_base_seeded: bool = False

    @property
    def is_healthy(self) -> bool:
        return self.checks_failed == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "is_healthy": self.is_healthy,
            "errors": self.errors,
            "warnings": self.warnings,
            "skills_discovered": self.skills_discovered,
            "config_valid": self.config_valid,
            "schemas_valid": self.schemas_valid,
            "knowledge_base_seeded": self.knowledge_base_seeded,
        }


def _check(condition: bool, report: HealthReport, ok_msg: str, fail_msg: str) -> None:
    """Record a single check result."""
    if condition:
        report.checks_passed += 1
        logger.debug(ok_msg)
    else:
        report.checks_failed += 1
        report.errors.append(fail_msg)
        logger.error(fail_msg)


def validate_directories(report: HealthReport) -> None:
    """Validate that all required directories exist."""
    for d in REQUIRED_DIRS:
        path = PROJECT_ROOT / d
        _check(path.is_dir(), report, f"Directory OK: {d}", f"Missing directory: {d}")


def create_runtime_dirs(report: HealthReport) -> None:
    """Create runtime directories that must exist for the system to function."""
    for d in RUNTIME_DIRS:
        path = PROJECT_ROOT / d
        try:
            path.mkdir(parents=True, exist_ok=True)
            report.checks_passed += 1
            logger.info(f"Ensured runtime directory: {d}")
        except OSError as e:
            report.checks_failed += 1
            report.errors.append(f"Cannot create {d}: {e}")
            logger.error(f"Cannot create {d}: {e}")


def validate_files(report: HealthReport) -> None:
    """Validate that all required files exist and are non-empty."""
    for f in REQUIRED_FILES:
        path = PROJECT_ROOT / f
        exists = path.is_file()
        nonempty = exists and path.stat().st_size > 0
        _check(nonempty, report, f"File OK: {f}", f"Missing or empty file: {f}")


def validate_config(report: HealthReport) -> None:
    """Validate that config/settings.yaml parses as valid YAML."""
    config_path = PROJECT_ROOT / "config" / "settings.yaml"
    if not config_path.is_file():
        report.checks_failed += 1
        report.errors.append("config/settings.yaml not found")
        return

    if yaml is None:
        report.warnings.append("PyYAML not installed; skipping YAML validation")
        return

    try:
        with open(config_path, encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        _check(
            isinstance(config, dict) and "system" in config,
            report,
            "Config YAML valid",
            "Config YAML invalid or missing 'system' key",
        )
        report.config_valid = True
    except yaml.YAMLError as e:
        report.checks_failed += 1
        report.errors.append(f"YAML parse error in settings.yaml: {e}")
        logger.error(f"YAML parse error: {e}")


def validate_schemas(report: HealthReport) -> None:
    """Validate that config/schemas/tool_schemas.json parses as valid JSON."""
    schema_path = PROJECT_ROOT / "config" / "schemas" / "tool_schemas.json"
    if not schema_path.is_file():
        report.checks_failed += 1
        report.errors.append("config/schemas/tool_schemas.json not found")
        return

    try:
        with open(schema_path, encoding="utf-8") as fh:
            schemas = json.load(fh)
        required_keys = ["toolSchemas", "subSkillSchemas", "qualityGateSchemas"]
        has_all = all(k in schemas for k in required_keys)
        _check(
            has_all,
            report,
            "Schemas JSON valid with all required keys",
            f"Schemas JSON missing required keys: {required_keys}",
        )
        report.schemas_valid = has_all
    except json.JSONDecodeError as e:
        report.checks_failed += 1
        report.errors.append(f"JSON parse error in tool_schemas.json: {e}")
        logger.error(f"JSON parse error: {e}")


def validate_knowledge_base(report: HealthReport) -> None:
    """Validate that SECOND-KNOWLEDGE-BRAIN.md exists and is seeded."""
    skb_path = PROJECT_ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
    if not skb_path.is_file():
        report.checks_failed += 1
        report.errors.append("SECOND-KNOWLEDGE-BRAIN.md not found")
        return

    content = skb_path.read_text(encoding="utf-8")
    min_size = 5000
    has_citations = "DOI" in content or "doi" in content
    has_cites = "CITES" in content
    has_iawa = "IAWA" in content

    _check(
        len(content) > min_size,
        report,
        "Knowledge base has sufficient content",
        f"Knowledge base too small ({len(content)} bytes, need {min_size})",
    )
    _check(
        has_citations, report, "Knowledge base has citations", "Knowledge base lacks DOI citations"
    )
    _check(has_cites, report, "Knowledge base has CITES data", "Knowledge base lacks CITES data")
    _check(has_iawa, report, "Knowledge base has IAWA data", "Knowledge base lacks IAWA data")

    report.knowledge_base_seeded = has_citations and has_cites and has_iawa


def discover_skills(report: HealthReport) -> None:
    """Use the skill loader to discover and count registered skills."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.skill_loader import SkillLoader

        loader = SkillLoader()
        registry = loader.discover_skills()
        report.skills_discovered = len(registry)
        _check(
            len(registry) >= 8,
            report,
            f"Discovered {len(registry)} skills",
            f"Expected >=8 skills, found {len(registry)}",
        )
    except Exception as e:
        report.checks_failed += 1
        report.errors.append(f"Skill discovery failed: {e}")
        logger.error(f"Skill discovery failed: {e}")


def validate_reference_data(report: HealthReport) -> None:
    """Validate the curated reference datasets (species / CITES / IUCN) and the example output.

    Confirms each JSON file parses, is non-empty, and (for species) that every
    cites_key/iucn_key cross-resolves. Also exercises the reference-data module
    and tools registry to ensure the grounding layer imports cleanly.
    """
    ref_dir = PROJECT_ROOT / "references"
    for name in ("species_database.json", "cites_listings.json", "iucn_status.json"):
        path = ref_dir / name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            nonempty = bool(data)
            _check(
                nonempty,
                report,
                f"Reference JSON OK: {name}",
                f"Reference JSON empty/invalid: {name}",
            )
        except Exception as e:
            report.checks_failed += 1
            report.errors.append(f"Reference JSON parse error {name}: {e}")
            logger.error(f"Reference JSON parse error {name}: {e}")

    # cross-key integrity for the species database
    try:
        species = json.loads((ref_dir / "species_database.json").read_text(encoding="utf-8"))
        cites_names = {
            e["scientific_name"]
            for e in json.loads((ref_dir / "cites_listings.json").read_text(encoding="utf-8"))
        }
        iucn_names = {
            e["scientific_name"]
            for e in json.loads((ref_dir / "iucn_status.json").read_text(encoding="utf-8"))
        }
        bad_iucn = [v["iucn_key"] for v in species.values() if v["iucn_key"] not in iucn_names]
        bad_cites = [
            v["cites_key"]
            for v in species.values()
            if v["cites_key"] and v["cites_key"] not in cites_names
        ]
        _check(
            not bad_iucn, report, "Species iucn_keys resolve", f"unresolved iucn_keys: {bad_iucn}"
        )
        _check(
            not bad_cites,
            report,
            "Species cites_keys resolve",
            f"unresolved cites_keys: {bad_cites}",
        )
    except Exception as e:
        report.checks_failed += 1
        report.errors.append(f"Reference cross-key check failed: {e}")

    # import-smoke for the grounding + tools layer
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts import reference_data as rd  # noqa: F401
        from scripts.tools_registry import get_registry  # noqa: F401

        reg = get_registry()
        _check(
            len(reg.list_tools()) >= 8,
            report,
            "Tools registry bootstraps >=8 tools",
            "Tools registry boot failed",
        )
    except Exception as e:
        report.checks_failed += 1
        report.errors.append(f"Reference/tools import smoke failed: {e}")
        logger.error(f"Reference/tools import smoke failed: {e}")

    # example output presence
    ex = PROJECT_ROOT / "assets" / "examples" / "sample_output.md"
    _check(
        ex.is_file() and ex.stat().st_size > 0,
        report,
        "Example output OK",
        "Missing assets/examples/sample_output.md",
    )


def run_validation() -> HealthReport:
    """Run full validation suite and return a health report."""
    report = HealthReport()
    validate_directories(report)
    validate_files(report)
    validate_config(report)
    validate_schemas(report)
    validate_knowledge_base(report)
    validate_reference_data(report)
    discover_skills(report)
    return report


def run_init() -> HealthReport:
    """Create runtime directories then run full validation."""
    report = HealthReport()
    create_runtime_dirs(report)
    validate_directories(report)
    validate_files(report)
    validate_config(report)
    validate_schemas(report)
    validate_knowledge_base(report)
    validate_reference_data(report)
    discover_skills(report)
    return report


def print_report(report: HealthReport) -> None:
    """Print a structured health summary."""
    print("=" * 60)
    print("Wood Quality Assessment - Project Health Report")
    print("=" * 60)
    print(f"  Checks passed:  {report.checks_passed}")
    print(f"  Checks failed:  {report.checks_failed}")
    print(f"  Skills found:   {report.skills_discovered}")
    print(f"  Config valid:   {report.config_valid}")
    print(f"  Schemas valid:  {report.schemas_valid}")
    print(f"  KB seeded:      {report.knowledge_base_seeded}")
    print(f"  Overall health: {'HEALTHY' if report.is_healthy else 'ISSUES DETECTED'}")
    if report.warnings:
        print("\n  Warnings:")
        for w in report.warnings:
            print(f"    - {w}")
    if report.errors:
        print("\n  Errors:")
        for e in report.errors:
            print(f"    - {e}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on failure."""
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m scripts.setup [init|validate|status]")
        print("  init      Create runtime dirs + validate project")
        print("  validate  Validate project integrity (no writes)")
        print("  status     Print health summary only")
        return 0

    command = argv[0].lower()

    if command == "init":
        report = run_init()
        print_report(report)
        return 0 if report.is_healthy else 1
    elif command == "validate":
        report = run_validation()
        print_report(report)
        return 0 if report.is_healthy else 1
    elif command == "status":
        report = run_validation()
        print_report(report)
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m scripts.setup [init|validate|status]")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
