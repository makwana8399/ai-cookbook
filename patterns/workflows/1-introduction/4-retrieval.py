import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

def search_kb(question: str):
    with open("kb.json", "r", encoding="utf-8") as f:
        return json.load(f)

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Answer user questions from the internal knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    }
]

system_prompt = (
    "You are a helpful assistant that answers questions "
    "from the knowledge base about our e-commerce store."
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the return policy?"},
]

completion = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
    tools=tools,
)

tool_call = completion.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

kb_result = search_kb(**args)

messages.append(completion.choices[0].message)
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(kb_result),
    }
)

class KBResponse(BaseModel):
    answer: str = Field(description="Answer to the user's question")
    source: int = Field(description="Record id of the answer")

completion_2 = client.beta.chat.completions.parse(
    model="openai/gpt-4o-mini",
    messages=messages,
    response_format=KBResponse,
)

final = completion_2.choices[0].message.parsed

print("\nFINAL ANSWER:")
print("Answer:", final.answer)
print("Source ID:", final.source)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the weather in Tokyo?"},
]

completion_3 = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
)

print("\nNON-KB QUESTION:")
print(completion_3.choices[0].message.content)