# utils/character_agent.py
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

def get_character_response(character_name: str, user_question: str) -> str:
    """Generates authentic in-character conversational chat responses."""
    system_prompt = (
        f"You are the character {character_name} from the book chapter currently being read.\n"
        "Talk directly to the reader in your authentic character voice. Keep your answer under 3 sentences.\n"
        "Do not break character. Do not say you are an AI assistant."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7 # Higher temperature lets personalities shine through!
            )
        )
        return response.text
    except Exception as e:
        return f"Could not contact character memory. Error: {str(e)}"