"""Dermatological condition definitions and reference data."""

from dataclasses import dataclass


@dataclass
class Condition:
    name: str
    description: str
    typical_severity: int  # 1-5
    keywords: list[str]
    morphology: dict


# Reference database of common dermatological conditions
CONDITIONS_DB = {
    "melanoma": Condition(
        name="Melanoma",
        description=(
            "A serious form of skin cancer that develops from melanocytes. "
            "Requires urgent medical evaluation."
        ),
        typical_severity=5,
        keywords=["asymmetric", "irregular_border", "multi_color", "large", "dark"],
        morphology={
            "symmetry": "asymmetric",
            "border": "irregular",
            "color_uniformity": "multi_color",
            "typical_colors": ["black", "dark_brown", "blue", "red", "white"],
            "surface": "varied",
        },
    ),
    "basal_cell_carcinoma": Condition(
        name="Basal Cell Carcinoma",
        description=(
            "The most common type of skin cancer. Slow-growing and rarely "
            "metastasizes but requires medical treatment."
        ),
        typical_severity=4,
        keywords=["pearly", "translucent", "raised", "rolled_border", "telangiectasia"],
        morphology={
            "symmetry": "variable",
            "border": "rolled",
            "color_uniformity": "uniform",
            "typical_colors": ["skin_colored", "pink", "pearly"],
            "surface": "smooth",
        },
    ),
    "squamous_cell_carcinoma": Condition(
        name="Squamous Cell Carcinoma",
        description=(
            "A common skin cancer arising from squamous cells. "
            "Can metastasize if untreated."
        ),
        typical_severity=4,
        keywords=["scaly", "crusty", "rough", "red", "ulcerated", "firm"],
        morphology={
            "symmetry": "variable",
            "border": "irregular",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink", "skin_colored"],
            "surface": "scaly",
        },
    ),
    "actinic_keratosis": Condition(
        name="Actinic Keratosis",
        description=(
            "A precancerous skin growth caused by sun damage. "
            "Can progress to squamous cell carcinoma."
        ),
        typical_severity=3,
        keywords=["rough", "scaly", "dry", "sandpaper", "sun_exposed"],
        morphology={
            "symmetry": "variable",
            "border": "ill_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink", "brown", "skin_colored"],
            "surface": "rough",
        },
    ),
    "psoriasis": Condition(
        name="Psoriasis",
        description=(
            "A chronic autoimmune condition causing rapid skin cell buildup "
            "forming scales and red patches."
        ),
        typical_severity=3,
        keywords=["silvery_scales", "red_patches", "plaque", "symmetric", "thick"],
        morphology={
            "symmetry": "symmetric",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink", "silvery"],
            "surface": "scaly",
        },
    ),
    "eczema": Condition(
        name="Eczema (Atopic Dermatitis)",
        description=(
            "A chronic inflammatory skin condition causing itchy, "
            "red, and dry skin."
        ),
        typical_severity=2,
        keywords=["itchy", "red", "dry", "inflamed", "cracked", "weeping"],
        morphology={
            "symmetry": "variable",
            "border": "ill_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink"],
            "surface": "rough",
        },
    ),
    "contact_dermatitis": Condition(
        name="Contact Dermatitis",
        description=(
            "Skin inflammation caused by contact with an allergen "
            "or irritant."
        ),
        typical_severity=2,
        keywords=["red", "itchy", "blisters", "localized", "weeping"],
        morphology={
            "symmetry": "variable",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink"],
            "surface": "varied",
        },
    ),
    "seborrheic_keratosis": Condition(
        name="Seborrheic Keratosis",
        description=(
            "A common benign skin growth. Appears waxy and stuck-on. "
            "Generally harmless."
        ),
        typical_severity=1,
        keywords=["waxy", "stuck_on", "brown", "raised", "well_defined"],
        morphology={
            "symmetry": "symmetric",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["brown", "tan", "black"],
            "surface": "waxy",
        },
    ),
    "dermatofibroma": Condition(
        name="Dermatofibroma",
        description="A common benign skin nodule, firm to touch.",
        typical_severity=1,
        keywords=["firm", "small", "brown", "dimple_sign", "nodule"],
        morphology={
            "symmetry": "symmetric",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["brown", "pink", "red"],
            "surface": "smooth",
        },
    ),
    "tinea": Condition(
        name="Tinea (Ringworm)",
        description=(
            "A fungal infection of the skin causing ring-shaped rashes."
        ),
        typical_severity=2,
        keywords=["ring_shaped", "scaly", "red", "clearing_center", "circular"],
        morphology={
            "symmetry": "symmetric",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["red", "pink"],
            "surface": "scaly",
        },
    ),
    "acne": Condition(
        name="Acne Vulgaris",
        description=(
            "A common skin condition caused by clogged hair follicles."
        ),
        typical_severity=2,
        keywords=["papules", "pustules", "comedones", "oily", "face"],
        morphology={
            "symmetry": "variable",
            "border": "variable",
            "color_uniformity": "variable",
            "typical_colors": ["red", "pink", "white", "skin_colored"],
            "surface": "raised",
        },
    ),
    "benign_nevus": Condition(
        name="Benign Nevus (Mole)",
        description=(
            "A common benign growth of melanocytes. Usually harmless "
            "but should be monitored for changes."
        ),
        typical_severity=1,
        keywords=["symmetric", "uniform_color", "small", "round", "smooth"],
        morphology={
            "symmetry": "symmetric",
            "border": "well_defined",
            "color_uniformity": "uniform",
            "typical_colors": ["brown", "tan", "dark_brown"],
            "surface": "smooth",
        },
    ),
}
