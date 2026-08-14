import json
import requests
import os

def run_evals():
    cases_path = os.path.join(os.path.dirname(__file__), 'cases.json')
    with open(cases_path, 'r') as f:
        cases = json.load(f)

    url = "http://127.0.0.1:8000/api/v1/triage"
    headers = {"Content-Type": "application/json"}
    
    score = 0
    total = len(cases)
    
    print("Starting LLM Evaluation...\n")
    
    for case in cases:
        payload = {"text": case["input"]}
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data["category"] == case["expected_category"]:
                print(f"✅ Case {case['id']} PASS")
                score += 1
            else:
                print(f"❌ Case {case['id']} FAIL: Expected {case['expected_category']}, got {data['category']}")
        except Exception as e:
            print(f"❌ Case {case['id']} FAIL (Error): {e}")
            
    print(f"\nScore: {score} out of {total}")

if __name__ == "__main__":
    run_evals()
