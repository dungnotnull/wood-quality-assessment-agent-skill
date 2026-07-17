---
name: skill-registry
description: Comprehensive documentation for the wood-quality-assessment skill registry - including registration, resolution, execution, validation, input/output schemas, hooks system, and modular architecture.
---

# Wood Quality Assessment - Skill Registry Documentation

## Executive Summary

The **wood-quality-assessment** skill registry implements a flexible, production-grade architecture for wood quality and forestry standards compliance analysis. This registry enables dynamic skill discovery, resolution, execution, and validation through a standardized system of hooks, schemas, and modular components.

---

## Architecture Overview

```
wood-quality-assessment/
+-- SKILL.md                    # This file - skill registry documentation
+-- config/                     # Configuration management
|   +-- settings.yaml           # System-wide settings and feature flags
|   `-- schemas/                # JSON schemas for tools and validation
|       `-- tool_schemas.json   # Tool input/output schemas (static catalog)
+-- scripts/                    # Automation and utilities
|   +-- hooks_system.py         # Lifecycle hooks and state management
|   +-- skill_loader.py         # Dynamic skill discovery and loading
|   +-- validator.py            # Schema validation and quality gate checking
|   +-- reference_data.py       # Grounding layer: species/CITES/IUCN lookups
|   +-- tools_registry.py       # Executable tool definitions (schemas + handlers)
|   +-- seed_reference_data.py  # (Re)generates the references/*.json datasets
|   `-- setup.py                # Installation, validation, health report
+-- references/                 # Domain knowledge and templates (real grounding data)
|   +-- templates/              # Output templates for reports
|   +-- species_database.json   # 28 curated species profiles (anatomy/density/MC)
|   +-- cites_listings.json     # 16 CITES appendix listings (I/II/III)
|   `-- iucn_status.json        # 28 IUCN Red List assessments
+-- assets/                     # Static resources
|   +-- diagrams/               # System architecture and flow diagrams
|   +-- examples/               # Sample inputs and outputs (sample_input.json, sample_output.md)
|   `-- schemas/                # Visual schema representations
+-- skills/                     # Skill implementations
|   +-- main.md                 # Primary harness orchestrator (Step 1.5 routing)
|   +-- sub-router.md           # Chain-of-thought routing sub-skill
|   `-- sub-*.md                # 7 specialized analysis sub-skills
`-- tools/                      # Python utilities and tests
    +-- knowledge_updater.py     # Knowledge crawl pipeline
    +-- run_test_scenarios.py   # Test orchestrator (251 checks)
    +-- test_knowledge_updater.py # 20 unit tests
    +-- test_reference_data.py   # 52 unit tests (grounding layer)
    `-- test_tools_registry.py   # 52 unit tests (tools registry)
```

---

## Skill Registration

### Registration Protocol

Skills are registered through YAML frontmatter in `.md` files:

```yaml
---
name: skill-name
description: When to trigger this skill + what it does
---
```

### Registration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier (kebab-case) |
| `description` | string | Yes | Triggering description (what it does + when to use) |

### Skill Types

1. **Main Harness Skills**: Primary orchestrators (e.g., `wood-quality-assessment`)
2. **Sub-Skills**: Specialized components (e.g., `sub-gather-requirements`)
3. **Utility Skills**: Support functions (e.g., `skill-registry`, `hooks`)

### Registration Discovery

The skill loader automatically discovers skills in:

1. `skills/` directory (recursive scan)
2. `skills/sub-skills/` directory (optional subdirectory)
3. Registered paths in `config/settings.yaml`

