# Wood Quality Assessment - System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User Invocation Layer                        │
│                   /wood-quality-assessment [query]                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Language Detection                           │
│                    Vietnamese / English / Other                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Main Harness (skills/main.md)                    │
│                    ┌───────────────────────────┐                    │
│                    │   Pre-Flight Hooks         │                    │
│                    │   - Log invocation         │                    │
│                    │   - Create execution state │                    │
│                    └───────────────────────────┘                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Step 1      │   │   Step 2      │   │   Step 3      │
│ sub-gather-   │   │ sub-evidence- │   │ sub-grain-    │
│ requirements  │   │ collector     │   │ image-analysis│
│               │   │               │   │               │
│ Intake: 9     │   │ Fetch:        │   │ Analyze:      │
│ fields        │   │ - CITES       │   │ - IAWA codes  │
│ - Species     │   │ - IUCN        │   │ - Vessels     │
│ - Photos      │   │ - Anatomy     │   │ - Rays        │
│ - Moisture    │   │ - Physical    │   │ - Parenchyma  │
│ - Density     │   │ - Legality    │   │ - Rings       │
│ - Origin      │   │               │   │ - Color       │
│ - Use         │   │               │   │ - Genus ID    │
│ - Market      │   │               │   │ - Confidence  │
│ - Language    │   │               │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Step 4      │   │   Step 5      │   │   Step 6      │
│ sub-physical- │   │ sub-authenti- │   │ sub-knowledge-│
│ property-     │   │ city-compli-  │   │ updater       │
│ analysis      │   │ ance          │   │               │
│               │   │               │   │ Query:        │
│ Assess:       │   │ Detect:       │   │ - SKB         │
│ - MC%         │   │ - Species     │   │ - Citations   │
│ - Condition   │   │   match       │   │ - Tiers       │
│ - Density     │   │ - Substitutes │   │ - Evidence    │
│ - Drying      │   │ - CITES       │   │ - Gaps        │
│ - Stability   │   │ - IUCN        │   │               │
│ - Grade       │   │ - Legality    │   │               │
│ - Suitability │   │ - Origin      │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Step 7      │
                    │ sub-quality-  │
                    │ advisor      │
                    │               │
                    │ Synthesize:   │
                    │ - Verdict     │
                    │ - Grade       │
                    │ - Scenarios   │
                    │ - Risks       │
                    │ - Evidence    │
                    │ - Actions     │
                    └───────┬───────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Quality Gate System                              │
│                    ┌───────────────────────────┐                    │
│                    │   11 Quality Gates        │                    │
│                    │   U1-U6 (Universal)       │                    │
│                    │   G1-G5 (Domain)          │                    │
│                    │   - Auto-fix enabled       │                    │
│                    │   - Max 2 retries          │                    │
│                    │   - Degradation on fail   │                    │
│                    └───────────────────────────┘                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Output Generation                               │
│                    ┌───────────────────────────┐                    │
│                    │   Apply Template          │                    │
│                    │   Format Sections          │                    │
│                    │   Add Citations            │                    │
│                    │   Include Disclosure        │                    │
│                    └───────────────────────────┘                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Post-Execution Hooks                           │
│                    ┌───────────────────────────┐                    │
│                    │   - Log completion         │                    │
│                    │   - Persist state          │                    │
│                    │   - Emit events            │                    │
│                    │   - Track metrics          │                    │
│                    └───────────────────────────┘                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Final Report                                 │
│           Structured, Evidenced, Risk-Disclosed Output               │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Data Sources                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ CITES    │  │  IUCN    │  │InsideWood│  │  Wood    │       │
│  │ Checklist│  │ Red List │  │ Database │  │ Database │       │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└────────┼─────────────┼─────────────┼─────────────┼──────────────┘
         │             │             │             │
         │  ┌──────────┴─────────────┴─────────────┴───┐        │
         │  │              WebFetch / WebSearch         │        │
         │  └───────────────────┬───────────────────────┘        │
         │                      │                                │
         ▼                      ▼                                │
