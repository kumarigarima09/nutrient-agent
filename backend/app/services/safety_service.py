"""
Safety & Clinical Boundary Layer
Detects high-risk medical triggers, severe symptoms, eating disorder behaviors,
chronic diseases, and pregnancy. Ensures the application operates strictly as a nutrition coach
and never diagnoses illness or prescribes clinical treatments.
"""

import re
from typing import Dict, Any, List

# Clinical red flag triggers
SAFETY_TRIGGERS = {
    "eating_disorder": [
        "binge", "purging", "vomit after eating", "laxatives to lose weight",
        "starving myself", "hate my body", "afraid of eating anything",
        "less than 500 calories", "severe anorexia", "bulimia"
    ],
    "kidney_disease": [
        "kidney disease", "ckd", "renal failure", "dialysis", "nephropathy", "high creatinine"
    ],
    "diabetes_clinical": [
        "type 1 diabetes", "insulin pump", "ketoacidosis", "diabetic coma",
        "blood sugar over 300", "hypoglycemia seizure"
    ],
    "pregnancy_lactation": [
        "pregnant", "pregnancy", "breastfeeding", "trimester", "lactating"
    ],
    "severe_symptoms": [
        "chest pain", "shortness of breath", "fainting", "syncope", "blood in stool",
        "severe stomach pain", "sudden unexplained weight loss"
    ],
    "severe_allergies": [
        "anaphylaxis", "throat swelling", "epipen", "closed airways"
    ]
}

SAFETY_DISCLAIMERS = {
    "eating_disorder": (
        "IMPORTANT HEALTH NOTICE: Nutrition coaches and AI tools are not equipped to treat eating disorders or severe distress around food. "
        "If you are experiencing compulsive restriction, bingeing, or distress, please consider reaching out to a compassionate healthcare professional "
        "or a specialized organization such as NEDA (National Eating Disorders Association helpline) or an accredited dietitian."
    ),
    "kidney_disease": (
        "CLINICAL NOTICE: Kidney disease requires precise clinical management of electrolytes (potassium, phosphorus, sodium) and specific protein titration "
        "by a registered nephrology dietitian or physician. Automated nutrition recommendations cannot account for individual glomerular filtration rates."
    ),
    "diabetes_clinical": (
        "CLINICAL NOTICE: For individuals managing insulin-dependent diabetes or unstable blood glucose, macronutrient timing and carbohydrate counting "
        "must be coordinated directly with your endocrinologist or certified diabetes care and education specialist."
    ),
    "pregnancy_lactation": (
        "HEALTH NOTICE: Caloric and micronutrient requirements (folate, iron, calcium, choline) change significantly during pregnancy and lactation. "
        "Please follow the specific dietary plan prescribed by your obstetrician or clinical prenatal dietitian."
    ),
    "severe_symptoms": (
        "URGENT NOTICE: The symptoms you described require prompt medical evaluation. Please seek immediate assistance from an urgent care clinic, "
        "emergency department, or your primary physician."
    ),
    "severe_allergies": (
        "SAFETY WARNING: Severe allergies carrying risk of anaphylaxis must be managed under medical supervision with emergency medications (such as an epinephrine auto-injector). "
        "Always inspect food labels carefully."
    ),
    "general": (
        "Medical Disclaimer: This application provides generalized dietary and lifestyle guidance based on peer-reviewed nutritional science. "
        "It does not provide medical diagnoses, treatment plans, or clinical therapy. Always consult a qualified healthcare professional before making major dietary changes."
    )
}


class SafetyService:

    @classmethod
    def check_input_safety(cls, text: str) -> Dict[str, Any]:
        """
        Screens text for clinical safety triggers.
        Returns safety status, flagged categories, and relevant medical disclaimers.
        """
        text_lower = text.lower()
        flagged_categories: List[str] = []

        for category, triggers in SAFETY_TRIGGERS.items():
            for trig in triggers:
                # Word boundary match
                pattern = rf'\b{re.escape(trig)}\b'
                if re.search(pattern, text_lower):
                    if category not in flagged_categories:
                        flagged_categories.append(category)
                    break

        if flagged_categories:
            disclaimers = [SAFETY_DISCLAIMERS[cat] for cat in flagged_categories]
            return {
                "is_safe_for_automated_planning": False,
                "flagged_categories": flagged_categories,
                "requires_medical_referral": True,
                "disclaimer": " ".join(disclaimers),
                "action": "redirect_to_healthcare_professional"
            }

        return {
            "is_safe_for_automated_planning": True,
            "flagged_categories": [],
            "requires_medical_referral": False,
            "disclaimer": SAFETY_DISCLAIMERS["general"],
            "action": "proceed"
        }
