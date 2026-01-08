import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",     # REQUIRED for free key
    "X-Title": "AI Cookbook Project"        # REQUIRED
}

payload = {
    "model": "meta-llama/llama-3-8b-instruct",  # ✅ FREE MODEL
    "messages": [
        {"role": "system", "content": "You're a helpful assistant."},
        {"role": "user", "content": "Write a limerick about the Python programming language."}
    ]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(" Error:", response.status_code)
    print(response.text)
    exit()

data = response.json()
print("\n RESPONSE:\n")
print(data["choices"][0]["message"]["content"])