┌────────────────────────────────────────────────────────────────┤
│                 Fallback Chain (on failure)                     │
│  Live Source → Cached → SKB → Generic → Limitation Flag       │
└────────────────────────────────────────────────────────────────┘
```

## State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                    State Manager                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Execution State (per assessment)                        │    │
│  │  - execution_id: SHA256 hash                            │    │
│  │  - skill_name: wood-quality-assessment                  │    │
│  │  - status: pending|running|completed|failed             │    │
│  │  - current_step: 0-8                                     │    │
│  │  - gates_passed: []                                      │    │
│  │  - gates_failed: []                                     │    │
│  │  - degradation_level: 0-4                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Persistence (.state/skill_state.json)                    │    │
│  │  - Automatic save on state change                         │    │
│  │  - Load on system initialization                         │    │
│  │  - Thread-safe with RLock                                │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Hooks System

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hooks Emission Flow                           │
│                                                                 │
│  before_skill_invoke ──► skill_execution() ──► after_skill_invoke
│         │                                                  │     │
│         │                                            on_error   │
│         │                                                  │     │
│         ▼                                                  ▼     │
│  ┌─────────────┐                                   ┌──────────┐  │
│  │ Log invoke  │                                   │Log error │  │
│  │ Create state│                                   │Update    │  │
│  │ Emit event  │                                   │status    │  │
│  └─────────────┘                                   └──────────┘  │
│                                                                 │
│  before_quality_gate ──► quality_gate() ──► after_quality_gate │
│         │                                                  │     │
│         ▼                                                  ▼     │
│  ┌─────────────┐                                   ┌──────────┐  │
│  │ Log gate    │                                   │Log result│  │
│  │ Check state │                                   │Track time│  │
│  └─────────────┘                                   └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Layer                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  config/settings.yaml                                    │    │
│  │  - System metadata                                       │    │
│  │  - Feature flags                                         │    │
│  │  - LLM parameters                                        │    │
│  │  - Tool settings                                         │    │
│  │  - Quality gate config                                   │    │
│  │  - Performance optimization                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  config/schemas/tool_schemas.json                       │    │
│  │  - Tool input/output schemas                            │    │
│  │  - Sub-skill schemas                                    │    │
│  │  - Quality gate validation schemas                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Knowledge Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              Knowledge Update Pipeline                           │
│                                                                 │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │ Academic   │    │   News     │    │ Standards  │            │
│  │ Sources    │    │   RSS      │    │   Docs     │            │
│  │ (Semantic  │    │   Feeds    │    │   (Crawl)  │            │
│  │ Scholar)   │    │            │    │            │            │
│  └──────┬─────┘    └──────┬─────┘    └──────┬─────┘            │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│              ┌──────────────────────────┐                       │
│              │  knowledge_updater.py    │                       │
│              │  - Fetch with retry      │                       │
│              │  - SHA256 dedup          │                       │
│              │  - Composite scoring     │                       │
│              │  - Structured logging    │                       │
│              └───────────┬──────────────┘                       │
│                          │                                     │
│                          ▼                                     │
│              ┌──────────────────────────┐                       │
│              │  SECOND-KNOWLEDGE-      │                       │
│              │  BRAIN.md (append)      │                       │
│              │  - Section 1-7          │                       │
│              │  - Tiered citations     │                       │
│              │  - Update log           │                       │
│              └──────────────────────────┘                       │
│                                                                 │
│  Schedule: Weekly academic (Mon 8am) + Daily news (7am)        │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling & Degradation

```
┌─────────────────────────────────────────────────────────────────┐
│              Graceful Degradation Levels                         │
│                                                                 │
│  Level 0: All operational                                       │
│  ├─ Live sources available                                     │
│  ├─ All gates passing                                          │
│  └─ Full confidence output                                      │
│                                                                 │
│  Level 1: Cached fallback                                       │
│  ├─ Live sources failed, using cached                          │
│  ├─ All gates passing                                          │
│  └─ Note: "Using cached data"                                 │
│                                                                 │
│  Level 2: Knowledge base fallback                              │
│  ├─ Cache failed, using SKB                                    │
│  ├─ Minor gates may fail                                       │
│  └─ Note: "Using knowledge base"                               │
│                                                                 │
│  Level 3: Generic defaults                                      │
│  ├─ SKB incomplete, using generic                              │
│  ├─ Some gates failing                                         │
│  └─ Note: "Using generic defaults"                             │
│                                                                 │
│  Level 4: Critical failure                                      │
│  ├─ No reliable data source                                    │
│  ├─ Multiple gates failing                                     │
│  └─ LIMITATION banner: "Analysis severely limited"             │
└─────────────────────────────────────────────────────────────────┘
```

---

**Architecture Version:** 1.0.0
**Last Updated:** 2026-07-16
