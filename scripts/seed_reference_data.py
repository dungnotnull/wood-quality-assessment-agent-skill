"""Seed reference data files for wood-quality-assessment grounding.

Generates references/species_database.json, references/cites_listings.json,
references/iucn_status.json from a curated, real-world dataset mirroring the
authoritative content embedded in SECOND-KNOWLEDGE-BRAIN.md.

Idempotent: overwrites the three output files on each run.

Run:  python scripts/seed_reference_data.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

SPECIES: dict[str, dict[str, Any]] = {}
CITES: list[dict[str, Any]] = []
IUCN: list[dict[str, Any]] = []


def _add(**entry: Any) -> None:
    """Register one species entry keyed by its scientific name."""
    name = entry.pop("scientific_name")
    SPECIES[name] = entry


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


_add(
    scientific_name="Tectona grandis",
    common_names={"en": ["Teak"], "vi": ["Teak", "Giac te"]},
    family="Lamiaceae",
    wood_type="hardwood",
    porosity="ring-porous to semi-ring-porous",
    density_kgm3={"min": 520, "max": 690, "typical": 620},
    moisture_benchmarks={"green_max": 75, "fad_typical": 30, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 4.0, "tr_ratio": 1.75},
    iawa_features={
        "vessel_arrangement": (
            "earlywood solitary large with white deposits; latewood smaller solitary"
        ),
        "rays": "1-4 seriate, non-storied",
        "parenchyma": "vasicentric + marginal",
        "ring_boundaries": "distinct (tropical)",
        "perforations": "simple",
        "special": "contains tectoquinone (oily feel); tyloses moderate",
    },
    heartwood_color="golden-brown, darkens with age",
    native_origin=[
        "South/Southeast Asia (India, Myanmar, Laos, Thailand)",
        "widely plantation-grown",
    ],
    common_uses=["furniture", "boatbuilding", "decking", "carving", "veneer"],
    common_substitution_risks=[
        "Gmelina arborea",
        "Persea americana",
        "Cordia alliodora",
        "treated Catalpa",
    ],
    cites_key=None,
    iucn_key="Tectona grandis",
)

_add(
    scientific_name="Dalbergia nigra",
    common_names={"en": ["Brazilian Rosewood", "Rio Rosewood"], "vi": ["Cam nuoc Brazil"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 800, "max": 1000, "typical": 900},
    moisture_benchmarks={"green_max": 60, "fad_typical": 25, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.0, "radial": 4.6, "tr_ratio": 1.74},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, narrow (<=200um)",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "indistinct to distinct",
        "perforations": "simple",
        "special": "dark gum deposits; full storied structure (vessels/parenchyma/fibers)",
    },
    heartwood_color="dark purple-brown to black with irregular darker streaks",
    native_origin=["Brazil (Atlantic Forest)"],
    common_uses=["historical fine furniture", "veneer", "musical instruments (guitar backs)"],
    common_substitution_risks=["other Dalbergia spp.", "Machaerium scleroxylon (Santos rosewood)"],
    cites_key="Dalbergia nigra",
    iucn_key="Dalbergia nigra",
)

_add(
    scientific_name="Dalbergia latifolia",
    common_names={"en": ["Indian Rosewood", "East Indian Rosewood"], "vi": ["Cam An Do"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 770, "max": 880, "typical": 820},
    moisture_benchmarks={"green_max": 60, "fad_typical": 25, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 4.5, "tr_ratio": 1.56},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, narrow",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "distinct to indistinct",
        "perforations": "simple",
        "special": "dark gum deposits; storied structure",
    },
    heartwood_color="golden-brown to dark purple-brown with darker streaks",
    native_origin=["India", "Indonesia (plantation)"],
    common_uses=["fine furniture", "musical instruments", "veneer", "carving"],
    common_substitution_risks=[
        "Dalbergia sissoo",
        "Machaerium scleroxylon",
        "other Dalbergia spp.",
    ],
    cites_key="Dalbergia spp.",
    iucn_key="Dalbergia latifolia",
)

_add(
    scientific_name="Dalbergia retusa",
    common_names={"en": ["Cocobolo"], "vi": ["Cocobolo"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 960, "max": 1200, "typical": 1080},
    moisture_benchmarks={"green_max": 50, "fad_typical": 22, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.4, "radial": 3.2, "tr_ratio": 2.0},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, very small vessels",
        "rays": "1-3 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent + banded",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "oily surface; strong orange-red heartwood with black streaking",
    },
    heartwood_color="orange-red to deep red with black streaks",
    native_origin=["Central America (Mexico to Panama)"],
    common_uses=["knife handles", "turning", "musical instruments", "inlay"],
    common_substitution_risks=["Dalbergia granadillo", "other Dalbergia spp."],
    cites_key="Dalbergia spp.",
    iucn_key="Dalbergia retusa",
)

_add(
    scientific_name="Dalbergia oliveri",
    common_names={"en": ["Burmese Rosewood", "Southeast Asian Rosewood"], "vi": ["Cam lai"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 820, "max": 1000, "typical": 900},
    moisture_benchmarks={"green_max": 55, "fad_typical": 24, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.2, "radial": 4.0, "tr_ratio": 1.8},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, narrow",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "Burmese rosewood group; overlap with D. bariensis requires DART-MS/DNA",
    },
    heartwood_color="reddish-brown with darker streaks",
    native_origin=["Myanmar", "Thailand", "Laos", "Vietnam", "Cambodia"],
    common_uses=["fine furniture", "carving", "veneer", "traditional handicraft"],
    common_substitution_risks=[
        "Dalbergia bariensis",
        "Pterocarpus macrocarpus",
        "Milletia leucantha",
    ],
    cites_key="Dalbergia spp.",
    iucn_key="Dalbergia oliveri",
)

_add(
    scientific_name="Pterocarpus erinaceus",
    common_names={"en": ["African Rosewood", "Kosso", "Barwood"], "vi": ["Padauk Phi"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 650, "max": 800, "typical": 720},
    moisture_benchmarks={"green_max": 65, "fad_typical": 28, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.0, "radial": 3.5, "tr_ratio": 1.71},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent (eye-shaped bands)",
        "ring_boundaries": "distinct to indistinct",
        "perforations": "simple",
        "special": "high overexploitation risk; West African savanna species",
    },
    heartwood_color="deep reddish-brown with dark streaks",
    native_origin=["West Africa (Senegal to Cameroon)"],
    common_uses=["furniture", "veneer", "handicraft"],
    common_substitution_risks=["Pterocarpus soyauxii (African padauk)", "Dalbergia spp."],
    cites_key="Pterocarpus erinaceus",
    iucn_key="Pterocarpus erinaceus",
)

_add(
    scientific_name="Pterocarpus soyauxii",
    common_names={"en": ["African Padauk"], "vi": ["Padauk Phi"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 720, "max": 800, "typical": 760},
    moisture_benchmarks={"green_max": 65, "fad_typical": 28, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.0, "radial": 3.5, "tr_ratio": 1.71},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3",
        "rays": "1-3 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent + marginal",
        "ring_boundaries": "distinct to indistinct",
        "perforations": "simple",
        "special": (
            "vivid red/orange heartwood fresh; "
            "distinct from P. erinaceus by range and anatomy overlap"
        ),
    },
    heartwood_color="vivid red to orange-red, darkens to brown",
    native_origin=["Central/West Africa (Cameroon, Gabon, Nigeria, Congo)"],
    common_uses=["furniture", "turning", "musical instruments", "veneer"],
    common_substitution_risks=["Pterocarpus erinaceus"],
    cites_key=None,
    iucn_key="Pterocarpus soyauxii",
)

_add(
    scientific_name="Pterocarpus santalinus",
    common_names={"en": ["Red Sanders", "Red Sandalwood"], "vi": ["Huong dan do"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 900, "max": 1050, "typical": 975},
    moisture_benchmarks={"green_max": 50, "fad_typical": 22, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.0, "radial": 3.0, "tr_ratio": 2.0},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, very small numerous vessels",
        "rays": "1-2 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "deep red-purple heartwood; natural dye source",
    },
    heartwood_color="deep red-purple to purplish-red",
    native_origin=["India (Eastern Ghats, Andhra Pradesh)"],
    common_uses=["dye extraction", "carving", "medicinal", "musical instruments"],
    common_substitution_risks=["Pterocarpus soyauxii", "Adenanthera pavonina"],
    cites_key="Pterocarpus santalinus",
    iucn_key="Pterocarpus santalinus",
)

_add(
    scientific_name="Swietenia macrophylla",
    common_names={"en": ["Big-leaf Mahogany", "Honduras Mahogany"], "vi": ["Go moc ho la lon"]},
    family="Meliaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 520, "max": 590, "typical": 560},
    moisture_benchmarks={"green_max": 70, "fad_typical": 30, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 5.0, "radial": 3.0, "tr_ratio": 1.67},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, medium (100-200um)",
        "rays": "1-5 seriate, storied",
        "parenchyma": "vasicentric + confluent + marginal",
        "ring_boundaries": "distinct to indistinct (tropical)",
        "perforations": "simple",
        "special": "reddish-brown gum deposits; interlocked grain",
    },
    heartwood_color="reddish-brown, darkens with age",
    native_origin=["Central/South America (Mexico to Amazon)"],
    common_uses=["fine furniture", "cabinetry", "veneer", "boatbuilding"],
    common_substitution_risks=[
        "Khaya spp. (African mahogany)",
        "Toona ciliata",
        "plantation Swietenia",
    ],
    cites_key="Swietenia macrophylla",
    iucn_key="Swietenia macrophylla",
)

_add(
    scientific_name="Entandrophragma cylindricum",
    common_names={"en": ["Sapele"], "vi": ["Sapele"]},
    family="Meliaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 590, "max": 650, "typical": 620},
    moisture_benchmarks={"green_max": 70, "fad_typical": 30, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 4.5, "tr_ratio": 1.56},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-4",
        "rays": "1-5 seriate, STORIED",
        "parenchyma": "narrow marginal + narrow regular bands (Meliaceae diagnostic)",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "interlocked grain -> ribbon stripe figure on quartersawn",
    },
    heartwood_color="dark reddish-brown with ribbon stripe",
    native_origin=["West/Central Africa (Cameroon, Gabon, Congo, Ghana)"],
    common_uses=["veneer", "doors", "cabinetry", "musical instruments"],
    common_substitution_risks=[
        "Entandrophragma utile (Sipo)",
        "Khaya spp.",
        "Swietenia macrophylla",
    ],
    cites_key=None,
    iucn_key="Entandrophragma cylindricum",
)

_add(
    scientific_name="Khaya ivorensis",
    common_names={"en": ["African Mahogany"], "vi": ["Go moc Phi"]},
    family="Meliaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 490, "max": 560, "typical": 525},
    moisture_benchmarks={"green_max": 75, "fad_typical": 32, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 5.5, "radial": 3.0, "tr_ratio": 1.83},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + narrow regular bands",
        "ring_boundaries": "often indistinct",
        "perforations": "simple",
        "special": "similar to Swietenia; lacks strong gum deposits",
    },
    heartwood_color="pinkish-brown",
    native_origin=["West Africa (Ivory Coast, Ghana, Cameroon)"],
    common_uses=["furniture", "veneer", "boatbuilding", "joinery"],
    common_substitution_risks=["Swietenia macrophylla", "Entandrophragma utile"],
    cites_key=None,
    iucn_key="Khaya ivorensis",
)

_add(
    scientific_name="Cedrela odorata",
    common_names={"en": ["Spanish Cedar", "Cedro"], "vi": ["Cedrela"]},
    family="Meliaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 440, "max": 560, "typical": 480},
    moisture_benchmarks={"green_max": 75, "fad_typical": 33, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.5, "radial": 4.0, "tr_ratio": 1.63},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, medium",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + marginal",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "distinctive cedar odor; cigar box wood",
    },
    heartwood_color="pinkish to reddish-brown",
    native_origin=["Central/South America, Caribbean"],
    common_uses=["cigar boxes", "veneer", "joinery", "musical instruments"],
    common_substitution_risks=["Toona ciliata", "Swietenia spp."],
    cites_key="Cedrela odorata",
    iucn_key="Cedrela odorata",
)

_add(
    scientific_name="Handroanthus spp.",
    common_names={"en": ["Ipe", "Lapacho", "Brazilian Walnut"], "vi": ["Ipe"]},
    family="Bignoniaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 960, "max": 1200, "typical": 1080},
    moisture_benchmarks={"green_max": 60, "fad_typical": 26, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.0, "radial": 5.0, "tr_ratio": 1.6},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, small numerous vessels",
        "rays": "1-4 seriate",
        "parenchyma": "aliform + confluent + banded",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "lapachol content; extremely durable; very heavy",
    },
    heartwood_color="olive-brown to dark brown, yellowish streaks",
    native_origin=["Central/South America"],
    common_uses=["decking", "flooring", "heavy construction", "turning"],
    common_substitution_risks=["Tabebuia spp.", "Mezilaurus itauba"],
    cites_key="Handroanthus spp.",
    iucn_key="Handroanthus impetiginosus",
)

_add(
    scientific_name="Shorea spp.",
    common_names={"en": ["Meranti", "Balau", "Lauan"], "vi": ["Meranti"]},
    family="Dipterocarpaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 370, "max": 970, "typical": 580},
    moisture_benchmarks={"green_max": 90, "fad_typical": 38, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.0, "radial": 4.5, "tr_ratio": 1.78},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples",
        "rays": "1-5 seriate",
        "parenchyma": "paratracheal + apotracheal banded",
        "ring_boundaries": "indistinct (tropical)",
        "perforations": "simple",
        "special": "DIAGNOSTIC: axial intercellular canals in tangential lines (Dipterocarpaceae)",
    },
    heartwood_color="variable by group: light red, dark red, yellow",
    native_origin=["Southeast Asia (Indonesia, Malaysia, Philippines)"],
    common_uses=["plywood", "construction", "flooring", "veneer"],
    common_substitution_risks=["Parashorea spp.", "Hopea spp.", "group mislabeling within Shorea"],
    cites_key=None,
    iucn_key="Shorea negrosensis",
)

_add(
    scientific_name="Quercus alba",
    common_names={"en": ["White Oak"], "vi": ["So trang"]},
    family="Fagaceae",
    wood_type="hardwood",
    porosity="ring-porous",
    density_kgm3={"min": 630, "max": 770, "typical": 770},
    moisture_benchmarks={"green_max": 80, "fad_typical": 35, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.8, "radial": 5.1, "tr_ratio": 1.73},
    iawa_features={
        "vessel_arrangement": (
            "ring-porous; earlywood 200-400um continuous row; latewood dendritic flame"
        ),
        "rays": "TWO SIZES - broad multiseriate (>1mm) + fine uniseriate",
        "parenchyma": "apotracheal diffuse-in-aggregates + paratracheal scanty",
        "ring_boundaries": "very distinct",
        "perforations": "simple",
        "special": "ABUNDANT tyloses (white oak group) - distinguishes from red oak",
    },
    heartwood_color="light to medium brown with olive cast",
    native_origin=["Eastern North America"],
    common_uses=["barrels (cooperage)", "flooring", "furniture", "boatbuilding"],
    common_substitution_risks=["Quercus rubra (red oak)", "Quercus robur (European oak)"],
    cites_key=None,
    iucn_key="Quercus alba",
)

_add(
    scientific_name="Quercus rubra",
    common_names={"en": ["Red Oak"], "vi": ["So do"]},
    family="Fagaceae",
    wood_type="hardwood",
    porosity="ring-porous",
    density_kgm3={"min": 630, "max": 770, "typical": 700},
    moisture_benchmarks={"green_max": 80, "fad_typical": 35, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.6, "radial": 4.0, "tr_ratio": 2.15},
    iawa_features={
        "vessel_arrangement": "ring-porous; earlywood large continuous row; latewood dendritic",
        "rays": "TWO SIZES - broad multiseriate + fine uniseriate",
        "parenchyma": "apotracheal diffuse-in-aggregates + paratracheal scanty",
        "ring_boundaries": "very distinct",
        "perforations": "simple",
        "special": "tyloses SPARSE/ABSENT (red oak group) - distinguishes from white oak",
    },
    heartwood_color="pinkish to reddish-brown",
    native_origin=["Eastern North America"],
    common_uses=["flooring", "cabinetry", "furniture", "millwork"],
    common_substitution_risks=["Quercus alba (white oak)", "other red oaks"],
    cites_key=None,
    iucn_key="Quercus rubra",
)

_add(
    scientific_name="Quercus robur",
    common_names={"en": ["European Oak", "English Oak"], "vi": ["So Au Chau"]},
    family="Fagaceae",
    wood_type="hardwood",
    porosity="ring-porous",
    density_kgm3={"min": 650, "max": 770, "typical": 720},
    moisture_benchmarks={"green_max": 80, "fad_typical": 35, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 9.5, "radial": 5.2, "tr_ratio": 1.83},
    iawa_features={
        "vessel_arrangement": "ring-porous; earlywood 200-350um, 1-3 vessels wide",
        "rays": "broad multiseriate + fine uniseriate",
        "parenchyma": "vasicentric + confluent",
        "ring_boundaries": "very distinct",
        "perforations": "simple",
        "special": "tyloses abundant; broader rays than Q. alba",
    },
    heartwood_color="light to medium brown",
    native_origin=["Europe"],
    common_uses=["furniture", "flooring", "cooperage", "veneer"],
    common_substitution_risks=["Quercus petraea", "Quercus alba"],
    cites_key=None,
    iucn_key="Quercus robur",
)

_add(
    scientific_name="Diospyros spp.",
    common_names={"en": ["Ebony"], "vi": ["Hoang dan den"]},
    family="Ebenaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 900, "max": 1150, "typical": 1020},
    moisture_benchmarks={"green_max": 50, "fad_typical": 22, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 9.0, "radial": 5.0, "tr_ratio": 1.8},
    iawa_features={
        "vessel_arrangement": (
            "solitary + radial multiples 2-3, very small (<=100um), numerous (>40/mm2)"
        ),
        "rays": "1-2 seriate (exclusively uniseriate in some), STORIED (low rays)",
        "parenchyma": "vasicentric",
        "ring_boundaries": "indistinct",
        "perforations": "simple",
        "special": "jet black heartwood in D. crassiflora/D. celebica; streaked in others",
    },
    heartwood_color="jet black to black with streaks",
    native_origin=["Africa, South/Southeast Asia (D. ebenum - Sri Lanka/India)"],
    common_uses=["carving", "piano keys", "inlay", "turning", "fingerboards"],
    common_substitution_risks=["Diospyros crassiflora vs D. celebica", "stained Eucalyptus"],
    cites_key="Diospyros spp.",
    iucn_key="Diospyros crassiflora",
)

_add(
    scientific_name="Aquilaria spp.",
    common_names={"en": ["Agarwood", "Aloeswood"], "vi": ["Tram huong"]},
    family="Thymelaeaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 400, "max": 700, "typical": 530},
    moisture_benchmarks={"green_max": 70, "fad_typical": 30, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.5, "radial": 3.5, "tr_ratio": 1.86},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, small-medium",
        "rays": "1-3 seriate",
        "parenchyma": "vasicentric + sparse banded",
        "ring_boundaries": "indistinct",
        "perforations": "simple",
        "special": "resinous infected heartwood (oud) is the trade product, not normal wood",
    },
    heartwood_color="pale; infected resin-wood dark brown/black with resin",
    native_origin=["Southeast Asia (Vietnam, Indonesia, Malaysia, India)"],
    common_uses=["perfume/oud oil", "incense", "carvings", "medicinal"],
    common_substitution_risks=["Gyrinops spp.", "non-resinous Aquilaria fraud"],
    cites_key="Aquilaria spp.",
    iucn_key="Aquilaria malaccensis",
)

_add(
    scientific_name="Gonystylus spp.",
    common_names={"en": ["Ramin"], "vi": ["Ramin"]},
    family="Thymelaeaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 560, "max": 700, "typical": 640},
    moisture_benchmarks={"green_max": 75, "fad_typical": 32, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.5, "radial": 4.5, "tr_ratio": 1.89},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, medium",
        "rays": "1-3 seriate, storied",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "indistinct",
        "perforations": "simple",
        "special": "pale uniform wood; high illegal-logging history",
    },
    heartwood_color="pale yellow to cream (no distinct heartwood)",
    native_origin=["Southeast Asia (Malaysia, Indonesia, Papua)"],
    common_uses=["veneer", "blinds", "mouldings", "turning"],
    common_substitution_risks=["Dacrydium spp.", "Leptospermum"],
    cites_key="Gonystylus spp.",
    iucn_key="Gonystylus bancanus",
)

_add(
    scientific_name="Intsia spp.",
    common_names={"en": ["Merbau", "Kwila"], "vi": ["Merbau"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 740, "max": 900, "typical": 800},
    moisture_benchmarks={"green_max": 65, "fad_typical": 28, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 4.0, "tr_ratio": 1.75},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, medium",
        "rays": "1-4 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent + banded",
        "ring_boundaries": "distinct to indistinct",
        "perforations": "simple",
        "special": "yellowish sulfur-like powder in vessels (soluble extractives)",
    },
    heartwood_color="yellowish to orange-brown, darkens",
    native_origin=["Southeast Asia, Oceania (Indonesia, PNG, Fiji)"],
    common_uses=["flooring", "decking", "joinery", "furniture"],
    common_substitution_risks=["Pometia pinnata", "other Fabaceae"],
    cites_key=None,
    iucn_key="Intsia bijuga",
)

_add(
    scientific_name="Pericopsis elata",
    common_names={"en": ["Afrormosia", "African Teak"], "vi": ["Afrormosia"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 610, "max": 700, "typical": 660},
    moisture_benchmarks={"green_max": 65, "fad_typical": 28, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 6.5, "radial": 3.5, "tr_ratio": 1.86},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3",
        "rays": "1-3 seriate, STORIED",
        "parenchyma": "vasicentric + aliform + confluent + banded",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "teak-like appearance; marketed as African teak",
    },
    heartwood_color="yellowish-brown to dark brown with streaks",
    native_origin=["West/Central Africa (Cameroon, Congo, Ghana, Cote d'Ivoire)"],
    common_uses=["furniture", "veneer", "boatbuilding", "joinery"],
    common_substitution_risks=["Tectona grandis", "other legumes"],
    cites_key="Pericopsis elata",
    iucn_key="Pericopsis elata",
)

_add(
    scientific_name="Microberlinia brazzavillensis",
    common_names={"en": ["Zebrawood"], "vi": ["Go van ngua"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 740, "max": 810, "typical": 775},
    moisture_benchmarks={"green_max": 65, "fad_typical": 28, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 8.0, "radial": 4.5, "tr_ratio": 1.78},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, medium-large",
        "rays": "1-4 seriate, most STORIED",
        "parenchyma": "vasicentric + aliform + confluent",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": (
            "DIAGNOSTIC: regular parenchyma bands create alternating dark/light zebra pattern"
        ),
    },
    heartwood_color="light golden with dark brown streaks",
    native_origin=["West Africa (Gabon, Cameroon, Congo)"],
    common_uses=["veneer", "turning", "furniture accents"],
    common_substitution_risks=["other Microberlinia spp."],
    cites_key=None,
    iucn_key="Microberlinia brazzavillensis",
)

_add(
    scientific_name="Millettia leucantha",
    common_names={"en": ["Burmese Blackwood", "Tamalan"], "vi": ["Cam lai den"]},
    family="Fabaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 820, "max": 950, "typical": 880},
    moisture_benchmarks={"green_max": 55, "fad_typical": 24, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 3.8, "tr_ratio": 1.84},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples, narrow",
        "rays": "1-3 seriate, STORIED",
        "parenchyma": "aliform + confluent",
        "ring_boundaries": "distinct",
        "perforations": "simple",
        "special": "very similar to Dalbergia - KEY DISTINCTION requires DART-MS or DNA",
    },
    heartwood_color="dark brown to violet-brown with darker streaks",
    native_origin=["Myanmar", "Thailand", "Vietnam", "Cambodia"],
    common_uses=["fine furniture", "carving", "veneer"],
    common_substitution_risks=["Dalbergia oliveri", "Dalbergia bariensis"],
    cites_key=None,
    iucn_key="Millettia leucantha",
)

_add(
    scientific_name="Pinus spp.",
    common_names={"en": ["Pine"], "vi": ["Thong"]},
    family="Pinaceae",
    wood_type="softwood",
    porosity="tracheid (non-porous)",
    density_kgm3={"min": 380, "max": 690, "typical": 520},
    moisture_benchmarks={"green_max": 120, "fad_typical": 40, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.0, "radial": 4.0, "tr_ratio": 1.75},
    iawa_features={
        "vessel_arrangement": "N/A (softwood - no vessels)",
        "rays": "ray tracheids present",
        "parenchyma": "N/A",
        "ring_boundaries": "very distinct; abrupt (hard pines) or gradual (soft pines)",
        "perforations": "N/A (tracheids)",
        "special": (
            "axial resin canals with THIN-walled epithelial cells "
            "(Pinus-type, diagnostic); cross-field pits fenestriform "
            "(soft pines) or pinoid (hard pines)"
        ),
    },
    heartwood_color="cream to reddish-brown",
    native_origin=["Northern hemisphere (wide distribution)"],
    common_uses=["construction", "framing", "furniture", "plywood", "flooring"],
    common_substitution_risks=[
        "Larix spp. (larch)",
        "Picea spp. (spruce)",
        "Pseudotsuga (Douglas fir)",
    ],
    cites_key=None,
    iucn_key="Pinus sylvestris",
)

_add(
    scientific_name="Picea spp.",
    common_names={"en": ["Spruce"], "vi": ["Vu sam"]},
    family="Pinaceae",
    wood_type="softwood",
    porosity="tracheid (non-porous)",
    density_kgm3={"min": 400, "max": 470, "typical": 430},
    moisture_benchmarks={"green_max": 120, "fad_typical": 40, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 7.5, "radial": 3.5, "tr_ratio": 2.14},
    iawa_features={
        "vessel_arrangement": "N/A (softwood)",
        "rays": "ray tracheids present",
        "parenchyma": "N/A",
        "ring_boundaries": "very distinct; abrupt transition",
        "perforations": "N/A (tracheids)",
        "special": (
            "axial resin canals with THICK-walled epithelial cells; "
            "spiral thickening in tracheids (diagnostic); "
            "piceoid cross-field pits"
        ),
    },
    heartwood_color="cream to pale yellowish",
    native_origin=["Northern hemisphere (boreal/temperate)"],
    common_uses=["construction", "musical instrument soundboards (Sitka spruce)", "pulp"],
    common_substitution_risks=["Abies spp. (fir - no resin canals)", "Tsuga (hemlock)"],
    cites_key=None,
    iucn_key="Picea abies",
)

_add(
    scientific_name="Acer saccharum",
    common_names={"en": ["Sugar Maple", "Hard Maple"], "vi": ["Maple ngot"]},
    family="Sapindaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 690, "max": 740, "typical": 720},
    moisture_benchmarks={"green_max": 70, "fad_typical": 32, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 9.9, "radial": 4.8, "tr_ratio": 2.06},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-5, small (<=100um)",
        "rays": "1-5 seriate",
        "parenchyma": "apotracheal diffuse-in-aggregates + scanty paratracheal",
        "ring_boundaries": "distinct",
        "perforations": "simple (most species); sometimes scalariform (A. saccharum)",
        "special": "birdseye/curly figure prized; dense hard wood",
    },
    heartwood_color="pale reddish-brown",
    native_origin=["Eastern North America"],
    common_uses=["flooring", "furniture", "butcher blocks", "musical instruments"],
    common_substitution_risks=["Acer rubrum (soft maple)", "Betula alleghaniensis"],
    cites_key=None,
    iucn_key="Acer saccharum",
)

_add(
    scientific_name="Betula alleghaniensis",
    common_names={"en": ["Yellow Birch"], "vi": ["Tuong vang"]},
    family="Betulaceae",
    wood_type="hardwood",
    porosity="diffuse-porous",
    density_kgm3={"min": 610, "max": 710, "typical": 660},
    moisture_benchmarks={"green_max": 70, "fad_typical": 32, "kd_target": 12},
    shrinkage_tr_ratio={"tangential": 9.2, "radial": 6.3, "tr_ratio": 1.46},
    iawa_features={
        "vessel_arrangement": "solitary + radial multiples 2-3, small (50-100um)",
        "rays": "1-4 seriate",
        "parenchyma": "apotracheal diffuse-in-aggregates + scanty paratracheal",
        "ring_boundaries": "distinct",
        "perforations": "SCALARIFORM (diagnostic, 10-30 bars)",
        "special": "scalariform perforation plates distinguish from maple",
    },
    heartwood_color="pale yellow to light reddish-brown",
    native_origin=["Northeastern North America"],
    common_uses=["furniture", "cabinetry", "plywood", "turning"],
    common_substitution_risks=["Acer saccharum (maple)"],
    cites_key=None,
    iucn_key="Betula alleghaniensis",
)

CITES.extend(
    [
        {
            "scientific_name": "Dalbergia nigra",
            "appendix": "I",
            "annotation": "All parts and derivatives",
            "listing_date": "1992",
            "notes": "Brazilian Rosewood - most restricted; commercial trade prohibited",
        },
        {
            "scientific_name": "Dalbergia spp.",
            "appendix": "II",
            "annotation": (
                "#15 - all parts except seeds, seedling cultures, "
                "finished musical instruments <=10kg, finished accessories/parts, "
                "non-commercial <=10kg. Excludes D. nigra."
            ),
            "listing_date": "2017",
            "notes": "All rosewoods (300+ species) listed Jan 2017",
        },
        {
            "scientific_name": "Pterocarpus erinaceus",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood",
            "listing_date": "2017",
            "notes": "African Rosewood/Kosso - high overexploitation",
        },
        {
            "scientific_name": "Pterocarpus santalinus",
            "appendix": "II",
            "annotation": "Logs, wood chips, powder, extracts (not finished products)",
            "listing_date": "1995",
            "notes": "Red Sanders - Indian endemic",
        },
        {
            "scientific_name": "Pterocarpus tinctorius",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer sheets",
            "listing_date": "2022",
            "notes": "Mukula/African padauk trade",
        },
        {
            "scientific_name": "Swietenia macrophylla",
            "appendix": "II",
            "annotation": (
                "Logs, sawn wood, veneer. Neotropical populations only. Plantation exempt."
            ),
            "listing_date": "2003",
            "notes": "Big-leaf Mahogany",
        },
        {
            "scientific_name": "Swietenia mahagoni",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer. Neotropical only. Plantation exempt.",
            "listing_date": "2003",
            "notes": "Caribbean Mahogany",
        },
        {
            "scientific_name": "Swietenia humilis",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer. Neotropical only. Plantation exempt.",
            "listing_date": "2003",
            "notes": "Pacific Coast Mahogany",
        },
        {
            "scientific_name": "Cedrela odorata",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood. Neotropical populations.",
            "listing_date": "2023",
            "notes": "Spanish Cedar - listed at CoP19",
        },
        {
            "scientific_name": "Handroanthus spp.",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood (selected Neotropical species)",
            "listing_date": "2023",
            "notes": "Ipe/Lapacho - newly listed",
        },
        {
            "scientific_name": "Aquilaria spp.",
            "appendix": "II",
            "annotation": (
                "All parts except seeds, pollen, seedling cultures, "
                "fruits, leaves, exhausted powder"
            ),
            "listing_date": "2005",
            "notes": "Agarwood - resinous infected wood is the trade product",
        },
        {
            "scientific_name": "Gyrinops spp.",
            "appendix": "II",
            "annotation": "Same as Aquilaria",
            "listing_date": "2005",
            "notes": "Agarwood relatives",
        },
        {
            "scientific_name": "Gonystylus spp.",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood, finished products",
            "listing_date": "2003",
            "notes": "Ramin - high illegal-logging history",
        },
        {
            "scientific_name": "Diospyros spp.",
            "appendix": "II",
            "annotation": (
                "Logs, sawn wood, veneer, plywood, transformed wood (Madagascar populations)"
            ),
            "listing_date": "2023",
            "notes": "Ebony - Madagascar populations listed at CoP19",
        },
        {
            "scientific_name": "Pericopsis elata",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood",
            "listing_date": "1995",
            "notes": "Afrormosia - African teak substitute",
        },
        {
            "scientific_name": "Khaya spp.",
            "appendix": "II",
            "annotation": "Logs, sawn wood, veneer, plywood (Khaya grandifoliola populations)",
            "listing_date": "2023",
            "notes": "African mahogany - CoP19 listing",
        },
    ]
)

IUCN.extend(
    [
        {
            "scientific_name": "Dalbergia nigra",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Dalbergia latifolia",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Dalbergia retusa",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2020,
        },
        {
            "scientific_name": "Dalbergia oliveri",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2020,
        },
        {
            "scientific_name": "Pterocarpus erinaceus",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2020,
        },
        {
            "scientific_name": "Pterocarpus santalinus",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Pterocarpus soyauxii",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Swietenia macrophylla",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2018,
        },
        {
            "scientific_name": "Entandrophragma cylindricum",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2018,
        },
        {
            "scientific_name": "Khaya ivorensis",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2018,
        },
        {
            "scientific_name": "Cedrela odorata",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2018,
        },
        {
            "scientific_name": "Handroanthus impetiginosus",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Shorea negrosensis",
            "category": "CR",
            "category_full": "Critically Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Quercus alba",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Quercus rubra",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Quercus robur",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Diospyros crassiflora",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Aquilaria malaccensis",
            "category": "CR",
            "category_full": "Critically Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Gonystylus bancanus",
            "category": "CR",
            "category_full": "Critically Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Intsia bijuga",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2018,
        },
        {
            "scientific_name": "Pericopsis elata",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Microberlinia brazzavillensis",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing",
            "assessed_year": 2019,
        },
        {
            "scientific_name": "Millettia leucantha",
            "category": "VU",
            "category_full": "Vulnerable",
            "trend": "Decreasing",
            "assessed_year": 2020,
        },
        {
            "scientific_name": "Tectona grandis",
            "category": "EN",
            "category_full": "Endangered",
            "trend": "Decreasing (natural populations)",
            "assessed_year": 2019,
            "notes": "Natural populations Endangered; plantation teak widely LC in trade",
        },
        {
            "scientific_name": "Pinus sylvestris",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Picea abies",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Acer saccharum",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2017,
        },
        {
            "scientific_name": "Betula alleghaniensis",
            "category": "LC",
            "category_full": "Least Concern",
            "trend": "Stable",
            "assessed_year": 2014,
        },
    ]
)


def main() -> int:
    refs = ROOT / "references"
    refs.mkdir(parents=True, exist_ok=True)
    _write(refs / "species_database.json", SPECIES)
    _write(refs / "cites_listings.json", CITES)
    _write(refs / "iucn_status.json", IUCN)

    # Cross-check integrity: every species iucn_key must resolve in IUCN.
    iucn_names = {e["scientific_name"] for e in IUCN}
    missing_iucn = [s["iucn_key"] for s in SPECIES.values() if s["iucn_key"] not in iucn_names]
    if missing_iucn:
        raise SystemExit(f"IUCN cross-check failed; missing: {missing_iucn}")

    # Cross-check: every species cites_key (if set) must resolve in CITES.
    cites_names = {e["scientific_name"] for e in CITES}
    missing_cites = [
        s["cites_key"]
        for s in SPECIES.values()
        if s["cites_key"] and s["cites_key"] not in cites_names
    ]
    if missing_cites:
        raise SystemExit(f"CITES cross-check failed; missing: {missing_cites}")

    print(f"species_database.json: {len(SPECIES)} species")
    print(f"cites_listings.json: {len(CITES)} listings")
    print(f"iucn_status.json: {len(IUCN)} assessments")
    print("Cross-checks: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
