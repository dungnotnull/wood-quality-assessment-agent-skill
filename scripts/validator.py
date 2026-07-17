"""
Wood Quality Assessment - Schema Validator
Implements input/output validation and quality gate checking.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wqa.validator")


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    code: str
    message: str
    severity: ValidationSeverity
    field: str | None = None
    expected: Any | None = None
    actual: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "field": self.field,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(
        self,
        code: str,
        message: str,
        field: str | None = None,
        expected: Any | None = None,
        actual: Any | None = None,
    ) -> None:
        """Add an error issue."""
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=ValidationSeverity.ERROR,
                field=field,
                expected=expected,
                actual=actual,
            )
        )
        self.is_valid = False

    def add_warning(self, code: str, message: str, field: str | None = None) -> None:
        """Add a warning issue."""
        self.warnings.append(
            ValidationIssue(
                code=code, message=message, severity=ValidationSeverity.WARNING, field=field
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [issue.to_dict() for issue in self.issues],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "metadata": self.metadata,
        }


class SchemaValidator:
    """Validates data against JSON schemas."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path or Path("config/schemas/tool_schemas.json")
        self.schemas: dict[str, dict[str, Any]] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all schemas from schema file."""
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found: {self.schema_path}")
            return

        try:
            with open(self.schema_path, encoding="utf-8") as f:
                data = json.load(f)
                self.schemas = data
                logger.info(f"Loaded {len(data)} schema categories")
        except Exception as e:
            logger.error(f"Failed to load schemas: {e}")

    def get_schema(
        self, category: str, name: str, schema_type: str = "input"
    ) -> dict[str, Any] | None:
        """Get a specific schema."""
        if category not in self.schemas:
            return None

        category_schemas = self.schemas[category]
        if name not in category_schemas:
            return None

        skill_schemas = category_schemas[name]
        return skill_schemas.get(schema_type)

    def validate(
        self, data: dict[str, Any], category: str, name: str, schema_type: str = "input"
    ) -> ValidationResult:
        """Validate data against schema."""
        result = ValidationResult(is_valid=True)

        schema = self.get_schema(category, name, schema_type)
        if not schema:
            result.add_error(
                code="SCHEMA_NOT_FOUND",
                message=f"Schema not found: {category}/{name}/{schema_type}",
            )
            return result

        # Validate required fields
        if "required" in schema:
            for required_field in schema["required"]:
                if required_field not in data:
                    result.add_error(
                        code="MISSING_REQUIRED_FIELD",
                        message=f"Required field missing: {required_field}",
                        field=required_field,
                    )

        # Validate field types and constraints
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                if field_name not in data:
                    continue

                field_value = data[field_name]
                field_result = self._validate_field(field_value, field_schema, field_name)
                result.issues.extend(field_result.issues)
                result.warnings.extend(field_result.warnings)

        return result

    def _validate_field(
        self, value: Any, schema: dict[str, Any], field_name: str
    ) -> ValidationResult:
        """Validate a single field against its schema."""
        result = ValidationResult(is_valid=True)

        # Type validation
        if "type" in schema:
            type_result = self._validate_type(value, schema["type"], field_name)
            if not type_result.is_valid:
                result.issues.extend(type_result.issues)

        # Enum validation
        if "enum" in schema and value not in schema["enum"]:
            result.add_error(
                code="INVALID_ENUM_VALUE",
                message=f"Value must be one of: {schema['enum']}",
                field=field_name,
                expected=schema["enum"],
                actual=value,
            )

        # String constraints
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                result.add_error(
                    code="STRING_TOO_SHORT",
                    message=f"String must be at least {schema['minLength']} characters",
                    field=field_name,
                    expected=f"length >= {schema['minLength']}",
                    actual=len(value),
                )

            if "maxLength" in schema and len(value) > schema["maxLength"]:
                result.add_error(
                    code="STRING_TOO_LONG",
                    message=f"String must be at most {schema['maxLength']} characters",
                    field=field_name,
                    expected=f"length <= {schema['maxLength']}",
                    actual=len(value),
                )

            if "pattern" in schema:
                pattern = schema["pattern"]
                if not re.match(pattern, value):
                    result.add_error(
                        code="PATTERN_MISMATCH",
                        message="String does not match required pattern",
                        field=field_name,
                        expected=pattern,
                        actual=value,
                    )

        # Number constraints
        if isinstance(value, (int, float)):
            if "minimum" in schema and value < schema["minimum"]:
                result.add_error(
                    code="NUMBER_TOO_SMALL",
                    message=f"Value must be at least {schema['minimum']}",
                    field=field_name,
                    expected=f">= {schema['minimum']}",
                    actual=value,
                )

            if "maximum" in schema and value > schema["maximum"]:
                result.add_error(
                    code="NUMBER_TOO_LARGE",
                    message=f"Value must be at most {schema['maximum']}",
                    field=field_name,
                    expected=f"<= {schema['maximum']}",
                    actual=value,
                )

        # Array constraints
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                result.add_error(
                    code="ARRAY_TOO_SMALL",
                    message=f"Array must have at least {schema['minItems']} items",
                    field=field_name,
                    expected=f"length >= {schema['minItems']}",
                    actual=len(value),
                )

            if "maxItems" in schema and len(value) > schema["maxItems"]:
                result.add_error(
                    code="ARRAY_TOO_LARGE",
                    message=f"Array must have at most {schema['maxItems']} items",
                    field=field_name,
                    expected=f"length <= {schema['maxItems']}",
                    actual=len(value),
                )

        # Object validation
        if isinstance(value, dict) and "required" in schema:
            for required_field in schema["required"]:
                if required_field not in value:
                    result.add_error(
                        code="MISSING_REQUIRED_FIELD",
                        message=f"Required field missing: {required_field}",
                        field=f"{field_name}.{required_field}",
                    )

        return result

    def _validate_type(self, value: Any, type_spec: Any, field_name: str) -> ValidationResult:
        """Validate value against type specification."""
        result = ValidationResult(is_valid=True)

        # Handle array of types
        if isinstance(type_spec, list):
            # Value can be any of the listed types
            if not any(self._check_type(value, t) for t in type_spec):
                result.add_error(
                    code="TYPE_MISMATCH",
                    message=f"Value must be one of types: {type_spec}",
                    field=field_name,
                    expected=type_spec,
                    actual=type(value).__name__,
                )
            return result

        # Single type
        if not self._check_type(value, type_spec):
            result.add_error(
                code="TYPE_MISMATCH",
                message=f"Value must be of type: {type_spec}",
                field=field_name,
                expected=type_spec,
                actual=type(value).__name__,
            )

        return result

    def _check_type(self, value: Any, type_name: str) -> bool:
        """Check if value matches type name."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected_type = type_mapping.get(type_name)
        if expected_type is None:
            return True  # Unknown type, assume valid

        return isinstance(value, expected_type)


