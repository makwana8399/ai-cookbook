import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

completion = client.chat.completions.create(
    model="meta-llama/llama-3-8b-instruct",
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {"role": "user", "content": "Write a limerick about the Python programming language."}
    ],
)

print(completion.choices[0].message.content)