# test-scenarios.md — Skill 159: wood-quality-assessment

Five concrete end-to-end test scenarios with real wood species data. Each scenario lists the input provided by the "user", the expected sub-skill flow, and which quality gates are exercised. These scenarios validate the full harness from intake to verdict.

---

## Scenario 1: Standard Authentic Analysis — Vietnamese Furniture

**Input (simulated user message in Vietnamese):**
```
Tôi có một lô gỗ Teak (Tectona grandis) nhập từ Myanmar, dự định sản xuất bàn ghế nội thất xuất khẩu sang EU.
- Ảnh end-grain: [attached]
- Độ ẩm: 9.5% (đo bằng máy điện trở EM)
- Tỷ trọng: 640 kg/m3 (air-dry 12%)
- Xuất xứ: Myanmar
```

**Expected Harness Flow:**

| Step | Sub-Skill | Expected Output | Gates Exercised |
|------|-----------|-----------------|-----------------|
| 1 | sub-gather-requirements | Species: Tectona grandis (Teak), photos: 1 (end-grain), MC: 9.5% EM, density: 640 kg/m³, origin: Myanmar, use: interior furniture, market: EU, lang: vi | G1 (species confirmed) |
| 2 | sub-evidence-collector | CITES: Not listed (Tectona grandis not CITES-protected), IUCN: EN (natural populations — flag), Legality: EUDR due diligence, Anatomy: ring-porous, olivaceous parenchyma, non-storied | G2 (CITES+IUCN retrieved) |
| 3 | sub-grain-image-analysis | Wood type: hardwood, porosity: ring-porous to semi-ring-porous, IAWA codes: 3, 5, 13, 79, 89, 106, candidate: Tectona grandis, confidence: HIGH, diagnostic: white vessel deposits, marginal parenchyma, golden-brown color | G3 (confidence + mismatches) |
| 4 | sub-physical-property-analysis | MC: 9.5% EM, condition: KD-I, benchmark: 620-690 kg/m³, density: 640 kg/m³ — MATCH, drying: ADEQUATE for interior furniture (8-10% target), T/R: 1.3-1.5 (excellent), grade: A | G4 (MC+density with benchmark) |
| 5 | sub-authenticity-compliance | Species match: MATCH, substitution: LOW, CITES: Not listed, IUCN: EN (flag for natural population source), EUDR: due diligence required, origin: plausible (Myanmar is natural range), legality: COMPLIANT with EUDR documentation | G5 (CITES+IUCN both species) |
| 6 | sub-knowledge-updater | Citations: Wood Handbook, IAWA Teak anatomy, CITES not-listed confirmation, coverage: STRONG, gaps: updated IUCN population data for Myanmar teak | G6 (≥1 source surfaced) |
| 7 | sub-quality-advisor | Verdict: AUTHENTIC, Grade: A, risks: (1) IUCN EN status means natural harvest may face future restrictions, (2) verify plantation vs natural source, (3) EUDR geolocation documentation required | G7 (valid verdict) |
| 8 | Quality Gates | U1-U6 + G1-G5: All gates expected to PASS | All |

**Expected Final Verdict:** AUTHENTIC — Tectona grandis matched, physical properties consistent, legally compliant for EU import with EUDR due diligence documentation. Flag: verify plantation (CITES-exempt, IUCN LC) vs natural forest (IUCN EN) source.

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| U1 | PASS | ≥3 sources (Wood Database, USDA FPL, CITES checklist, IAWA standard) |
| U2 | PASS | Disclosure before verdict |
| U3 | PASS | All sources tiered and date-stamped |
| U4 | PASS | Output in Vietnamese |
| U5 | PASS | All 12 template sections present |
| U6 | PASS | All claims linked to sources |
| G1 | PASS | Anatomy reference (Wood Database Teak + IAWA code) cited |
| G2 | PASS | MC 9.5% EM, density 640 kg/m³ vs benchmark 620-690 |
| G3 | PASS | CITES+IUN checked (not listed + EN) |
| G4 | PASS | Verdict: Authentic |
| G5 | PASS | Confidence HIGH, image disclaimer included |

---

