"""Wood Quality Assessment - Tools Registry.

A small, self-contained tool registry that binds *tool schemas* to *execution
handlers* so the harness (and any agent) can discover, validate, and invoke
domain tools dynamically and offline-safely.

Every tool declares:
  * a human/agent description (used for routing),
  * a JSON Schema (Draft 7) input + output contract,
  * a deterministic Python handler.

Handlers reuse the reference-data layer and the schema validator; all external
failures degrade gracefully (the registry never raises to callers - it returns
a ``ToolResult`` with ``ok=False`` and structured errors).

This module is the "rich tool definitions (schemas and execution handlers)"
counterpart to the static ``config/schemas/tool_schemas.json`` catalog: here
the schemas are executable.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Any

try:
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    jsonschema = None  # type: ignore

from scripts import reference_data as rd

logger = logging.getLogger("wqa.tools_registry")

ROOT_SCHEMA = "http://json-schema.org/draft-07/schema#"


@dataclass
class ToolResult:
    """Standardized execution result returned by every tool handler."""

    ok: bool
    output: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    tool: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "output": self.output,
            "errors": self.errors,
            "duration_ms": round(self.duration_ms, 2),
            "tool": self.tool,
        }


@dataclass
class Tool:
    """A registered tool: contract + handler."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _validate(instance: Any, schema: dict[str, Any]) -> list[str]:
    """Validate an instance against a JSON Schema; returns a list of errors."""
    if jsonschema is None:
        return []
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return []
    except jsonschema.ValidationError as exc:  # type: ignore
        return [exc.message]
    except Exception as exc:  # pragma: no cover
        return [f"schema engine error: {exc}"]


