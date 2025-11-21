# post_skyflow_data.py

import requests
import json

# Your Skyflow-protected data
skyflow_data = {
    "condition": "leukemia",
    "studies": [
        {
            "nct_id": "NCT12345",
            "title": "B-cell ALL Treatment Study",
            "status": "RECRUITING",
            "phase": ["PHASE3"],
            "conditions": ["B-cell Acute Lymphoblastic Leukemia"],
            "lead_sponsor": "[NAME_VGMgLRv]",  # Skyflow token
            "investigators": ["[NAME_Jgf3GNQ]", "[NAME_BuVLer5]"],  # Skyflow tokens
            "sites": ["[LOCATION_ADDRESS_STREET_S5USJli], Columbus, OH"],  # Skyflow token
            "patient_data": {
                "mrn": "[HEALTHCARE_NUMBER_tKNCgm6]",  # Skyflow token
                "dob": "[DOB_gCXQIV6]",  # Skyflow token
                "age": 46,
                "sex": "Male",
                "phone": "[PHONE_NUMBER_46UXbal]"  # Skyflow token
            },
            "medical_history": {
                "diagnosis": "Relapsed refractory B-ALL",
                "blasts_percentage": 58,
                "cytogenetics": "t(12;21)(p13;q22), IKZF1 deletion",
                "mutations": "NRAS G12D, TP53 R248Q"
            },
            "current_status": {
                "symptoms": ["fatigue", "night sweats", "lymphadenopathy"],
                "performance_status": "ECOG 1"
            },
            "summary": "46M with relapsed refractory B-ALL, previously treated with hyper-CVAD and blinatumomab. Current bone marrow shows 58% blasts with high-risk cytogenetics."
        }
    ]
}

# POST to your API
print("Posting Skyflow-protected data to API...")

response = requests.post(
    'http://localhost:8000/api/load',
    json=skyflow_data
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n✓ Data loaded successfully!")
    print("\nNow you can:")
    print("1. Get studies: curl http://localhost:8000/api/studies")
    print('2. Ask Claude: curl -X POST http://localhost:8000/api/ask -H "Content-Type: application/json" -d \'{"question":"Analyze this leukemia case"}\'')
else:
    print(f"\n✗ Error loading data")