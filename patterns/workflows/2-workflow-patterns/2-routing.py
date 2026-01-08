from typing import Optional, Literal
from pydantic import BaseModel
from openai import OpenAI
import os, json, logging
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

model = "mistralai/mistral-7b-instruct"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarRequestType(BaseModel):
    request_type: Literal["new_event", "modify_event", "other"]
    confidence_score: float
    description: str

class NewEventDetails(BaseModel):
    name: str
    date: str
    duration_minutes: int
    participants: list[str]

class Change(BaseModel):
    field: str
    new_value: str

class ModifyEventDetails(BaseModel):
    event_identifier: str
    changes: list[Change]
    participants_to_add: list[str]
    participants_to_remove: list[str]

class CalendarResponse(BaseModel):
    success: bool
    message: str
    calendar_link: Optional[str] = None

def extract_json(text: str):
    try:
        start = text.index("{")
        end = text.rindex("}")
        return json.loads(text[start:end + 1])
    except Exception:
        return None

def llm_json(prompt: str, fallback: dict):
    res = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Respond ONLY with valid JSON. No text, no explanation."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    data = extract_json(res.choices[0].message.content)
    return data if data else fallback

def route_calendar_request(user_input: str) -> CalendarRequestType:
    data = llm_json(
        f"""
Return JSON only.

{{
  "request_type": "new_event | modify_event | other",
  "confidence_score": 0.0,
  "description": ""
}}

Text:
{user_input}
""",
        {
            "request_type": "other",
            "confidence_score": 0.0,
            "description": ""
        }
    )
    return CalendarRequestType(**data)

def handle_new_event(description: str) -> CalendarResponse:
    data = llm_json(
        f"""
Return JSON only.

{{
  "name": "",
  "date": "",
  "duration_minutes": 60,
  "participants": []
}}

Text:
{description}
""",
        {
            "name": "event",
            "date": "",
            "duration_minutes": 60,
            "participants": []
        }
    )

    d = NewEventDetails(**data)

    return CalendarResponse(
        success=True,
        message=f"Created event '{d.name}' on {d.date} with {', '.join(d.participants)}",
        calendar_link=f"calendar://new?event={d.name}",
    )

def handle_modify_event(description: str) -> CalendarResponse:
    data = llm_json(
        f"""
Return JSON only.

{{
  "event_identifier": "",
  "changes": [],
  "participants_to_add": [],
  "participants_to_remove": []
}}

Text:
{description}
""",
        {
            "event_identifier": "",
            "changes": [],
            "participants_to_add": [],
            "participants_to_remove": []
        }
    )

    d = ModifyEventDetails(**data)

    return CalendarResponse(
        success=True,
        message=f"Modified event '{d.event_identifier}'",
        calendar_link=f"calendar://modify?event={d.event_identifier}",
    )

def process_calendar_request(user_input: str) -> Optional[CalendarResponse]:
    route = route_calendar_request(user_input)

    if route.confidence_score < 0.7:
        return None

    if route.request_type == "new_event":
        return handle_new_event(route.description)

    if route.request_type == "modify_event":
        return handle_modify_event(route.description)

    return None

inputs = [
    "Let's schedule a team meeting next Tuesday at 2pm with Alice and Bob",
    "Move the team meeting with Alice and Bob to Wednesday at 3pm",
    "What's the weather like today?"
]

for text in inputs:
    result = process_calendar_request(text)
    if result:
        print(result.message)
    else:
        print("Request not recognized")