### Registration Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Skill Registration",
  "type": "object",
  "required": ["name", "description"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "minLength": 3,
      "maxLength": 64
    },
    "description": {
      "type": "string",
      "minLength": 20,
      "maxLength": 200
    }
  }
}
```

---

## Skill Resolution

### Resolution Process

When a skill is invoked, the resolver follows these steps:

1. **Parse Invocation**: Extract skill name from `Skill("skill-name")` or `/skill-name` command
2. **Lookup Registry**: Find registered skill by name
3. **Load Skill File**: Read corresponding `.md` file from `skills/` directory
4. **Validate Frontmatter**: Ensure YAML is valid and required fields present
5. **Cache**: Store in memory for subsequent invocations (TTL: 3600s)

### Resolution Fallback

If direct resolution fails:

1. Try fuzzy matching (Levenshtein distance ≤ 2)
2. Try alias lookup (defined in skill metadata)
3. Return error with suggestions

### Resolution Caching

- **In-Memory Cache**: LRU cache with 100-entry limit
- **Cache TTL**: 3600 seconds (1 hour)
- **Cache Invalidation**: On skill file modification (monitored via file watcher)

---

## Skill Execution

### Execution Protocol

Skills are executed through a standardized workflow:

```
[Invocation] → [Pre-Hooks] → [Context Setup] → [Skill Body] → [Post-Hooks] → [Quality Gates] → [Output]
```

### Execution Context

Each skill execution receives a context object:

```python
@dataclass
class SkillExecutionContext:
    skill_name: str
    execution_id: str
    inputs: Dict[str, Any]
    config: Dict[str, Any]
    state: SkillState
    hooks: HookRegistry
    tools: ToolRegistry
```

### Execution Hooks

Pre-execution hooks:
- `before_skill_invoke`: Called before skill execution starts
- `state_change`: Called when execution state changes

Post-execution hooks:
- `after_skill_invoke`: Called after skill execution completes
- `on_skill_error`: Called on execution errors

Quality gate hooks:
- `before_quality_gate`: Called before each quality gate
- `after_quality_gate`: Called after each quality gate

### Execution Error Handling

Errors are handled through graceful degradation:

**Level 0**: All systems operational
**Level 1**: Live sources failed, using cached
**Level 2**: Cache failed, using knowledge base
**Level 3**: Knowledge base incomplete, using generic defaults
**Level 4**: Critical failure, explicit limitation banner

---

## Routing & Tools Registry

### Chain-of-Thought Router (`skills/sub-router.md`)

`main.md` invokes `sub-router` as **Step 1.5** (between intake and evidence
collection). The router reads the `analysis_type` and missing-input inventory
from Step 1, performs explicit chain-of-thought planning, and emits an ordered
execution `plan[]` (steps 2-7 with `run`/`skip` actions, rationales, a
per-step degradation forecast, and limitation notes). This is the flexible
dispatch layer: the pipeline adapts to `combined` / `anatomy_only` /
`physical_only` / `compliance_only` instead of always running every sub-skill.

Router quality gates: **R1** (routing completeness), **R2** (rationale for
every skip), **R3** (degradation coverage for missing inputs), **R4** (no
silent `analysis_type` fallback).

### Executable Tools Registry (`scripts/tools_registry.py`)

The static catalog `config/schemas/tool_schemas.json` declares tool contracts;
`scripts/tools_registry.py` makes them **executable**. Each tool binds a JSON
Schema (Draft 7) input+output contract to a deterministic, offline-safe Python
handler, all backed by the grounding layer in `scripts/reference_data.py`.

| Tool | Description |
|------|-------------|
| `lookup_species` | Fuzzy-resolve (Levenshtein <=2) a free-form species name to its profile |
| `lookup_cites` | Genus-aware CITES appendix lookup with access date |
| `lookup_iucn` | Genus-aware IUCN Red List category lookup |
| `compare_density` | Compare measured air-dry density to the species benchmark |
| `classify_moisture` | Classify a moisture reading against the species KD target |
| `assess_substitution` | Score substitution risk between claimed and candidate species |
| `validate_schema` | Validate an arbitrary payload against a registered sub-skill schema |
| `quality_gate` | Evaluate a single quality gate (U1-U6, G1-G5) |

```python
from scripts.tools_registry import get_registry

