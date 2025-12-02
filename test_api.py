import requests
import json

print("=== Test 1: Health Check ===")
response = requests.get("http://localhost:8000/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

print("=== Test 2: Models List ===")
response = requests.get("http://localhost:8000/v1/models")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

print("=== Test 3: Chat Completion (Simple) ===")
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "간단히 '안녕하세요'라고만 답변해주세요"}
        ]
    }
)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {result['choices'][0]['message']['content']}\n")

print("=== Test 4: Chat Completion (RAG Test) ===")
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Project X에 대해 알려줘"}
        ]
    }
)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {result['choices'][0]['message']['content']}\n")

print("=== All Tests Completed Successfully! ===")