class QualityGateChecker:
    """Checks quality gates against outputs."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path or Path("config/schemas/tool_schemas.json")
        self.gate_schemas: dict[str, dict[str, Any]] = {}
        self._load_gate_schemas()

    def _load_gate_schemas(self) -> None:
        """Load quality gate schemas."""
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found: {self.schema_path}")
            return

        try:
            with open(self.schema_path, encoding="utf-8") as f:
                data = json.load(f)
                self.gate_schemas = data.get("qualityGateSchemas", {})
                logger.info(f"Loaded {len(self.gate_schemas)} quality gate schemas")
        except Exception as e:
            logger.error(f"Failed to load gate schemas: {e}")

    def check_gate(self, gate_name: str, output: dict[str, Any]) -> ValidationResult:
        """Check a single quality gate."""
        result = ValidationResult(is_valid=True)

        if gate_name not in self.gate_schemas:
            result.add_error(code="GATE_NOT_FOUND", message=f"Quality gate not found: {gate_name}")
            return result

        gate_schema = self.gate_schemas[gate_name]
        validation = gate_schema.get("validation", {})

        # Execute validation based on gate type
        gate_checks = {
            "U1": self._check_u1,
            "U2": self._check_u2,
            "U3": self._check_u3,
            "U4": self._check_u4,
            "U5": self._check_u5,
            "U6": self._check_u6,
            "G1": self._check_g1,
            "G2": self._check_g2,
            "G3": self._check_g3,
            "G4": self._check_g4,
            "G5": self._check_g5,
        }

        check_func = gate_checks.get(gate_name)
        if check_func:
            check_result = check_func(output, validation)
            result.issues.extend(check_result.issues)
            result.warnings.extend(check_result.warnings)
            result.is_valid = check_result.is_valid
        else:
            result.add_warning(
                code="GATE_NO_IMPLEMENTATION",
                message=f"No check implementation for gate: {gate_name}",
            )

        return result

    def _check_u1(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U1: Source Citation Count."""
        result = ValidationResult(is_valid=True)

        sources = output.get("sources", [])
        if len(sources) < validation.get("min_sources", 3):
            result.add_error(
                code="U1_INSUFFICIENT_SOURCES",
                message=f"Need at least {validation.get('min_sources', 3)} sources",
                expected=f">= {validation.get('min_sources', 3)}",
                actual=len(sources),
            )

        authoritative = validation.get("authoritative_domains", [])
        authoritative_count = sum(
            1 for s in sources if any(domain in s.get("url", "") for domain in authoritative)
        )
        if authoritative_count < validation.get("min_authoritative", 1):
            result.add_error(
                code="U1_INSUFFICIENT_AUTHORITATIVE",
                message=(
                    f"Need at least {validation.get('min_authoritative', 1)} authoritative source"
                ),
                expected=f">= {validation.get('min_authoritative', 1)}",
                actual=authoritative_count,
            )

        return result

    def _check_u2(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U2: Risk Disclosure."""
        result = ValidationResult(is_valid=True)

        disclosure = output.get("disclosure", "")
        if not disclosure:
            result.add_error(code="U2_MISSING_DISCLOSURE", message="Disclosure section required")
            return result

        keywords = validation.get("disclosure_keywords", [])
        has_keywords = any(kw.lower() in disclosure.lower() for kw in keywords)
        if not has_keywords:
            result.add_error(
                code="U2_NO_RISK_KEYWORDS",
                message=f"Disclosure must contain risk keywords: {keywords}",
            )

        return result

    def _check_u3(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U3: Evidence Hierarchy."""
        result = ValidationResult(is_valid=True)

        sources = output.get("sources", [])
        for source in sources:
            if "tier" not in source:
                result.add_error(
                    code="U3_MISSING_TIER",
                    message=f"Source missing tier: {source.get('title', 'Unknown')}",
                )

        return result

    def _check_u4(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U4: Language Consistency."""
        result = ValidationResult(is_valid=True)

        language = output.get("language", "en")
        if language not in validation.get("supported_languages", ["en", "vi"]):
            result.add_warning(
                code="U4_UNSUPPORTED_LANGUAGE", message=f"Language not supported: {language}"
            )

        return result

    def _check_u5(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U5: Output Template."""
        result = ValidationResult(is_valid=True)

        required_sections = validation.get("required_sections", 12)
        section_names = validation.get("section_names", [])

        present_sections = sum(1 for section in section_names if section in output)
        if present_sections < required_sections:
            result.add_error(
                code="U5_MISSING_SECTIONS",
                message=(
                    f"Missing required sections (have {present_sections}, need {required_sections})"
                ),
                expected=required_sections,
                actual=present_sections,
            )

        return result

    def _check_u6(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check U6: Claim Traceability."""
        result = ValidationResult(is_valid=True)

        # Check for citations in content
        content = str(output)
        citation_pattern = validation.get("citation_pattern", r"\[\d+\]")
        has_citations = re.search(citation_pattern, content)

        if not has_citations and not output.get("judgment_flagging"):
            result.add_error(
                code="U6_NO_CITATIONS", message="Claims lack citations or judgment flagging"
            )

        return result

    def _check_g1(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check G1: Species Identification Confidence."""
        result = ValidationResult(is_valid=True)

        confidence = output.get("confidence")
        if not confidence:
            result.add_error(code="G1_MISSING_CONFIDENCE", message="Confidence level required")
            return result

        valid_levels = validation.get("confidence_levels", ["High", "Medium", "Low", "Very Low"])
        if confidence not in valid_levels:
            result.add_error(
                code="G1_INVALID_CONFIDENCE",
                message="Invalid confidence level",
                expected=valid_levels,
                actual=confidence,
            )

        if validation.get("requires_justification", True) and not output.get(
            "confidence_justification"
        ):
            result.add_error(
                code="G1_MISSING_JUSTIFICATION", message="Confidence requires justification"
            )

        return result

    def _check_g2(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check G2: Physical Benchmark Comparison."""
        result = ValidationResult(is_valid=True)

        required_comparisons = validation.get("required_comparisons", ["moisture", "density"])
        for comparison in required_comparisons:
            if f"{comparison}_comparison" not in output:
                result.add_error(
                    code="G2_MISSING_COMPARISON", message=f"Missing comparison for: {comparison}"
                )

        if validation.get("benchmark_source_required", True) and not output.get("benchmark_source"):
            result.add_error(
                code="G2_MISSING_BENCHMARK_SOURCE", message="Benchmark source required"
            )

        return result

    def _check_g3(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check G3: CITES/IUCN Verification."""
        result = ValidationResult(is_valid=True)

        required_checks = validation.get("required_checks", ["cites", "iucn"])
        for check in required_checks:
            if f"{check}_status" not in output:
                result.add_error(code="G3_MISSING_STATUS", message=f"Missing status check: {check}")

        if validation.get("access_date_required", True):
            for check in required_checks:
                status = output.get(f"{check}_status", {})
                if isinstance(status, dict) and not status.get("access_date"):
                    result.add_error(
                        code="G3_MISSING_ACCESS_DATE", message=f"Missing access date for: {check}"
                    )

        return result

    def _check_g4(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check G4: Legality Assessment."""
        result = ValidationResult(is_valid=True)

        if validation.get("target_market_required", True) and not output.get("target_market"):
            result.add_error(code="G4_MISSING_MARKET", message="Target market required")

        if validation.get("regulation_names_required", True):
            regulations = output.get("legality_regulations", [])
            if not regulations or not isinstance(regulations, list):
                result.add_error(code="G4_MISSING_REGULATIONS", message="Regulation names required")

        return result

    def _check_g5(self, output: dict[str, Any], validation: dict[str, Any]) -> ValidationResult:
        """Check G5: Verdict Category."""
        result = ValidationResult(is_valid=True)

        verdict = output.get("verdict")
        valid_verdicts = validation.get(
            "valid_verdicts",
            ["Authentic", "Suspected Adulteration", "Prohibited", "Non-compliant", "Inconclusive"],
        )

        if verdict not in valid_verdicts:
            result.add_error(
                code="G5_INVALID_VERDICT",
                message="Invalid verdict category",
                expected=valid_verdicts,
                actual=verdict,
            )

        return result


# Convenience functions
def validate_input(data: dict[str, Any], skill_name: str) -> tuple[bool, list[str]]:
    """Validate input data for a skill."""
    validator = SchemaValidator()
    result = validator.validate(data, "subSkillSchemas", skill_name, "input")
    return result.is_valid, [issue.message for issue in result.issues]


def validate_output(data: dict[str, Any], skill_name: str) -> tuple[bool, list[str]]:
    """Validate output data for a skill."""
    validator = SchemaValidator()
    result = validator.validate(data, "subSkillSchemas", skill_name, "output")
    return result.is_valid, [issue.message for issue in result.issues]


def check_quality_gate(gate_name: str, output: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check a quality gate against output."""
    checker = QualityGateChecker()
    result = checker.check_gate(gate_name, output)
    return result.is_valid, [issue.message for issue in result.issues]


# CLI interface
if __name__ == "__main__":
    print("Wood Quality Assessment - Schema Validator")
    print("=" * 60)

    # Example validation
    example_input = {
        "claimed_species": "Tectona grandis",
        "language": "en",
        "sample_photos": [],
        "moisture_pct": 12.5,
        "moisture_method": "moisture_meter",
        "density_kgm3": 650,
        "claimed_origin": "Vietnam",
        "intended_use": "furniture",
        "market_region": "EU",
    }

    is_valid, errors = validate_input(example_input, "sub-gather-requirements")

    print(f"\nInput validation: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")

    # Test quality gate
    example_output = {
        "verdict": "Authentic",
        "grade": "A",
        "disclosure": "This analysis has limitations...",
        "sources": [{"title": "Test", "url": "https://example.edu", "tier": "Tier 1"}],
        "language": "en",
    }

    is_valid, errors = check_quality_gate("U1", example_output)
    print(f"\nQuality gate U1: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