reg = get_registry()
result = reg.execute("lookup_cites", {"species": "Dalbergia oliveri"})
# result.to_dict() -> {"ok": True, "output": {"appendix": "II", ...}, "errors": [], ...}
```

Execution guarantees: inputs and outputs are schema-validated; handler
exceptions are caught and returned as structured `errors` (the registry never
raises to callers — graceful degradation by construction).

## Input/Output Validation

### Validation Schema

All inputs and outputs are validated against JSON schemas defined in `config/schemas/tool_schemas.json`.

### Input Validation

For each tool/skill, the validator checks:

1. **Required Fields**: All required fields present
2. **Type Checking**: Field types match schema
3. **Value Constraints**: Enums, ranges, patterns respected
4. **Custom Validation**: Domain-specific rules

### Output Validation

Outputs are validated for:

1. **Required Sections**: All mandatory sections present
2. **Data Types**: Output fields match expected types
3. **Format Compliance**: Follows template structure
4. **Quality Gates**: All quality gates passed

### Validation Example

```python
from scripts.validator import validate_output

result = {
    "verdict": "Authentic",
    "grade": "A",
    "disclosure": "Analysis based on provided samples..."
}

is_valid, errors = validate_output(
    result,
    schema_name="sub-quality-advisor",
    output_type="output"
)

if not is_valid:
    print(f"Validation failed: {errors}")
```

---

## Quality Gates

### Universal Gates (U1-U6)

| Gate | Description | Validation Criteria |
|------|-------------|---------------------|
| U1 | Source Citation Count | ≥3 sources, ≥1 academic/authoritative |
| U2 | Risk Disclosure | Disclosure before verdict |
| U3 | Evidence Hierarchy | Tier stated per source |
| U4 | Language Consistency | Output matches user language |
| U5 | Output Template | All required sections present |
| U6 | Claim Traceability | Claims cited or flagged |

### Domain Gates (G1-G5)

| Gate | Description | Validation Criteria |
|------|-------------|---------------------|
| G1 | Species Confidence | Confidence level stated with justification |
| G2 | Physical Benchmark | Moisture/density compared to benchmarks |
| G3 | CITES/IUCN Verification | Status checked with access dates |
| G4 | Legality Assessment | Market-specific requirements assessed |
| G5 | Verdict Category | One of 5 defined categories |

### Gate Execution

1. **Check**: Validate gate criteria against output
2. **Auto-Fix**: Attempt automatic fixes (if enabled)
3. **Retry**: Recheck after auto-fix (max 2 retries)
4. **Fail**: Mark gate as failed and log

---

## Hooks System

### Hook Points

| Hook Point | When Triggered | Parameters |
|------------|----------------|------------|
| `before_skill_invoke` | Before skill execution | `{skill_name, execution_id}` |
| `after_skill_invoke` | After skill execution | `{skill_name, execution_id, duration_ms, success}` |
| `on_skill_error` | On execution error | `{skill_name, execution_id, error, error_type}` |
| `before_quality_gate` | Before gate check | `{gate, execution_id, skill_name}` |
| `after_quality_gate` | After gate check | `{gate, execution_id, skill_name, duration_ms}` |
| `state_change` | On state update | `{execution_id, skill_name, changes}` |
| `degradation_triggered` | On degradation level change | `{execution_id, skill_name, degradation_level, reason}` |
| `knowledge_update` | On knowledge base update | `{section, entries_added, source}` |

### Hook Registration

```python
from scripts.hooks_system import hook, HookPoint

@hook(HookPoint.AFTER_SKILL_INVOKE)
def custom_hook(event):
    print(f"Skill {event.skill_name} completed in {event.data.get('duration_ms')}ms")
