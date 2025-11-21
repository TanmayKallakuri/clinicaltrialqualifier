# ask_claude_test.py

import requests
import json

print("Asking Claude to analyze the leukemia case...\n")

response = requests.post(
    'http://localhost:8000/api/ask',
    json={
        "question": "Analyze this relapsed refractory B-ALL case. What are the key clinical features, treatment challenges based on the patient's history with hyper-CVAD, blinatumomab, and inotuzumab? What type of clinical trial would be most appropriate for this patient?"
    }
)

if response.status_code == 200:
    result = response.json()
    
    print("="*70)
    print("CLAUDE'S ANALYSIS")
    print("="*70)
    print()
    print(result['answer'])
    print()
    print("="*70)
    print(f"Model: {result['model']}")
    print(f"Studies analyzed: {result['analyzed_studies']} / {result['total_studies']}")
    print(f"Security: {result['security']}")
    print("="*70)
else:
    print(f"[ERROR] Error {response.status_code}")
    print(response.text)