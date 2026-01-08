from typing import List, Dict
from pydantic import BaseModel
from openai import OpenAI
import os, json, logging, re
from dotenv import load_dotenv

# ------------------ SETUP ------------------
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Free + stable model
model = "mistralai/mistral-7b-instruct"

# ------------------ MODELS ------------------
class SubTask(BaseModel):
    section_type: str
    description: str
    style_guide: str
    target_length: int

class OrchestratorPlan(BaseModel):
    topic_analysis: str
    target_audience: str
    sections: List[SubTask]

class SectionContent(BaseModel):
    content: str
    key_points: List[str]

class SuggestedEdits(BaseModel):
    section_name: str
    suggested_edit: str

class ReviewFeedback(BaseModel):
    cohesion_score: float
    suggested_edits: List[SuggestedEdits]
    final_version: str

# ------------------ SAFE JSON ------------------
def safe_json_load(text: str):
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return json.loads(text)

def extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return safe_json_load(match.group(0))

def llm_json(prompt: str, retries: int = 1):
    for attempt in range(retries + 1):
        res = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Reply ONLY with valid JSON. No explanations."
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = res.choices[0].message.content
        try:
            return extract_json(content)
        except Exception:
            if attempt == retries:
                raise
            logger.warning("Retrying due to JSON error...")

# ------------------ ORCHESTRATOR ------------------
class BlogOrchestrator:
    def __init__(self):
        self.sections_content = {}

    def get_plan(self, topic, target_length, style):
        data = llm_json(f"""
Create a blog plan in JSON.

Format:
{{
  "topic_analysis": "...",
  "target_audience": "...",
  "sections": [
    {{
      "section_type": "Introduction",
      "description": "...",
      "style_guide": "...",
      "target_length": 200
    }}
  ]
}}

Topic: {topic}
Target Length: {target_length}
Style: {style}
""")
        return OrchestratorPlan(**data)

    def write_section(self, topic, section):
        data = llm_json(f"""
Write ONE blog section in JSON.

Format:
{{
  "content": "...",
  "key_points": ["...", "..."]
}}

Topic: {topic}
Section Type: {section.section_type}
Goal: {section.description}
Style: {section.style_guide}
Target Length: {section.target_length}
""")
        return SectionContent(**data)

    def review_post(self, topic, audience):
        combined = "\n\n".join(
            f"{k}:\n{v.content}" for k, v in self.sections_content.items()
        )

        data = llm_json(f"""
Review and polish blog in JSON.

Format:
{{
  "cohesion_score": 0.0,
  "suggested_edits": [
    {{
      "section_name": "...",
      "suggested_edit": "..."
    }}
  ],
  "final_version": "FULL BLOG HERE"
}}

Topic: {topic}
Audience: {audience}
Content:
{combined}
""", retries=2)

        return ReviewFeedback(**data)

    def write_blog(self, topic, target_length=1000, style="informative"):
        plan = self.get_plan(topic, target_length, style)
        logger.info(f"Planned {len(plan.sections)} sections")

        for section in plan.sections:
            logger.info(f"Writing section: {section.section_type}")
            self.sections_content[section.section_type] = self.write_section(topic, section)

        logger.info("Reviewing full blog")
        review = self.review_post(topic, plan.target_audience)

        return {
            "structure": plan,
            "sections": self.sections_content,
            "review": review,
        }

# ------------------ RUN ------------------
if __name__ == "__main__":
    orchestrator = BlogOrchestrator()

    topic = "The impact of AI on software development"
    result = orchestrator.write_blog(
        topic=topic,
        target_length=1200,
        style="technical but accessible",
    )

    print("\n================ FINAL BLOG ================\n")
    print(result["review"].final_version)
    print("\nCohesion Score:", result["review"].cohesion_score)