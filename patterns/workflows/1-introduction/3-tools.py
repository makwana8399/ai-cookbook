import json
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

def get_weather(latitude: float, longitude: float):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,wind_speed_10m"
    )
    return response.json()["current"]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature in Celsius",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
            },
        },
    }
]

messages = [
    {"role": "system", "content": "You are a helpful weather assistant."},
    {"role": "user", "content": "What's the weather in Paris today?"},
]

completion = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
    tools=tools,
)

tool_call = completion.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

weather_data = get_weather(**args)

print("\nRAW OUTPUT:\n", weather_data)

messages.append(completion.choices[0].message)
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(weather_data),
    }
)

class WeatherResponse(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    response: str

completion_2 = client.beta.chat.completions.parse(
    model="openai/gpt-4o-mini",
    messages=messages,
    response_format=WeatherResponse,
)

final = completion_2.choices[0].message.parsed

print("\nFINAL RESULT:")
print("Temperature:", final.temperature)
print("Response:", final.response)