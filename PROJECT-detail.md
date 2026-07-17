# PROJECT-detail.md — Skill 159: wood-quality-assessment

## Executive Summary

`wood-quality-assessment` is a professional-grade harness for Claude Code targeting the
**Wood Quality & Forestry-Standards Compliance** domain. It transforms Claude into a domain-expert that delivers
structured, evidence-backed outputs by combining real-time data aggregation,
recognized domain methods, and academic research into a single orchestrated
workflow ending in a risk/limitation-disclosed recommendation.

---

## Problem Statement

Practitioners in this domain face three structural gaps:
1. **Data fragmentation**: authoritative data scattered across sources.
2. **Methodology gaps**: most advice lacks systematic, evidence-graded methods.
3. **No self-improvement**: static tools don't learn from new research.

This skill addresses all three via real-time aggregation, professional
frameworks, and a continuously-updated knowledge crawl pipeline.

---

## Target Users & Use Cases

| User | Trigger Example | Skill Response |
|------|----------------|----------------|
| Practitioner | "Analyze Wood Quality & Forestry-Standards Compliance case X" | Full evidenced report |
| Researcher | "What methods apply to Y?" | Method-grounded guidance with citations |
| Decision-maker | "Assess risk/feasibility of Z" | Risk-disclosed assessment with scenarios |
| Learner | "Explain method M in this domain" | Educational framing with evidence |

---

## Harness Architecture

```
USER INPUT
    │
    ▼
[main.md — wood-quality-assessment]
    │
    ├─► sub-gather-requirements.md  → Clarify the object under assessment (claimed species, sample photos, moisture reading & method, density if available, claimed origin, intended use, market/region) and language before any analysis.
    ├─► sub-evidence-collector.md  → Fetch authoritative reference data for the candidate species: CITES Appendix status, IUCN status, FSC/PEFC rules, EUTR/Lacey/VNFOREST legality requirements, and a reference grain/anatomy atlas entry (InsideWood, Wood Database).
    ├─► sub-grain-image-analysis.md  → Analyze provided grain/figure imagery using IAWA hardwood/softwood feature lists to estimate vessel arrangement, ray width, parenchyma pattern, ring density and boundaries, and color — yielding a candidate species/genus group.
    ├─► sub-physical-property-analysis.md  → Interpret moisture content (MC%) and density (kg/m3) against species benchmarks and standards (ISO 3129, ASTM D143) to assess drying adequacy, dimensional stability and mechanical-grade suitability.
    ├─► sub-authenticity-compliance.md  → Detect adulteration/substitution/mislabeling and assess legality: compare detected candidate species vs claimed species, and check candidates against CITES Appendices, IUCN status, and national bans (EUTR/Lacey/VNFOREST) and origin-mismatch illegal-logging risk.
    ├─► sub-knowledge-updater.md  → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative wood-anatomy, drying, density, and CITES/standards evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
    ├─► sub-quality-advisor.md  → Synthesize all prior analysis into a risk-disclosed verdict and grade with a full evidence chain and remediation actions.

    └─► [QUALITY GATE — main.md]
            ✓ Claims cited to sources
            ✓ Disclosure included
            ✓ Evidence hierarchy respected
            ✓ Output formatted per template
```

---

## Full Sub-Skill Catalog

### 1. `sub-gather-requirements.md`
- **Purpose:** Clarify the object under assessment (claimed species, sample photos, moisture reading & method, density if available, claimed origin, intended use, market/region) and language before any analysis.
- **Role:** intake specialist for a timber & handicraft quality lab
- **Inputs:** Raw user message + any attached photos/measurements.
- **Outputs:** Structured requirements: {claimed_species, sample_photos[], moisture_pct, moisture_method, density_kgm3, claimed_origin, intended_use, market_region, language}.
- **Tools:** - Conversation only (no external tools)
- **Quality Gate:** At least one claimed species OR a usable sample photo confirmed before proceeding.

### 2. `sub-evidence-collector.md`
- **Purpose:** Fetch authoritative reference data for the candidate species: CITES Appendix status, IUCN status, FSC/PEFC rules, EUTR/Lacey/VNFOREST legality requirements, and a reference grain/anatomy atlas entry (InsideWood, Wood Database).
- **Role:** forestry-data librarian
- **Inputs:** Claimed species / candidate species list from Step 1.
- **Outputs:** Evidence bundle: {cites_status, iucn_status, legality_requirements, anatomy_reference, physical_reference_benchmarks}.
- **Tools:** - WebSearch, WebFetch (CITES Checklist, IUCN, InsideWood, Wood Database, VNFOREST)
- Read (SECOND-KNOWLEDGE-BRAIN.md for cached benchmarks)
- **Quality Gate:** CITES and IUCN status retrieved for at least the claimed species; anatomy reference retrieved or limitation flagged.

### 3. `sub-grain-image-analysis.md`
- **Purpose:** Analyze provided grain/figure imagery using IAWA hardwood/softwood feature lists to estimate vessel arrangement, ray width, parenchyma pattern, ring density and boundaries, and color — yielding a candidate species/genus group.
- **Role:** wood anatomist
- **Inputs:** Sample photos (end-grain, tangential, radial if available) + anatomy reference from Step 2.
- **Outputs:** Anatomy scorecard: {vessel_arrangement, ray_width, parenchyma_pattern, ring_density_per_mm, ring_boundaries_distinct, color, candidate_species_group, confidence, observed_vs_reference_mismatches}.
- **Tools:** - Image analysis (vision) over provided photos
- Read (SECOND-KNOWLEDGE-BRAIN.md IAWA feature lists)
- **Quality Gate:** Anatomy scorecard states an explicit confidence level and lists observed-vs-reference mismatches.

