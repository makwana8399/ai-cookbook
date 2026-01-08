from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
import os, json, logging
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

model = "mistralai/mistral-7b-instruct"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class EventExtraction(BaseModel):
    description: str
    is_calendar_event: bool
    confidence_score: float

class EventDetails(BaseModel):
    name: str
    date: str
    duration_minutes: int
    participants: list[str]

class EventConfirmation(BaseModel):
    confirmation_message: str
    calendar_link: Optional[str] = None

def safe_json(text: str) -> dict:
    """Extract JSON safely from LLM output"""
    start = text.find("{")
    end = text.rfind("}")
    return json.loads(text[start:end + 1])

def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Extracting event intent")

    today = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""
Today is {today}.
Analyze the text and respond ONLY in JSON.

Format:
{{
  "description": "...",
  "is_calendar_event": true/false,
  "confidence_score": 0.0-1.0
}}

Text:
{user_input}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    data = safe_json(completion.choices[0].message.content)
    return EventExtraction(**data)

def parse_event_details(description: str) -> EventDetails:
    logger.info("Parsing event details")

    today = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""
Today is {today}.
Extract event details and respond ONLY in JSON.

Format:
{{
  "name": "...",
  "date": "ISO 8601",
  "duration_minutes": 60,
  "participants": ["Alice", "Bob"]
}}

Text:
{description}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    data = safe_json(completion.choices[0].message.content)
    return EventDetails(**data)

def generate_confirmation(details: EventDetails) -> EventConfirmation:
    logger.info("Generating confirmation")

    prompt = f"""
Create a friendly confirmation message.
Sign off as Susie.

Event:
{details.model_dump()}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return EventConfirmation(
        confirmation_message=completion.choices[0].message.content.strip()
    )

def process_calendar_request(user_input: str) -> Optional[EventConfirmation]:
    extraction = extract_event_info(user_input)

    if not extraction.is_calendar_event or extraction.confidence_score < 0.7:
        logger.warning("Gate check failed")
        return None

    details = parse_event_details(extraction.description)
    return generate_confirmation(details)

print("\n--- VALID INPUT ---")
result = process_calendar_request(
    "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob."
)
if result:
    print(result.confirmation_message)
else:
    print("Not a calendar event.")

print("\n--- INVALID INPUT ---")
result = process_calendar_request(
    "Can you send an email to Alice and Bob?"
)
if result:
    print(result.confirmation_message)
else:
    print("Not a calendar event.")