## Scenario 2: Suspected Adulteration — Rosewood Substitution

**Input (simulated user message in English):**
```
We purchased "Indian Rosewood" (Dalbergia latifolia) for musical instrument backs.
- End-grain photo: [attached]
- Tangential surface: [attached]
- Moisture: 7.5% (oven-dry method)
- Density: 890 kg/m3 (air-dry, unusually high)
- Origin claimed: India
- Destination: USA
- No CITES documentation provided
```

**Expected Harness Flow:**

| Step | Expected Finding |
|------|-----------------|
| 1 | Species: Dalbergia latifolia (Indian Rosewood), MC: 7.5% OD, density: 890 kg/m³, origin: India, market: USA |
| 2 | CITES: Dalbergia spp. = Appendix II (Annotation #15 — musical instrument backs <10kg exempt), IUCN: VU, Lacey Act requirements, anatomy: diffuse-porous, storied structure, aliform-confluent parenchyma, D. latifolia benchmark density: 770-860 kg/m³ |
| 3 | Anatomy: diffuse-porous, storied rays + parenchyma + vessels, aliform-confluent parenchyma, dark gum deposits, IAWA: 5, 13, 58, 80, 83, 97, 118. Candidate: Dalbergia genus — but density (890) exceeds D. latifolia benchmark (770-860). Possible D. oliveri (Burmese Rosewood, 920-960) or D. retusa (Cocobolo, 900-1100). Confidence: MEDIUM (genus clear, species uncertain) |
| 4 | MC: 7.5% OD — KD-D condition, ADEQUATE for instruments. Density: 890 kg/m³ vs benchmark 770-860 → DEVIATION (+7.5%). Substitution signal: MODERATE |
| 5 | Species: genus match, species mismatch. Dalbergia latifolia claimed but density suggests D. oliveri or D. retusa. Substitution risk: HIGH. CITES: Both are Appendix II (Annotation #15). Musical parts ≤10kg → exempt. BUT no CITES documentation = potential violation if non-exempt items in shipment. Lacey Act: import declaration required. Origin: India plausible for D. latifolia, Myanmar/Thailand for D. oliveri, Central America for D. retusa. |
| 6 | Citations on Dalbergia identification, CITES Annotation #15, density database |
| 7 | Verdict: SUSPECTED ADULTERATION. Grade: B (density still acceptable for instruments). Risks: CITES non-compliance if non-exempt items, Lacey Act false declaration, IUU harvest risk. Recommend: DART-MS or DNA to confirm species. |

**Expected Final Verdict:** SUSPECTED ADULTERATION — Dalbergia genus confirmed but density outside D. latifolia range suggests D. oliveri or D. retusa. CITES applies to both. Verify species by DART-MS or DNA barcoding before making Lacey Act declaration.

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| G1 | PASS | Anatomy reference for Dalbergia genus cited |
| G2 | PASS | Density deviation explicitly compared to benchmark |
| G3 | PASS | CITES Annex II + IUCN VU checked for both claimed D. latifolia and candidate alternate species |
| G4 | PASS | Verdict: Suspected Adulteration |
| G5 | PASS | Confidence MEDIUM with confusable genera listed |

---

## Scenario 3: Prohibited Species — CITES Appendix I

**Input (simulated user message in English):**
```
We have a vintage furniture piece claimed to be "Rio Rosewood" — Dalbergia nigra.
- End-grain photo: [attached — dark, dense wood, storied structure visible]
- Moisture: 8.2% (EM)
- Density: 840 kg/m3
- Origin: Brazil
- Exporting to: EU
- No CITES documents available
```

**Expected Harness Flow:**

| Step | Expected Finding |
|------|-----------------|
| 1 | Species: Dalbergia nigra (Brazilian Rosewood, Rio Rosewood), MC: 8.2%, density: 840 kg/m³, origin: Brazil, market: EU |
| 2 | CITES: Dalbergia nigra = **Appendix I** (since 1992). International COMMERCIAL trade PROHIBITED. IUCN: VU. Anatomy: diffuse-porous, storied, aliform-confluent parenchyma, benchmark density 800-880 kg/m³. EUDR: prohibited species cannot be imported commercially. |
| 3 | Anatomy: diffuse-porous, storied, aliform-confluent, dark gum deposits, dense. IAWA: 5, 13, 58, 80, 83, 97, 118. Candidate: Dalbergia genus, consistent with D. nigra. Confidence: MEDIUM (cannot distinguish D. nigra from other dense Dalbergia without DART-MS). |
| 4 | MC: 8.2% EM, KD-I, ADEQUATE for furniture. Density: 840 kg/m³ vs D. nigra benchmark 800-880 → MATCH. Substitution signal: NONE (within range). Grade: B (good density for furniture). |
| 5 | Species: MATCH to Dalbergia genus. CITES: Appendix I = **COMMERCIAL TRADE PROHIBITED**. No permits = illegal. Even non-commercial requires both export AND import permits. Origin: Brazil plausible (natural range of D. nigra). EU market: CITES I = cannot import commercially. Antiquities exemption: If piece is pre-1992 (before CITES I listing) and can be proven, may qualify for exception — requires certificate from Brazilian CITES MA. |
| 6 | CITES Appendix I regulations, D. nigra identification, vintage/antique exemptions |
| 7 | Verdict: PROHIBITED. Grade: B (physically suitable, but irrelevant — legality overrides). Scenarios: Best = proven pre-1992 antique with Brazilian certificate → possible non-commercial export. Base = no documentation → illegal to trade. Worst = not actually D. nigra but another restricted Dalbergia → still illegal. |

**Expected Final Verdict:** PROHIBITED — Dalbergia nigra is CITES Appendix I. International commercial trade is prohibited regardless of physical quality. The only legal path is proof of pre-1992 manufacture + Brazilian CITES MA certificate for non-commercial export.

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| G1 | PASS | D. nigra anatomy reference (Wood Database + IAWA) |
| G2 | PASS | Density benchmark comparison |
| G3 | PASS | CITES I explicitly checked for D. nigra |
| G4 | PASS | Verdict: Prohibited |
| G5 | PASS | Confidence MEDIUM with image disclaimer |

---

## Scenario 4: Non-Compliant — Missing Documentation

**Input (simulated user message in English):**
```
Shipment of Sapele (Entandrophragma cylindricum) sawn timber from Republic of Congo.
- End-grain photo: [attached — diffuse-porous, storied rays, narrow parenchyma bands]
- Moisture: 14.2% (EM)
- Density: 620 kg/m3
- Intended: Interior flooring for German market
- Supplier: "No FSC certificate, no CITES permit — said it's not needed"
```

**Expected Harness Flow:**

| Step | Expected Finding |
|------|-----------------|
| 1 | Species: Entandrophragma cylindricum (Sapele), MC: 14.2% EM, density: 620 kg/m³, origin: Republic of Congo, market: Germany (EU), use: interior flooring |
| 2 | CITES: Not listed (Entandrophragma is NOT CITES-listed for Congo populations — verify: E. cylindricum is NOT Appendix II; only certain Khaya populations are), IUCN: VU (Vulnerable), Legality: EUDR requires due diligence + harvest geo-coordinates, FSC: recommended for VU species from Congo Basin, anatomy: diffuse-porous, storied, narrow regular marginal parenchyma bands, cedar-like scent |
| 3 | Anatomy: diffuse-porous, storied rays, narrow regular parenchyma bands (IAWA: 86, 89, 106), cedar scent. Candidate: Entandrophragma cylindricum. Confidence: HIGH. Mismatches: none vs reference. |
| 4 | MC: 14.2% EM, condition: AD. Target for interior flooring (heated): 6-9% MC. **INADEQUATE — MC too high by ~5%.** Must re-dry. Density: 620 kg/m³ vs benchmark 590-650 → MATCH. Mechanical grade: D30. Substitution: NONE. Grade: C (marginal — MC off-spec). |
| 5 | Species: MATCH. CITES: Not listed. IUCN: VU — requires EUDR due diligence. Origin: Congo Basin (plausible). EUDR: **MISSING documentation** — no harvest geo-coordinates, no due diligence statement, no FSC. Supplier claim "not needed" is WRONG. Legality for EU: NON-COMPLIANT — EUDR requires due diligence for ALL timber imports. FSC: not certified — for VU species from high-risk region, this is a red flag. |
| 6 | EUDR requirements, E. cylindricum IUCN VU, Congo Basin governance indicators |
| 7 | Verdict: NON-COMPLIANT. Grade: C. Risks: EUDR violation → shipment seizure + fines, MC off-spec → flooring failure (cupping, gapping), reputational damage from non-compliant sourcing. Remediation: (1) Hold shipment, (2) re-dry to 6-9% MC, (3) request EUDR due diligence from supplier including geo-coordinates, (4) consider switching to FSC-certified Sapele supplier. |

**Expected Final Verdict:** NON-COMPLIANT — Species identity confirmed as Sapele but shipment fails EUDR due diligence requirements. No harvest documentation provided. MC too high for interior flooring. Re-drying + documentation required before market entry.

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| G1 | PASS | Sapele anatomy reference (InsideWood + Wood Database) cited |
| G2 | PASS | MC 14.2% vs target 6-9%; density 620 vs benchmark 590-650 |
| G3 | PASS | CITES not listed + IUCN VU checked |
| G4 | PASS | Verdict: Non-compliant |
| G5 | PASS | Confidence HIGH, image disclaimer included |

---

## Scenario 5: Degraded Mode — Minimal Input, No Live Sources

**Input (simulated user message):**
```
"Is this oak?" — single blurry photo of a wood surface (not clean end-grain, tangential view only)
No moisture, no density, no origin, no intended use info. All web sources simulated as unreachable.
```

**Expected Harness Flow:**

| Step | Expected Finding |
|------|-----------------|
| 1 | Species: "claimed Quercus (oak)", photos: 1 — tangential only, NO end-grain, quality: POOR for identification. MC: not provided (assume 12-15% AD). Density: not provided. Origin: not stated. Use: general woodworking. Market: global. Language: en. Assumptions: extensive. Gaps: 6 of 9 fields missing. |
| 2 | Degraded mode: Live sources unreachable → fallback to SECOND-KNOWLEDGE-BRAIN.md. CITES: Quercus spp. not listed. IUCN: varies by species (most Quercus LC, some threatened). Anatomy from SKB: ring-porous, broad+fine rays (oak diagnostic). Physical: generic oak benchmark 630-770 kg/m³. Limitation: "historical data as of last SKB update." |
| 3 | IMAGE QUALITY INSUFFICIENT — tangential view only, no clean end-grain, poor resolution. Cannot code IAWA features. Wood appears ring-porous (oak-like) but cannot confirm. Rays not visible on tangential (need face grain for ray height). Confidence: LOW. Candidate grouping: "possibly Quercus (oak) but cannot exclude Fraxinus (ash) or Carya (hickory) — insufficient data." Image-only uncertainty: MAXIMUM. |
| 4 | No MC reading → assume 12-15% AD (estimated, not measured). Flag as unreliable. No density → cannot compare to benchmark. Use generic oak range 630-770 kg/m³ as reference only. Mechanical: cannot estimate without density. Drying: cannot assess. Substitution: cannot assess. Physical assessment: INCOMPLETE. |
| 5 | Species match: CANNOT DETERMINE (insufficient evidence). Substitution risk: CANNOT ASSESS. CITES: Oak not listed (low risk). IUCN: varies — general oak not a concern. Legality: insufficient data for origin/market determination. Origin: not stated — cannot assess. Follow-up: REQUIRED — provide clean end-grain photo at 10x+ magnification, measure MC and density, state origin and market. |
| 6 | SKB: Oak anatomy reference, generic density range. Coverage: WEAK — species-level data absent, only genus-level. |
| 7 | Verdict: INCONCLUSIVE. Grade: Cannot assign (insufficient data). Scenarios: Best = it's American White Oak, safe + legal. Base = some oak species, need confirmation. Worst = not oak at all (ash/hickory substitute), potentially non-compliant depending on origin. Risks: species misidentification, physical unsuitability, regulatory unknown. Remediation: send 1 board with clean end-grain cut, MC reading, density measurement, origin + market info. |

**Expected Final Verdict:** INCONCLUSIVE — Insufficient data (no clean end-grain, no physical measurements, no origin, no market). Cannot determine species, cannot assess legality, cannot grade physical quality. LIMITATION banner applied (Level 3).

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| U1 | ⚠️ | Sources may be limited to SKB cached entries — live sources unreachable |
| U2 | PASS | Disclosure must precede verdict |
| U3 | ⚠️ | Sources from SKB may lack live access dates — flagged |
| U4 | PASS | English output |
| U5 | ⚠️ | Some sections may be abbreviated — physical analysis section incomplete |
| U6 | ⚠️ | Multiple claims flagged as "agent judgment — not verified" |
| G1 | ⚠️ FAIL | Species ID cites only generic oak reference, no image-based confirmation |
| G2 | ⚠️ FAIL | MC and density both missing — no benchmark comparison possible |
| G3 | PASS | CITES/IUCN checked for Quercus genus (not listed / LC) |
| G4 | PASS | Verdict: Inconclusive |
| G5 | PASS | Image uncertainty maximally stated, disclaimer prominent |

---

## Scenario 6: Comparison — Two Species Side by Side

**Input (simulated user message):**
```
Compare these two samples for furniture production:
Sample A: Claimed "White Oak" (Quercus alba), end-grain + tangential [attached], MC 8.0% OD, density 720 kg/m³, USA origin, EU market.
Sample B: Claimed same as A — "White Oak" but looks different. End-grain + tangential [attached], MC 9.5% OD, density 580 kg/m³, origin "Europe", EU market.
```

**Expected Differential Findings:**

| Aspect | Sample A | Sample B |
|--------|----------|----------|
| Anatomy | Ring-porous, flame-like latewood vessels, ABUNDANT TYLOSES, broad+fine rays → Quercus alba (White Oak) | Ring-porous, flame-like latewood vessels, sparse tyloses, broad+fine rays → Quercus rubra group (Red Oak) |
| IAWA | 1, 3, 7, 13, 43, 56, 77, 99, 103 | 1, 3, 7, 13, 43, 77, 99, 103 (no tyloses = key diff) |
| Density | 720 kg/m³ → in White Oak range (680-770) | 580 kg/m³ → BELOW White Oak range, in Red Oak range (630-710)? No — 580 is below both. Check: European Oak (Q. robur) 670-720? Check measurement basis. |
| Confidence | HIGH — diagnostic tyloses + density match | MEDIUM — Red Oak group but density low; possible Q. rubra (630-710) but 580 = outlier; re-measure? |
| Verdict A | AUTHENTIC — White Oak confirmed | SUSPECTED ADULTERATION — different species than claimed; possibly Red Oak or mixed shipment |
| Verdict B | Grade A (MC 8.0%, density match, excellent stability) | Grade B (MC 9.5% acceptable, but species mismatch) |
| Comparison | A is superior for furniture — White Oak is more decay-resistant, better dimensional stability, higher density | B is Red Oak group — acceptable furniture wood but less decay-resistant, notably lower density, mislabeled as "White Oak" — economic downgrade substitution |

**Combined Verdict:** Sample A = AUTHENTIC (Quercus alba). Sample B = SUSPECTED ADULTERATION (mislabeled — appears to be Red Oak group, not White Oak). Physical grade: A = A, B = B. Risk: Mixed-species lot. Investigate supplier. CITES: Neither oak is CITES-listed. Legality: Lacey Act requires correct species declaration — B's declaration is false.

---

## Scenario 7: Risk Assessment — High-Risk Origin

**Input (simulated user message):**
```
African Rosewood (Pterocarpus erinaceus) logs for veneer production.
- End-grain + tangential [attached]
- MC: 18% (freshly sawn, green)
- Density: 720 kg/m³ (basic density)
- Origin: "West Africa" (vague, no specific country)
- Market: Vietnam
- No CITES permit, no FSC
```

**Expected Harness Flow:**

| Step | Expected Finding |
|------|-----------------|
| 1 | Species: Pterocarpus erinaceus (African Rosewood, Kosso, Barwood), MC: 18% (green/PAD), density: 720 kg/m³ basic (~815 air-dry), origin: "West Africa" (vague), market: Vietnam, use: veneer production |
| 2 | CITES: Pterocarpus erinaceus = **Appendix II** (since 2017) — requires CITES export permit. IUCN: **Endangered (EN)**. Vietnam legality: VNTLAS — import requires valid CITES export permit + origin documentation. Anatomy: diffuse-porous, storied, aliform-confluent parenchyma, vivid orange-red heartwood. Density benchmark: 650-800 kg/m³ basic. |
| 3 | Anatomy: diffuse-porous, vessels solitary + radial multiples 2-3, aliform-confluent parenchyma, STORIED rays + parenchyma, vivid orange-red color. IAWA: 5, 10, 13, 58, 80, 83, 97, 118. Candidate: Pterocarpus genus, consistent with P. erinaceus. Confidence: MEDIUM — cannot distinguish P. erinaceus from P. soyauxii or P. tinctorius without DART-MS/DNA (all West African Pterocarpus species). Mismatches: none vs genus reference. |
| 4 | MC: 18% PAD — TOO HIGH for use. Target for veneer: 8-12%. Requires kiln drying before peeling. Density: 720 basic → ~815 air-dry (approximate) — within Pterocarpus range. Grade: Cannot assign (MC too high — re-dry first). |
| 5 | Species: Pterocarpus genus match. CITES: **Appendix II — PERMIT REQUIRED.** Supplier has NO permit → CITES violation. IUCN: EN → heightened concern, VNTLAS high-risk classification. Origin: "West Africa" is VAGUE — violates VNTLAS documentation requirements. Specific country and harvest location needed. Legality: NON-COMPLIANT / PROHIBITED without CITES permit. Origin risk: HIGH — West Africa is known source of illegally logged rosewood. |
| 6 | CITES P. erinaceus Appendix II, VNTLAS import requirements, Pterocarpus identification references |
| 7 | Verdict: PROHIBITED (no CITES permit) / NON-COMPLIANT (insufficient origin documentation). Grade: N/A — re-dry first. Risks: (1) CITES violation → seizure + penalties in Vietnam and origin country, (2) EN species — sustainability + reputation, (3) vague origin — likely illegal logging from West African protected areas, (4) MC too high — veneer quality issues. Severe commercial and legal risk. Recommendation: REJECT. If acceptance is considered: (a) obtain CITES II export permit from specific origin country, (b) trace harvest to specific concession with GPS coordinates, (c) verify VNTLAS import procedures, (d) re-dry before processing. |

**Expected Final Verdict:** PROHIBITED — Pterocarpus erinaceus is CITES Appendix II requiring export permit. No permit available. Vague origin declaration + EN IUCN status + missing VNTLAS documentation. CRITICAL RISK. Do not accept shipment.

**Gate Results Expected:**
| Gate | Expected | Rationale |
|------|----------|-----------|
| G1 | PASS | Pterocarpus anatomy reference cited |
| G2 | ⚠️ | MC reported but no benchmark for MC — this is a drying assessment, not benchmark comparison; density benchmark comparison present |
| G3 | PASS | CITES II + IUCN EN checked |
| G4 | PASS | Verdict: Prohibited |
| G5 | PASS | Confidence MEDIUM, image disclaimer, confusable Pterocarpus species listed |

---

## Gate Coverage Matrix

| Gate | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
|------|----|----|----|----|----|----|-----|
| U1 — Sources | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ✓ |
| U2 — Disclosure first | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U3 — Tier labels | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ✓ |
| U4 — Language | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U5 — Template complete | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ✓ |
| U6 — Claims traceable | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ✓ |
| G1 — Anatomy reference | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ✓ |
| G2 — MC+Density benchmark | ✓ | ✓ | ✓ | ✓ | ⚠️ | ✓ | ⚠️ |
| G3 — CITES+IUCN both | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| G4 — Valid verdict | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| G5 — Image uncertainty | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Legend:** ✓ = Pass | ⚠️ = Pass with limitation flag | ✗ = Fail
