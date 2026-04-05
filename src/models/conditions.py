"""Dermatological condition knowledge base.

Provides detailed, patient-friendly information about common skin
conditions for the knowledge base / library feature.
"""

from dataclasses import asdict, dataclass, field


@dataclass
class ConditionInfo:
    key: str
    name: str
    category: str  # benign | precancer | cancer | inflammatory | infection
    severity: int  # 1-5 typical
    short_description: str
    overview: str
    appearance: str
    causes: list[str] = field(default_factory=list)
    symptoms: list[str] = field(default_factory=list)
    self_care: list[str] = field(default_factory=list)
    when_to_see_doctor: str = ""
    prevalence: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


CONDITIONS: dict[str, ConditionInfo] = {
    "melanoma": ConditionInfo(
        key="melanoma",
        name="Melanoma",
        category="cancer",
        severity=5,
        short_description=(
            "A serious skin cancer arising from pigment-producing cells. "
            "Early detection dramatically improves outcomes."
        ),
        overview=(
            "Melanoma develops from melanocytes, the cells that produce skin "
            "pigment. It can appear on existing moles or as new dark spots. "
            "Unlike more common skin cancers, melanoma can spread to other "
            "organs if not treated early, making prompt evaluation critical."
        ),
        appearance=(
            "Often asymmetric with irregular, notched borders; multiple colors "
            "(black, brown, red, white, blue); typically larger than 6 mm; "
            "changes over time in size, shape, or color."
        ),
        causes=[
            "UV radiation from sun or tanning beds",
            "Family or personal history of melanoma",
            "Many atypical moles (>50 total moles)",
            "Fair skin, light eyes, light hair",
            "History of severe sunburns, especially in childhood",
        ],
        symptoms=[
            "New or changing mole",
            "Asymmetric lesion",
            "Irregular, notched, or blurred borders",
            "Multiple colors within a single lesion",
            "Diameter greater than 6 mm",
            "Itching, bleeding, or crusting",
        ],
        self_care=[
            "Do NOT attempt to treat or remove at home",
            "Protect from sun exposure while awaiting evaluation",
            "Photograph the area for comparison over time",
        ],
        when_to_see_doctor=(
            "URGENT — see a dermatologist within 24-48 hours for any lesion "
            "with ABCDE warning signs. Early melanoma is highly treatable."
        ),
        prevalence="About 1 in 38 Americans develop melanoma in their lifetime",
    ),
    "basal_cell_carcinoma": ConditionInfo(
        key="basal_cell_carcinoma",
        name="Basal Cell Carcinoma (BCC)",
        category="cancer",
        severity=4,
        short_description=(
            "The most common form of skin cancer. Usually slow-growing and "
            "rarely spreads, but requires medical treatment."
        ),
        overview=(
            "BCC arises from basal cells in the deepest layer of the epidermis. "
            "It typically grows slowly and rarely metastasizes, but can cause "
            "significant local tissue damage if left untreated."
        ),
        appearance=(
            "Pearly or waxy bump, often with visible tiny blood vessels; may "
            "appear as a flat flesh-colored or brown scar-like lesion; can "
            "bleed, scab over, and recur in the same spot."
        ),
        causes=[
            "Chronic sun exposure",
            "Fair skin",
            "Prior radiation therapy",
            "Immunosuppression",
            "Age over 50",
        ],
        symptoms=[
            "Pearly, translucent bump on sun-exposed skin",
            "Sore that won't heal or keeps returning",
            "Rolled border with central depression",
            "Occasional bleeding or oozing",
        ],
        self_care=[
            "Do not pick or attempt to remove",
            "Keep the area clean and protected from sun",
        ],
        when_to_see_doctor=(
            "Schedule with a dermatologist within 1-2 weeks. Highly treatable "
            "when caught early."
        ),
        prevalence="Over 4 million cases diagnosed in the US each year",
    ),
    "squamous_cell_carcinoma": ConditionInfo(
        key="squamous_cell_carcinoma",
        name="Squamous Cell Carcinoma (SCC)",
        category="cancer",
        severity=4,
        short_description=(
            "Second most common skin cancer. Can spread if untreated but is "
            "usually curable when caught early."
        ),
        overview=(
            "SCC arises from squamous cells in the outer epidermis. Most often "
            "appears on sun-exposed areas. Has a higher risk of spreading than "
            "BCC, so timely treatment is important."
        ),
        appearance=(
            "Firm red nodule, flat scaly patch, or crusted sore; may ulcerate "
            "and bleed; often rough to the touch."
        ),
        causes=[
            "Cumulative sun exposure",
            "HPV infection (certain subtypes)",
            "Immunosuppression",
            "Chronic wounds or scars",
            "Exposure to arsenic or certain chemicals",
        ],
        symptoms=[
            "Rough, scaly red patch",
            "Raised growth with a central depression",
            "Open sore that persists for weeks",
            "Wart-like growth that bleeds",
        ],
        self_care=[
            "Avoid further sun exposure to the area",
            "Keep clean; do not pick",
        ],
        when_to_see_doctor=(
            "See a dermatologist within 1 week. Early-stage SCC has a >95% cure rate."
        ),
        prevalence="About 1.8 million US cases diagnosed annually",
    ),
    "actinic_keratosis": ConditionInfo(
        key="actinic_keratosis",
        name="Actinic Keratosis",
        category="precancer",
        severity=3,
        short_description=(
            "A precancerous rough patch caused by sun damage. Can progress "
            "to squamous cell carcinoma if untreated."
        ),
        overview=(
            "Actinic keratoses are rough, scaly patches that develop on skin "
            "damaged by years of sun exposure. A small percentage progress to "
            "skin cancer, so they are usually treated preventively."
        ),
        appearance=(
            "Rough, dry, scaly patch of skin, often easier to feel than see; "
            "1-3 mm to over 2 cm; pink, red, brown, or skin-colored; commonly "
            "on face, scalp, ears, neck, backs of hands."
        ),
        causes=[
            "Years of sun exposure",
            "Fair skin",
            "Older age",
            "Weakened immune system",
        ],
        symptoms=[
            "Sandpaper-like rough texture",
            "Flat or slightly raised patch",
            "Itching or burning",
            "Dry, scaly surface",
        ],
        self_care=[
            "Daily broad-spectrum sunscreen (SPF 30+)",
            "Wear protective clothing and hats",
            "Avoid peak sun hours",
        ],
        when_to_see_doctor=(
            "See a dermatologist within a few weeks for evaluation and "
            "possible treatment (cryotherapy, topical medications, etc.)."
        ),
        prevalence="Affects more than 58 million Americans",
    ),
    "psoriasis": ConditionInfo(
        key="psoriasis",
        name="Psoriasis",
        category="inflammatory",
        severity=3,
        short_description=(
            "A chronic autoimmune condition causing rapid skin-cell turnover "
            "and scaly red patches."
        ),
        overview=(
            "Psoriasis is a long-term condition where the immune system causes "
            "skin cells to multiply far too quickly. The buildup creates thick, "
            "scaly plaques that can be itchy, painful, and emotionally distressing."
        ),
        appearance=(
            "Well-defined red/pink plaques covered with silvery-white scales; "
            "commonly on elbows, knees, scalp, lower back; often symmetric."
        ),
        causes=[
            "Genetic predisposition",
            "Immune system dysfunction",
            "Stress",
            "Infections (e.g., strep throat)",
            "Certain medications",
            "Skin injury (Koebner phenomenon)",
        ],
        symptoms=[
            "Red patches with silvery scales",
            "Dry, cracked skin that may bleed",
            "Itching, burning, or soreness",
            "Thickened or ridged nails",
            "Swollen, stiff joints (psoriatic arthritis)",
        ],
        self_care=[
            "Moisturize daily with thick creams",
            "Take short warm (not hot) baths with colloidal oatmeal",
            "Manage stress",
            "Avoid known triggers",
        ],
        when_to_see_doctor=(
            "Schedule with a dermatologist for diagnosis and prescription "
            "treatment, especially if widespread or affecting quality of life."
        ),
        prevalence="About 2-3% of the global population",
    ),
    "eczema": ConditionInfo(
        key="eczema",
        name="Eczema (Atopic Dermatitis)",
        category="inflammatory",
        severity=2,
        short_description=(
            "A chronic condition causing itchy, inflamed, dry skin. Often "
            "begins in childhood and runs in families."
        ),
        overview=(
            "Eczema is a chronic inflammatory skin condition with a relapsing "
            "course. It's linked to a dysfunctional skin barrier and often "
            "occurs alongside allergies and asthma."
        ),
        appearance=(
            "Dry, red, itchy patches; may ooze and crust when severely "
            "inflamed; often on face, inner elbows, behind knees."
        ),
        causes=[
            "Genetic skin barrier dysfunction",
            "Immune system overactivity",
            "Environmental triggers (soaps, detergents, allergens)",
            "Stress",
            "Temperature and humidity changes",
        ],
        symptoms=[
            "Intense itching, especially at night",
            "Dry, sensitive skin",
            "Red to brownish-gray patches",
            "Small raised bumps that may leak fluid",
            "Thickened, cracked skin from scratching",
        ],
        self_care=[
            "Moisturize at least twice daily with fragrance-free creams",
            "Take short lukewarm baths and pat dry",
            "Use mild, fragrance-free soaps",
            "Avoid scratching — keep nails short",
            "Identify and avoid personal triggers",
        ],
        when_to_see_doctor=(
            "See a doctor if OTC measures aren't controlling symptoms, if skin "
            "is infected (yellow crusts, fever), or if sleep is disrupted."
        ),
        prevalence="Affects about 10-20% of children and 1-3% of adults",
    ),
    "contact_dermatitis": ConditionInfo(
        key="contact_dermatitis",
        name="Contact Dermatitis",
        category="inflammatory",
        severity=2,
        short_description=(
            "Skin inflammation caused by direct contact with an allergen "
            "or irritant."
        ),
        overview=(
            "Contact dermatitis comes in two main forms: irritant (from "
            "harsh substances damaging skin) and allergic (from immune "
            "response to allergens like nickel, fragrances, or poison ivy). "
            "Identifying and avoiding the trigger is the key to treatment."
        ),
        appearance=(
            "Red, itchy rash often in the shape of the contact area; may "
            "include blisters, swelling, and weeping."
        ),
        causes=[
            "Irritants: soaps, detergents, solvents, acids",
            "Allergens: nickel, fragrances, latex, certain plants",
            "Repeated wet work",
            "Personal care products",
        ],
        symptoms=[
            "Red, itchy rash",
            "Blisters that ooze and crust",
            "Dry, cracked, scaly skin",
            "Burning or tenderness",
        ],
        self_care=[
            "Identify and avoid the trigger",
            "Wash exposed skin with mild soap and water",
            "Apply cool compresses",
            "Use OTC hydrocortisone cream",
            "Oral antihistamines for itching",
        ],
        when_to_see_doctor=(
            "See a doctor if the rash is severe, widespread, on the face or "
            "genitals, or not improving after 1-2 weeks of self-care."
        ),
        prevalence="Very common — most adults experience it at some point",
    ),
    "seborrheic_keratosis": ConditionInfo(
        key="seborrheic_keratosis",
        name="Seborrheic Keratosis",
        category="benign",
        severity=1,
        short_description=(
            "A common, harmless skin growth that appears waxy and stuck on. "
            "More frequent with age."
        ),
        overview=(
            "Seborrheic keratoses are benign skin growths that multiply with "
            "age. They are not cancerous and do not become cancerous, but can "
            "sometimes be mistaken for melanoma."
        ),
        appearance=(
            "Waxy, scaly, slightly raised growths that look 'stuck on' the "
            "skin; tan, brown, or black; round or oval; usually well-defined."
        ),
        causes=[
            "Aging",
            "Genetic predisposition",
            "Sun exposure (possibly)",
        ],
        symptoms=[
            "Painless waxy bumps",
            "May itch occasionally",
            "Can become irritated if rubbed by clothing",
        ],
        self_care=[
            "No treatment usually needed",
            "Avoid picking or scratching",
        ],
        when_to_see_doctor=(
            "See a doctor if you're unsure whether a lesion is a SK or "
            "something more serious, or if it's bleeding, changing, or causing "
            "discomfort."
        ),
        prevalence="Extremely common in adults over 50",
    ),
    "dermatofibroma": ConditionInfo(
        key="dermatofibroma",
        name="Dermatofibroma",
        category="benign",
        severity=1,
        short_description=(
            "A harmless firm nodule under the skin, typically on the legs. "
            "Often appears after minor trauma."
        ),
        overview=(
            "Dermatofibromas are benign fibrous nodules that form in the "
            "dermis, often triggered by insect bites or minor injuries. They "
            "are harmless but can persist indefinitely."
        ),
        appearance=(
            "Firm, small (5-10 mm) round nodule; pink, red, brown, or "
            "purplish; characteristic 'dimple sign' when squeezed."
        ),
        causes=[
            "Minor trauma (insect bites, ingrown hairs)",
            "Unknown in many cases",
        ],
        symptoms=[
            "Firm bump under the skin",
            "Occasional itching or tenderness",
            "Dimple sign on pinching",
        ],
        self_care=["Leave it alone — no treatment needed for most cases"],
        when_to_see_doctor=(
            "See a doctor if the lesion grows rapidly, changes color, or "
            "becomes painful or ulcerated."
        ),
        prevalence="Common, especially in young to middle-aged adults",
    ),
    "tinea": ConditionInfo(
        key="tinea",
        name="Tinea (Ringworm)",
        category="infection",
        severity=2,
        short_description=(
            "A common fungal infection of the skin causing ring-shaped, "
            "itchy rashes. Highly treatable."
        ),
        overview=(
            "Despite the name, ringworm is caused by a fungus, not a worm. "
            "It's contagious and can spread through skin contact, shared "
            "items, or from pets."
        ),
        appearance=(
            "Ring-shaped red patches with a raised, scaly border and clearer "
            "center; can appear anywhere on the body."
        ),
        causes=[
            "Dermatophyte fungi",
            "Direct contact with infected people or animals",
            "Shared towels, clothing, or surfaces",
            "Warm, moist environments",
        ],
        symptoms=[
            "Itchy, ring-shaped rash",
            "Scaly, red edges",
            "Clearer skin in the center of the ring",
            "Can spread to multiple sites",
        ],
        self_care=[
            "OTC antifungal creams (clotrimazole, terbinafine) for 2-4 weeks",
            "Keep the area clean and dry",
            "Don't share towels, clothes, or bedding",
            "Wash hands after touching affected skin",
        ],
        when_to_see_doctor=(
            "See a doctor if OTC treatment fails after 2 weeks, if it's on "
            "the scalp or nails, or if it's widespread."
        ),
        prevalence="Very common — affects roughly 20% of people at some point",
    ),
    "acne": ConditionInfo(
        key="acne",
        name="Acne Vulgaris",
        category="inflammatory",
        severity=2,
        short_description=(
            "A common skin condition caused by clogged hair follicles. Can "
            "range from mild to severe and scarring."
        ),
        overview=(
            "Acne develops when hair follicles become plugged with oil and "
            "dead skin cells. Bacteria, hormones, and inflammation all play "
            "a role. It most commonly affects teens but can occur at any age."
        ),
        appearance=(
            "Whiteheads, blackheads, papules, pustules, nodules, or cysts; "
            "commonly on face, chest, upper back, shoulders."
        ),
        causes=[
            "Excess oil production",
            "Clogged hair follicles",
            "Bacteria (C. acnes)",
            "Hormonal changes",
            "Certain medications",
            "Diet (high-glycemic foods in some people)",
        ],
        symptoms=[
            "Comedones (whiteheads and blackheads)",
            "Inflamed red pimples",
            "Pus-filled pustules",
            "Tender nodules or cysts (severe acne)",
            "Scarring from severe lesions",
        ],
        self_care=[
            "Wash affected areas gently twice daily",
            "Use OTC benzoyl peroxide or salicylic acid",
            "Avoid picking or squeezing",
            "Use non-comedogenic skincare and cosmetics",
            "Be patient — treatments take 6-8 weeks to work",
        ],
        when_to_see_doctor=(
            "See a dermatologist for moderate-to-severe acne, scarring acne, "
            "or when OTC treatments aren't working after 8-12 weeks."
        ),
        prevalence="Affects about 85% of people aged 12-24",
    ),
    "benign_nevus": ConditionInfo(
        key="benign_nevus",
        name="Benign Nevus (Common Mole)",
        category="benign",
        severity=1,
        short_description=(
            "A common, harmless growth of pigment cells. Most adults have "
            "10-40 moles."
        ),
        overview=(
            "Moles are clusters of melanocytes (pigment cells) that form in "
            "the skin. Most are completely harmless, but new or changing moles "
            "should be evaluated as they can occasionally turn into melanoma."
        ),
        appearance=(
            "Usually round or oval; uniform brown or tan color; well-defined "
            "borders; typically smaller than 6 mm; flat or slightly raised."
        ),
        causes=[
            "Genetic predisposition",
            "Sun exposure (new moles)",
            "Normal pigment cell clusters",
        ],
        symptoms=[
            "Uniform color",
            "Symmetric shape",
            "Smooth, well-defined border",
            "Stable over time",
        ],
        self_care=[
            "Monthly self-exams using ABCDE criteria",
            "Photograph larger moles for comparison",
            "Sun protection to prevent new moles",
        ],
        when_to_see_doctor=(
            "See a dermatologist for any mole that becomes asymmetric, "
            "changes color, has irregular borders, grows larger than 6 mm, "
            "or is evolving in any way."
        ),
        prevalence="Most adults have at least 10-40 common moles",
    ),
}


def list_conditions() -> list[dict]:
    return [c.to_dict() for c in CONDITIONS.values()]


def get_condition(key: str) -> dict | None:
    cond = CONDITIONS.get(key)
    return cond.to_dict() if cond else None
