import os
import re
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: List[str]

completion = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",
    messages=[
        {
            "role": "system",
            "content": (
                "Extract event info.\n"
                "Return ONLY a valid JSON object with keys:\n"
                "name, date, participants\n"
                "No markdown, no extra text."
            ),
        },
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
)

raw_output = completion.choices[0].message.content
print("RAW OUTPUT:\n", raw_output)

clean = re.sub(r"</?s>|```json|```", "", raw_output).strip()

match = re.search(r"\{.*\}", clean, re.DOTALL)
if not match:
    raise ValueError("No JSON object found in model output")

json_text = match.group()

event = CalendarEvent.model_validate_json(json_text)

print("\nPARSED RESULT:")
print("Name:", event.name)
print("Date:", event.date)
print("Participants:", event.participants)