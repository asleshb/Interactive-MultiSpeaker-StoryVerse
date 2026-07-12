# utils/screenplay_engine.py
import json
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize the cloud brain securely using your API Key
client = genai.Client()

class ScriptLine(BaseModel):
    speaker: str = Field(description="The character name or 'Narrator'.")
    text: str = Field(description="The spoken text or narration.")
    type: Literal["narration", "dialogue", "internal_thought"] = Field(description="Audio track category.")
    emotion: Literal["neutral", "happy", "angry", "confused", "whispered", "excited", "mysterious"] = Field(description="Emotional tone cue.")

class Screenplay(BaseModel):
    script: List[ScriptLine]

def transform_page_to_screenplay(raw_text: str) -> list:
    """Sends page-specific text chunks to Gemini to extract structural scripts."""
    if not raw_text or raw_text == "No text found on this page.":
        return []
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Convert this text snippet into a screenplay strictly adhering to the schema:\n\n{raw_text}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a Hollywood Screenplay Writer adapting a novel into an interactive audio drama script.\n"
                    "Do NOT just copy book sentences word-for-word. Instead, actively convert passive descriptions into active lines:\n"
                    "Rules:\n"
                    "1. REWRITE PASSIVE DESCRIPTIONS TO INTERNAL THOUGHTS: When a book describes a character's proud feelings, opinions, or regular mindset, change the speaker to that character. Rewrite the sentence into a first-person direct thought spoken out loud by them.\n"
                    "2. CLEAN NARRATION ONLY: The Narrator must ONLY speak clean sentences that describe scenery, size, appearance, or background movement. Keep these atmospheric.\n"
                    "3. STRIP DIALOGUE TAGS: Remove words like 'he muttered' or 'she said' from the actual spoken text track.\n"
                    "4. EMOTION TRACK: Match the character's line to a fitting emotion cue."
                ),
                response_mime_type="application/json",
                response_schema=Screenplay,
                temperature=0.1
            ),
        )
        parsed_json = json.loads(response.text)
        return parsed_json.get('script', [])
    except Exception as e:
        print(f"Gemini Screenplay Error: {e}")
        return []