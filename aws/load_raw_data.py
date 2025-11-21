# load_real_skyflow_data.py

import requests
import json

# RAW Skyflow-protected data - tokens are VISIBLE
data = {
    "condition": "leukemia",
    "studies": [
        {
            "nct_id": "NCT12345",
            "title": "B-cell Acute Lymphoblastic Leukemia Treatment Study",
            "status": "RECRUITING",
            "phase": ["PHASE3"],
            "conditions": ["B-cell Acute Lymphoblastic Leukemia", "Relapsed Refractory ALL"],
            
            # SKYFLOW TOKENS - VISIBLE AS-IS
            "patient_name": "[NAME_VGMgLRv]",
            "patient_mrn": "[HEALTHCARE_NUMBER_tKNCgm6]",
            "patient_dob": "[DOB_gCXQIV6]",
            "patient_phone": "[PHONE_NUMBER_46UXbal]",
            "patient_address": "[LOCATION_ADDRESS_STREET_S5USJli], Columbus, OH 43221",
            "emergency_contact_name": "[NAME_ldlMjxb]",
            "emergency_contact_phone": "[PHONE_NUMBER_nwHLRg0]",
            "primary_care_physician": "[NAME_BuVLer5], MD",
            "attending_physician": "[NAME_Jgf3GNQ], MD",
            
            # NON-SENSITIVE DATA - PLAINTEXT
            "age": 46,
            "sex": "Male",
            "race": "White",
            "insurance": "Aetna PPO",
            
            "diagnosis": "Relapsed refractory B-cell acute lymphoblastic leukemia",
            "initial_diagnosis_year": 2022,
            "relapse_year": 2024,
            
            "bone_marrow_biopsy": {
                "date": "2025-09-18",
                "blast_percentage": 58,
                "cd19_positive": True,
                "cd22_positive": True,
                "cytogenetics": "t(12;21)(p13;q22) and IKZF1 deletion"
            },
            
            "mutations": {
                "NRAS": "G12D",
                "TP53": "R248Q (5% VAF)"
            },
            
            "treatment_history": [
                "hyper-CVAD induction (2022) - complete remission",
                "blinatumomab consolidation (2 cycles)",
                "inotuzumab ozogamicin (2024) - partial response, complicated by thrombocytopenia"
            ],
            
            "current_symptoms": [
                "Progressive fatigue",
                "Night sweats (drenching)",
                "Lymphadenopathy",
                "Exertional dyspnea",
                "Ecchymoses",
                "Low-grade fevers"
            ],
            
            "ecog_performance_status": 1,
            
            "labs": {
                "hemoglobin": "7.4 g/dL",
                "hematocrit": "22.1%",
                "wbc": "2.8 K/uL",
                "anc": "710/uL",
                "platelets": "61 K/uL",
                "creatinine": "0.9 mg/dL",
                "creatinine_clearance": "78 mL/min",
                "ast": "38 U/L",
                "alt": "41 U/L",
                "bilirubin": "1.1 mg/dL"
            },
            
            "cardiac": {
                "lvef": "52%",
                "ecg": "normal sinus rhythm"
            },
            
            "imaging": {
                "ct_findings": "Mild mediastinal and retroperitoneal lymphadenopathy (largest 2.1 cm). Mild splenomegaly. No pulmonary infiltrates."
            },
            
            "physical_exam": {
                "lymph_nodes": "bilateral cervical and supraclavicular up to 2.5 cm",
                "splenomegaly": "3 cm below costal margin",
                "ecchymoses": "scattered on forearms"
            },
            
            "summary": "46-year-old male with relapsed refractory B-cell ALL, originally diagnosed in 2022. Achieved CR with hyper-CVAD, consolidated with blinatumomab. Relapsed 2024 with 42% marrow blasts. Second-line inotuzumab yielded partial response but complicated by prolonged thrombocytopenia. Current BMBx shows 58% CD19+/CD22+ blasts with high-risk cytogenetics t(12;21) and IKZF1 deletion. Molecular: NRAS G12D, TP53 R248Q (5% VAF). No CNS disease. ECOG 1. Current cytopenias: Hgb 7.4, WBC 2.8K, Plt 61K. Adequate organ function for trial consideration."
        }
    ]
}

print("\n" + "="*70)
print("LOADING DATA WITH SKYFLOW TOKENS VISIBLE")
print("="*70)
print("\nSkyflow-protected fields (tokens shown as-is):")
print(f"  Patient Name: {data['studies'][0]['patient_name']}")
print(f"  MRN: {data['studies'][0]['patient_mrn']}")
print(f"  DOB: {data['studies'][0]['patient_dob']}")
print(f"  Phone: {data['studies'][0]['patient_phone']}")
print(f"  Address: {data['studies'][0]['patient_address']}")
print(f"  Physician: {data['studies'][0]['attending_physician']}")
print("\nNon-sensitive data (plaintext):")
print(f"  Age: {data['studies'][0]['age']}")
print(f"  Sex: {data['studies'][0]['sex']}")
print(f"  Diagnosis: {data['studies'][0]['diagnosis']}")
print(f"  ECOG: {data['studies'][0]['ecog_performance_status']}")
print("\nPosting to API...\n")

response = requests.post(
    'http://localhost:8000/api/load',
    json=data
)

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    result = response.json()
    print("[OK] SUCCESS")
    print(f"\nMessage: {result['message']}")
    print(f"Studies loaded: {result['studies_loaded']}")
    print(f"Skyflow protected: {result['skyflow_protected']}")
    print(f"Security: {result['security']}")
else:
    print("[ERROR] ERROR")
    print(response.text)

print("\n" + "="*70)