```

### Built-in Hooks

- **Logging Hooks**: Log all skill invocations, errors, and state changes
- **State Persistence**: Persist state changes to disk
- **Performance Monitoring**: Track execution times and token usage
- **Degradation Alerts**: Alert when degradation level changes

---

## State Management

### State Schema

```json
{
  "skill_name": "string",
  "execution_id": "string (SHA256)",
  "started_at": "ISO 8601 datetime",
  "status": "pending|running|completed|failed",
  "current_step": "integer (0-8)",
  "total_steps": "integer (default 8)",
  "gates_passed": ["string array"],
  "gates_failed": ["string array"],
  "degradation_level": "integer (0-4)",
  "metadata": {}
}
```

### State Persistence

States are persisted to `.state/skill_state.json` after:

1. Skill execution completion
2. Quality gate failure
3. Degradation level change
4. Critical errors

### State Loading

States are loaded on:

1. System initialization
2. Skill loader startup
3. Explicit state manager load() call

---

## Modular Directories

### `/config`

Configuration management with type-safe settings.

**Files:**
- `settings.yaml`: System-wide configuration
- `schemas/tool_schemas.json`: JSON schemas for validation

**Purpose:** Centralized configuration with feature flags, LLM parameters, tool settings, quality gate configuration, and monitoring thresholds.

### `/scripts`

Automation utilities and helper scripts.

**Files:**
- `hooks_system.py`: Lifecycle hooks and state management
- `skill_loader.py`: Dynamic skill discovery and loading
- `validator.py`: Schema validation and quality gate checking
- `reference_data.py`: Grounding layer — loads the reference JSON datasets and exposes type-safe, fuzzy-tolerant lookups (`resolve_species`, `get_cites`, `get_iucn`, `compare_density`, `classify_moisture`, `substitution_risk`)
- `tools_registry.py`: Executable tool registry — binds JSON Schema contracts to deterministic Python handlers (`lookup_species`, `lookup_cites`, `lookup_iucn`, `compare_density`, `classify_moisture`, `assess_substitution`, `validate_schema`, `quality_gate`)
- `seed_reference_data.py`: Idempotent generator that (re)writes the three `references/*.json` datasets and cross-checks key integrity
- `setup.py`: Installation, validation, and structured health report

**Purpose:** Production-grade automation with structured logging, error handling, type hints, and graceful degradation.

### `/references`

Curated domain knowledge and templates used for RAG/agent grounding. These are
**real datasets** (not placeholders), regenerated by `scripts/seed_reference_data.py`
and queried by `scripts/reference_data.py`.

**Files:**
- `templates/output_template.md`: Standard output format (14-section report template)
- `species_database.json`: 28 curated species profiles — family, wood type, porosity, density range, moisture benchmarks, T/R shrinkage, IAWA features, heartwood color, native origin, uses, documented substitution risks
- `cites_listings.json`: 16 CITES appendix listings (Appendix I/II/III) with annotations, listing dates, and notes
- `iucn_status.json`: 28 IUCN Red List assessments (category, trend, assessed year)

**Integrity:** every species `cites_key`/`iucn_key` cross-resolves to the CITES/IUCN files (validated by `setup.py` and unit tests). Live CITES/IUCN access dates must still come from checklist.cites.org / iucnredlist.org; these files are the offline grounding + fallback layer.

### `/assets`

Static resources and documentation.

**Files:**
- `diagrams/system_architecture.md`: System architecture and harness flow documentation
- `examples/sample_input.json`: Example assessment request payload
- `examples/sample_output.md`: Golden example output report (Scenario 1 — Teak, Vietnamese) demonstrating all 11 quality gates passing

**Purpose:** Visual aids and examples for users and developers.

---

## Tool Schemas

### Schema Organization

Tool schemas are organized in `config/schemas/tool_schemas.json`:

```json
{
  "toolSchemas": {
    "WebSearch": {...},
    "WebFetch": {...},
    "ImageAnalysis": {...},
    "Skill": {...},
    "Read": {...},
    "Write": {...},
    "Bash": {...}
  },
  "subSkillSchemas": {
    "sub-gather-requirements": {...},
    "sub-evidence-collector": {...},
    "sub-grain-image-analysis": {...},
    "sub-physical-property-analysis": {...},
    "sub-authenticity-compliance": {...},
    "sub-knowledge-updater": {...},
    "sub-quality-advisor": {...}
  },
  "qualityGateSchemas": {
    "U1": {...},
    "U2": {...},
    "U3": {...},
    "U4": {...},
    "U5": {...},
    "U6": {...},
    "G1": {...},
    "G2": {...},
    "G3": {...},
    "G4": {...},
    "G5": {...}
  }
}
```

### Schema Validation

Schemas are validated using JSON Schema Draft 7:

```python
import jsonschema
from config.schemas.tool_schemas import load_schema

schema = load_schema("sub-quality-advisor", "output")
jsonschema.validate(instance=result, schema=schema)
```

---

## Performance Optimization

### Context Window Management

- **Token Budgeting**: Limit to 80% of context window
- **Compression**: Enable compression for large outputs
- **Caching**: Cache tool results with 3600s TTL

### Token Usage Tracking

Track token usage per:

- Skill execution
- Tool invocation
- Quality gate check
- Total session

### Performance Metrics

Monitor:

- **Execution Time**: Per skill and per gate
- **Token Efficiency**: Tokens per result
- **Cache Hit Rate**: Percentage of cached results
- **Error Rate**: Percentage of failed executions

---

## Security Considerations

### Input Validation

- URL validation before web fetches
- Input sanitization for all user inputs
- Rate limiting on external API calls

### Output Sanitization

- HTML entity encoding
- Script tag removal
- XSS prevention

### Audit Logging

All sensitive operations are logged:

- Skill invocations
- External API calls
- State changes
- Errors and failures

---

## Troubleshooting

### Common Issues

**Issue**: Skill not found
- **Solution**: Check skill registration in `skills/` directory
- **Verify**: YAML frontmatter is valid

**Issue**: Validation failed
- **Solution**: Check input/output against schemas
- **Verify**: All required fields present

**Issue**: Quality gate failed
- **Solution**: Enable auto-fix in `config/settings.yaml`
- **Verify**: Gate criteria are met

**Issue**: State not persisting
- **Solution**: Check `.state/` directory exists and is writable
- **Verify**: File permissions are correct

### Debug Mode

Enable debug mode in `config/settings.yaml`:

```yaml
debug:
  verbose_logging: true
  print_raw_outputs: true
  skip_quality_gates: false
```

---

## Extension Guide

### Adding a New Skill

1. Create `skills/new-skill.md` with YAML frontmatter
2. Define skill workflow and tools
3. Add output schema to `config/schemas/tool_schemas.json`
4. Register quality gates if needed
5. Test with example inputs
6. Document in registry

### Adding a New Hook Point

1. Define in `scripts/hooks_system.py`:
   ```python
   class HookPoint(Enum):
       NEW_HOOK_POINT = "new_hook_point"
   ```

2. Implement emission logic
3. Document in registry
4. Add tests

### Adding a New Tool Schema

1. Add to `config/schemas/tool_schemas.json`
2. Define input and output schemas
3. Add validation logic
4. Test schema validation

---

## API Reference

### Skill Loader

```python
from scripts.skill_loader import SkillLoader, load_skill

loader = SkillLoader()
skill = loader.load("wood-quality-assessment")
```

### Validator

```python
from scripts.validator import validate_input, validate_output

valid, errors = validate_input(data, "sub-gather-requirements")
valid, errors = validate_output(data, "sub-quality-advisor")
```

### Hooks System

```python
from scripts.hooks_system import (
    hook, HookPoint,
    skill_execution, quality_gate,
    emit_state_change
)

@hook(HookPoint.AFTER_SKILL_INVOKE)
def custom_hook(event):
    pass
```

### State Manager

```python
from scripts.hooks_system import state_manager

state = state_manager.create_state("skill-name", 8)
state_manager.update_state(execution_id, status="running")
state_manager.persist()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-10 | Initial production release |
| 1.1.0 | 2026-07-17 | Reference grounding data (species/CITES/IUCN), tools registry with executable handlers, chain-of-thought router, example output, grounding + tools unit tests |

---

## References

- `config/settings.yaml` - System configuration
- `config/schemas/tool_schemas.json` - Tool and quality gate schemas
- `scripts/hooks_system.py` - Hooks implementation
- `skills/main.md` - Main harness skill
- `PROJECT-detail.md` - Full project specification

---

**Document Version**: 1.1.0
**Last Updated**: 2026-07-17
**Maintained By**: wood-quality-assessment contributors
