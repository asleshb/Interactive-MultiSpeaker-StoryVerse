import os
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# 1. Define the exact structure for a single line of your script
class ScriptLine(BaseModel):
    speaker: str = Field(description="The character name or 'Narrator'.")
    text: str = Field(description="The spoken text or narration. Do NOT invent new text.")
    type: Literal["narration", "dialogue", "internal_thought"] = Field(description="Audio track delivery category.")
    emotion: Literal["neutral", "happy", "angry", "confused", "whispered", "excited", "mysterious"] = Field(description="Emotional tone cue.")

# 2. Define the container for the final array
class Screenplay(BaseModel):
    script: List[ScriptLine]

# 3. Connect to Google AI Studio using your API key
# Get a free key from https://aistudio.google.com/
# Set it in your terminal environment variables: set GEMINI_API_KEY="your_key"


raw_book_text = """
 Harry Potter
happily as she wrestled a screaming Dudley into his high chair.
None of them noticed a large tawny owl flutter past the window.
At half past eight, Mr Dursley picked up his briefcase, pecked
Mrs Dursley on the cheek and tried to kiss Dudley goodbye but
missed, because Dudley was now having a tantrum and throwing
his cereal at the walls. ‘Little tyke,’ chortled Mr Dursley as he left
the house. He got into his car and backed out of number four’s
drive.
It was on the corner of the street that he noticed the first sign
of something peculiar – a cat reading a map. For a second, Mr
Dursley didn’t realise what he had seen – then he jerked his head
around to look again. There was a tabby cat standing on the corner
of Privet Drive, but there wasn’t a map in sight. What could
he have been thinking of? It must have been a trick of the light.
Mr Dursley blinked and stared at the cat. It stared back. As Mr
Dursley drove around the corner and up the road, he watched the
cat in his mirror. It was now reading the sign that said Privet Drive
– no, looking at the sign; cats couldn’t read maps or signs. Mr
Dursley gave himself a little shake and put the cat out of his
mind. As he drove towards town he thought of nothing except a
large order of drills he was hoping to get that day.
But on the edge of town, drills were driven out of his mind by
something else. As he sat in the usual morning traffic jam, he
couldn’t help noticing that there seemed to be a lot of strangely
dressed people about. People in cloaks. Mr Dursley couldn’t bear
people who dressed in funny clothes – the get-ups you saw on
young people! He supposed this was some stupid new fashion. He
drummed his fingers on the steering wheel and his eyes fell on a
huddle of these weirdos standing quite close by. They were whis-
pering excitedly together. Mr Dursley was enraged to see that a
couple of them weren’t young at all; why, that man had to be older
than he was, and wearing an emerald-green cloak! The nerve of
him! But then it struck Mr Dursley that this was probably some
silly stunt – these people were obviously collecting for something
… yes, that would be it. The traffic moved on, and a few minutes
later, Mr Dursley arrived in the Grunnings car park, his mind
back on drills.
Mr Dursley always sat with his back to the window in his office
on the ninth floor. If he hadn’t, he might have found it harder to
concentrate on drills that morning. He didn’t see the owls
"""

print("🎬 The Google Cloud Engine is processing your text structurally... Please wait...\n")

# 4. Execute structural screenplay transformation using Gemini 1.5 Flash
response = client.models.generate_content(
    model='gemini-2.5-flash', # Blazing fast and completely free
    contents=f"Convert this text snippet into a screenplay strictly adhering to the schema:\n\n{raw_book_text}",
    config=types.GenerateContentConfig(
        # The system instructions dictate your specific script rules
     system_instruction=(
            "You are a Hollywood Screenplay Writer adapting a novel into an interactive audio drama script.\n"
            "Do NOT just copy book sentences word-for-word. Instead, actively convert passive descriptions into active lines:\n\n"
            "Rules:\n"
            "1. REWRITE PASSIVE DESCRIPTIONS TO INTERNAL THOUGHTS: When a book describes a character's proud feelings, opinions, or regular mindset, change the speaker to that character. Rewrite the sentence into a first-person direct thought spoken out loud by them (e.g., Change 'They were proud to be normal' to 'We are perfectly normal, thank you very much!').\n"
            "2. CLEAN NARRATION ONLY: The Narrator must ONLY speak clean sentences that describe scenery, size, appearance, or background movement (e.g., 'Mr Dursley was the director of a firm called Grunnings...'). Keep these atmospheric.\n"
            "3. STRIP DIALOGUE TAGS: Remove words like 'he muttered' or 'she said' from the actual spoken text track.\n"
            "4. EMOTION TRACK: Match the character's line to a fitting emotion cue. For example, if they are proud of being normal, set emotion to 'excited' or 'neutral'."
        ),
        # This tells Google AI Studio to strictly force the output into your Pydantic schema
        response_mime_type="application/json",
        response_schema=Screenplay,
        temperature=0.1 # Keeps the model highly precise and rule-following
    ),
)

# 5. Output the beautiful, validated JSON array
print(response.text)