### 4. `sub-physical-property-analysis.md`
- **Purpose:** Interpret moisture content (MC%) and density (kg/m3) against species benchmarks and standards (ISO 3129, ASTM D143) to assess drying adequacy, dimensional stability and mechanical-grade suitability.
- **Role:** wood-technology engineer
- **Inputs:** Moisture reading + method, density (if provided), physical benchmarks from Step 2.
- **Outputs:** Physical scorecard: {moisture_pct, moisture_condition (green/FAD/AD/KD), density_vs_benchmark, shrinkage_estimate, drying_adequacy, mechanical_grade_indication}.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md benchmarks & drying theory)
- Arithmetic reasoning
- **Quality Gate:** Moisture & density each reported with measurement method and a species benchmark comparison.

### 5. `sub-authenticity-compliance.md`
- **Purpose:** Detect adulteration/substitution/mislabeling and assess legality: compare detected candidate species vs claimed species, and check candidates against CITES Appendices, IUCN status, and national bans (EUTR/Lacey/VNFOREST) and origin-mismatch illegal-logging risk.
- **Role:** timber-legality & anti-fraud analyst
- **Inputs:** Anatomy scorecard (Step 3), physical scorecard (Step 4), evidence bundle (Step 2), claimed species & origin (Step 1).
- **Outputs:** Compliance & authenticity verdict inputs: {species_match, substitution_risk, cites_violation, iucn_concern, legality_status, origin_consistency, recommended_followup_tests}.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md CITES & legality section)
- Reasoning over the evidence bundle
- **Quality Gate:** CITES & IUCN status explicitly checked for BOTH detected and claimed species; follow-up tests recommended when inconclusive.

### 6. `sub-knowledge-updater.md`
- **Purpose:** Query SECOND-KNOWLEDGE-BRAIN.md for authoritative wood-anatomy, drying, density, and CITES/standards evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
- **Role:** research librarian for wood science & forestry standards
- **Inputs:** Topic keywords from the current analysis (e.g., 'IAWA hardwood features', 'CITES Dalbergia', 'wood density benchmark').
- **Outputs:** 3-5 knowledge-base citations with Tier labels + flagged knowledge gaps.
- **Tools:** - Read (SECOND-KNOWLEDGE-BRAIN.md)
- WebSearch (gap-fill, max 2 queries)
- **Quality Gate:** At least 1 academic/authoritative source surfaced; evidence coverage rating provided.

### 7. `sub-quality-advisor.md`
- **Purpose:** Synthesize all prior analysis into a risk-disclosed verdict and grade with a full evidence chain and remediation actions.
- **Role:** senior wood-quality & compliance advisor
- **Inputs:** Anatomy scorecard, physical scorecard, compliance verdict inputs, knowledge-base evidence.
- **Outputs:** Verdict (one of 5 categories) + grade + scenario reasoning + key risks + evidence chain + remediation + mandatory disclosure.
- **Tools:** - Reasoning / synthesis
- Skill('sub-knowledge-updater') optional for evidence validation
- **Quality Gate:** Verdict is exactly one of the 5 declared categories; disclosure appears before the verdict.


---

## Skill File Format Specification

```markdown
---
name: {skill-name}
description: {one-line summary}
---
## Role & Persona
## Workflow (Harness Flow)
## Sub-skills Available   (main.md only)
## Tools
## Output Format
## Quality Gates
```

---

## E2E Execution Flow

```
1. User invokes /wood-quality-assessment [query]
2. main.md → sub-gather-requirements → structured requirements
3. sub-evidence-collector → data bundle
4. core analysis sub-skills → scorecard / signal set
5. sub-knowledge-updater → academic evidence entries
6. sub-advisor/synthesizer → final draft
7. main.md Quality Gate → verify, auto-fix, deliver
```

**Error handling:** primary sources fail → fallback chain → knowledge base →
explicit limitation flag; never silently proceed with stale data.

---

## SECOND-KNOWLEDGE-BRAIN Integration

- **Sources crawled:** academic databases + domain RSS + standards docs
- **Crawl config:** `KNOWLEDGE_CONFIG` in `tools/knowledge_updater.py`
- **Dedup:** SHA256 of DOI/URL
- **Scoring:** recency + keyword relevance + citation count

---

## Quality Gates Definition

Universal gates U1–U6 (see library SKILL-STANDARD.md) plus the domain gates
defined in `skills/main.md`: G1, G2, G3, G4, G5

---

## Test Scenarios

See `tests/test-scenarios.md` for 5+ concrete scenario tests.

---

## Key Design Decisions

1. Domain sub-skills kept separate (distinct methods/data).
2. Authoritative domain sources as primary; global fallback secondary.
3. Disclosure enforced at the quality-gate level, not optional.
4. SECOND-KNOWLEDGE-BRAIN as living memory updated by crawl pipeline.
5. Graceful degradation to knowledge base with explicit limitation flags.

---

## Idea (Vietnamese)

> Tạo skill thẩm định chất lượng gỗ và đồ gỗ mỹ nghệ nguyên khối, dựa trên việc phân tích hình ảnh vân gỗ, độ ẩm, mật độ vòng năm và liên tục cập nhật dữ liệu từ các tiêu chuẩn lâm nghiệp quốc tế để phát hiện gỗ giả, gỗ kém chất lượng hoặc gỗ thuộc danh mục cấm.