class ToolRegistry:
    """Holds registered tools and executes them with schema-guarded handlers."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._lock = RLock()

    # -- registration ------------------------------------------------------
    def register(self, tool: Tool) -> None:
        with self._lock:
            if tool.name in self._tools:
                logger.warning("overwriting already-registered tool %s", tool.name)
            self._tools[tool.name] = tool
            logger.info("registered tool: %s", tool.name)

    def get(self, name: str) -> Tool | None:
        with self._lock:
            return self._tools.get(name)

    def list_tools(self) -> list[str]:
        with self._lock:
            return sorted(self._tools.keys())

    def describe(self) -> list[dict[str, Any]]:
        with self._lock:
            return [t.to_dict() for t in self._tools.values()]

    # -- execution --------------------------------------------------------
    def execute(self, name: str, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        tool = self.get(name)
        if tool is None:
            return ToolResult(
                ok=False, errors=[f"unknown tool: {name}"], tool=name, duration_ms=0.0
            )
        in_errors = _validate(inputs, tool.input_schema)
        if in_errors:
            return ToolResult(
                ok=False,
                errors=[f"input validation: {e}" for e in in_errors],
                tool=name,
                duration_ms=(time.time() - start) * 1000,
            )
        try:
            output = tool.handler(inputs)
        except Exception as exc:  # graceful degradation: never raise to caller
            logger.exception("tool %s handler raised", name)
            return ToolResult(
                ok=False,
                errors=[f"handler error: {type(exc).__name__}: {exc}"],
                tool=name,
                duration_ms=(time.time() - start) * 1000,
            )
        out_errors = _validate(output, tool.output_schema)
        duration_ms = (time.time() - start) * 1000
        return ToolResult(
            ok=len(out_errors) == 0,
            output=output,
            errors=[f"output validation: {e}" for e in out_errors],
            duration_ms=duration_ms,
            tool=name,
        )

    def execute_many(self, plan: list[dict[str, Any]]) -> list[ToolResult]:
        """Execute a sequence of {tool, inputs} steps, returning each result."""
        results: list[ToolResult] = []
        for step in plan:
            name = step.get("tool", "")
            inputs = step.get("inputs", {})
            results.append(self.execute(name, inputs))
        return results


# ---------------------------------------------------------------------- #
# Built-in offline-safe tool handlers. Each returns a plain dict that
# conforms to its declared output schema.
# ---------------------------------------------------------------------- #


def _h_lookup_species(inputs: dict[str, Any]) -> dict[str, Any]:
    res = rd.resolve_species(inputs["query"])
    if res is None:
        return {
            "resolved": False,
            "query": inputs["query"],
            "scientific_name": None,
            "entry": None,
            "edit_distance": None,
            "note": "No match within fuzzy threshold.",
        }
    sci, entry, dist = res
    return {
        "resolved": True,
        "query": inputs["query"],
        "scientific_name": sci,
        "edit_distance": dist,
        "family": entry.get("family"),
        "wood_type": entry.get("wood_type"),
        "porosity": entry.get("porosity"),
        "density_kgm3": entry.get("density_kgm3"),
        "heartwood_color": entry.get("heartwood_color"),
        "native_origin": entry.get("native_origin"),
        "common_substitution_risks": entry.get("common_substitution_risks"),
    }


def _h_lookup_cites(inputs: dict[str, Any]) -> dict[str, Any]:
    species = inputs["species"]
    entry = rd.get_cites(species)
    if entry is None:
        return {
            "species": species,
            "listed": False,
            "appendix": None,
            "annotation": None,
            "note": "Not CITES-listed (verify live at checklist.cites.org).",
        }
    return {
        "species": species,
        "listed": True,
        "appendix": entry["appendix"],
        "annotation": entry.get("annotation"),
        "listing_date": entry.get("listing_date"),
        "notes": entry.get("notes"),
        "source": "references/cites_listings.json",
        "access_date": _now_iso(),
    }


def _h_lookup_iucn(inputs: dict[str, Any]) -> dict[str, Any]:
    species = inputs["species"]
    entry = rd.get_iucn(species)
    if entry is None:
        return {
            "species": species,
            "assessed": False,
            "category": None,
            "note": "No IUCN assessment cached (verify at iucnredlist.org).",
        }
    return {
        "species": species,
        "assessed": True,
        "category": entry["category"],
        "category_full": entry.get("category_full"),
        "trend": entry.get("trend"),
        "assessed_year": entry.get("assessed_year"),
        "notes": entry.get("notes"),
        "source": "references/iucn_status.json",
        "access_date": _now_iso(),
    }


def _h_compare_density(inputs: dict[str, Any]) -> dict[str, Any]:
    entry = rd.get_species(inputs["species"])
    if entry is None:
        return {"species": inputs["species"], "ok": False, "errors": ["species not found"]}
    dc = rd.compare_density(inputs.get("measured_kgm3"), entry)
    out = dc.to_dict()
    out["species"] = inputs["species"]
    out["ok"] = True
    return out


def _h_classify_moisture(inputs: dict[str, Any]) -> dict[str, Any]:
    entry = rd.get_species(inputs["species"])
    if entry is None:
        return {"species": inputs["species"], "ok": False, "errors": ["species not found"]}
    mc = rd.classify_moisture(inputs.get("moisture_pct"), entry)
    out = mc.to_dict()
    out["species"] = inputs["species"]
    out["ok"] = True
    return out


def _h_assess_substitution(inputs: dict[str, Any]) -> dict[str, Any]:
    sr = rd.substitution_risk(inputs["claimed_species"], inputs["candidate_species"])
    out = sr.to_dict()
    out["claimed_species"] = inputs["claimed_species"]
    out["candidate_species"] = inputs["candidate_species"]
    out["ok"] = True
    return out


def _h_validate_schema(inputs: dict[str, Any]) -> dict[str, Any]:
    from scripts.validator import validate_input, validate_output  # local import avoids cycles

    name = inputs["schema_name"]
    data = inputs["data"]
    io_type = inputs.get("io_type", "input")
    if io_type == "output":
        valid, errors = validate_output(data, name)
    else:
        valid, errors = validate_input(data, name)
    return {"schema_name": name, "io_type": io_type, "valid": bool(valid), "errors": errors or []}


def _h_quality_gate(inputs: dict[str, Any]) -> dict[str, Any]:
    from scripts.validator import check_quality_gate  # local import

    gate = inputs["gate"]
    payload = inputs["payload"]
    try:
        passed, errors = check_quality_gate(gate, payload)
    except Exception as exc:
        return {
            "gate": gate,
            "passed": False,
            "errors": [f"gate engine error: {exc}"],
            "auto_fixed": False,
        }
    return {"gate": gate, "passed": bool(passed), "errors": errors or [], "auto_fixed": False}


# ---------------------------------------------------------------------- #
# Tool definitions: schemas + registration.
# ---------------------------------------------------------------------- #
def _species_name_schema() -> dict[str, Any]:
    return {"type": "string", "minLength": 2, "maxLength": 120}


def _build_tools() -> list[Tool]:
    """Construct the list of built-in tools with their schemas."""
    tools: list[Tool] = []

    tools.append(
        Tool(
            name="lookup_species",
            description="Fuzzy-resolve a species name (Levenshtein<=2) to its database profile.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["query"],
                "properties": {"query": _species_name_schema()},
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["resolved", "query"],
                "properties": {
                    "resolved": {"type": "boolean"},
                    "query": {"type": "string"},
                    "scientific_name": {"type": ["string", "null"]},
                    "edit_distance": {"type": ["integer", "null"]},
                    "family": {"type": ["string", "null"]},
                    "wood_type": {"type": ["string", "null"]},
                    "porosity": {"type": ["string", "null"]},
                    "density_kgm3": {"type": ["object", "null"]},
                    "heartwood_color": {"type": ["string", "null"]},
                    "native_origin": {"type": ["array", "null"]},
                    "common_substitution_risks": {"type": ["array", "null"]},
                },
            },
            handler=_h_lookup_species,
        )
    )

    tools.append(
        Tool(
            name="lookup_cites",
            description="Return CITES appendix status for a species (genus-aware fallback).",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species"],
                "properties": {"species": _species_name_schema()},
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species", "listed"],
                "properties": {
                    "species": {"type": "string"},
                    "listed": {"type": "boolean"},
                    "appendix": {"type": ["string", "null"]},
                    "annotation": {"type": ["string", "null"]},
                    "listing_date": {"type": ["string", "null"]},
                    "notes": {"type": ["string", "null"]},
                    "source": {"type": "string"},
                    "access_date": {"type": "string"},
                },
            },
            handler=_h_lookup_cites,
        )
    )

    tools.append(
        Tool(
            name="lookup_iucn",
            description="Return the IUCN Red List category for a species (genus-aware fallback).",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species"],
                "properties": {"species": _species_name_schema()},
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species", "assessed"],
                "properties": {
                    "species": {"type": "string"},
                    "assessed": {"type": "boolean"},
                    "category": {"type": ["string", "null"]},
                    "category_full": {"type": ["string", "null"]},
                    "trend": {"type": ["string", "null"]},
                    "assessed_year": {"type": ["integer", "null"]},
                    "notes": {"type": ["string", "null"]},
                    "source": {"type": "string"},
                    "access_date": {"type": "string"},
                },
            },
            handler=_h_lookup_iucn,
        )
    )

    tools.append(
        Tool(
            name="compare_density",
            description="Compare a measured air-dry density (kg/m^3) to its species benchmark.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species"],
                "properties": {
                    "species": _species_name_schema(),
                    "measured_kgm3": {"type": ["number", "null"]},
                },
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species", "ok"],
                "properties": {
                    "species": {"type": "string"},
                    "ok": {"type": "boolean"},
                    "measured": {"type": ["number", "null"]},
                    "benchmark_typical": {"type": "number"},
                    "benchmark_min": {"type": "number"},
                    "benchmark_max": {"type": "number"},
                    "deviation_percent": {"type": ["number", "null"]},
                    "within_range": {"type": "boolean"},
                    "assessment": {"type": "string"},
                },
            },
            handler=_h_compare_density,
        )
    )

    tools.append(
        Tool(
            name="classify_moisture",
            description="Classify a moisture reading (%%) against the resolved species KD target.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species"],
                "properties": {
                    "species": _species_name_schema(),
                    "moisture_pct": {"type": ["number", "null"]},
                },
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["species", "ok"],
                "properties": {
                    "species": {"type": "string"},
                    "ok": {"type": "boolean"},
                    "moisture_pct": {"type": "number"},
                    "condition": {"type": "string"},
                    "kd_target": {"type": "number"},
                    "adequacy": {"type": "string"},
                    "notes": {"type": "string"},
                },
            },
            handler=_h_classify_moisture,
        )
    )

    tools.append(
        Tool(
            name="assess_substitution",
            description="Score substitution risk between a claimed and a candidate species.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["claimed_species", "candidate_species"],
                "properties": {
                    "claimed_species": _species_name_schema(),
                    "candidate_species": _species_name_schema(),
                },
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["ok", "risk_level", "species_match"],
                "properties": {
                    "ok": {"type": "boolean"},
                    "risk_level": {"type": "string", "enum": ["none", "low", "medium", "high"]},
                    "species_match": {"type": "boolean"},
                    "reasons": {"type": "array", "items": {"type": "string"}},
                    "claimed_species": {"type": "string"},
                    "candidate_species": {"type": "string"},
                },
            },
            handler=_h_assess_substitution,
        )
    )

    tools.append(
        Tool(
            name="validate_schema",
            description="Validate a payload against a registered sub-skill schema.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["schema_name", "data"],
                "properties": {
                    "schema_name": {"type": "string"},
                    "data": {"type": "object"},
                    "io_type": {"type": "string", "enum": ["input", "output"]},
                },
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["schema_name", "io_type", "valid", "errors"],
                "properties": {
                    "schema_name": {"type": "string"},
                    "io_type": {"type": "string"},
                    "valid": {"type": "boolean"},
                    "errors": {"type": "array", "items": {"type": "string"}},
                },
            },
            handler=_h_validate_schema,
        )
    )

    tools.append(
        Tool(
            name="quality_gate",
            description="Evaluate a single quality gate (U1-U6, G1-G5) against a payload.",
            input_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["gate", "payload"],
                "properties": {"gate": {"type": "string"}, "payload": {"type": "object"}},
            },
            output_schema={
                "$schema": ROOT_SCHEMA,
                "type": "object",
                "required": ["gate", "passed", "errors", "auto_fixed"],
                "properties": {
                    "gate": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "errors": {"type": "array", "items": {"type": "string"}},
                    "auto_fixed": {"type": "boolean"},
                },
            },
            handler=_h_quality_gate,
        )
    )

    return tools


_default_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Return the default registry with all built-in tools registered."""
    global _default_registry
    if _default_registry is None:
        reg = ToolRegistry()
        for tool in _build_tools():
            reg.register(tool)
        _default_registry = reg
    return _default_registry


# CLI --------------------------------------------------------------------
def _cli() -> int:
    import argparse
    import json
    import pathlib

    ap = argparse.ArgumentParser(description="wood-quality-assessment tools registry")
    ap.add_argument("--list", action="store_true", help="list registered tools")
    ap.add_argument("--describe", action="store_true", help="print tool schemas as JSON")
    ap.add_argument(
        "--exec", metavar="TOOL", help="execute a tool (use --input or --input-file for inputs)"
    )
    ap.add_argument("--input", metavar="JSON", help="JSON string of inputs for --exec")
    ap.add_argument("--input-file", metavar="PATH", help="path to a JSON file of inputs for --exec")
    args = ap.parse_args()

    reg = get_registry()
    if args.list:
        for t in reg.list_tools():
            print(t)
        return 0
    if args.describe:
        print(json.dumps(reg.describe(), indent=2))
        return 0
    if args.exec:
        if args.input_file:
            inputs = json.loads(pathlib.Path(args.input_file).read_text(encoding="utf-8-sig"))
        elif args.input:
            inputs = json.loads(args.input)
        else:
            inputs = {}
        result = reg.execute(args.exec, inputs)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0 if result.ok else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
