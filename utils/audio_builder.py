import os
import asyncio
import edge_tts

VOICE_MAP = {
    "Narrator": "en-US-ChristopherNeural",
    "Mr. Dursley": "en-GB-RyanNeural",
    "Mrs. Dursley": "en-GB-SoniaNeural",
    "Harry": "en-GB-ThomasNeural",
    "Dumbledore": "en-US-GuyNeural",
    "McGonagall": "en-GB-SoniaNeural",
    "Default": "en-US-ChristopherNeural"
}

TEMP_STREAM_DIR = os.path.join("static", "temp_audio")
os.makedirs(TEMP_STREAM_DIR, exist_ok=True)

async def download_single_line(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def generate_audio_stream(screenplay_script):
    print(f"[STREAMING] Starting progressive transfer for {len(screenplay_script)} elements...")
    for index, line in enumerate(screenplay_script):
        speaker = line.get("speaker", "Default")
        text = line.get("text", "")
        selected_voice = VOICE_MAP.get(speaker, VOICE_MAP["Default"])
        temp_file_path = os.path.join(TEMP_STREAM_DIR, f"stream_line_{index}.mp3")
        try:
            asyncio.run(download_single_line(text, selected_voice, temp_file_path))
            if os.path.exists(temp_file_path):
                with open(temp_file_path, "rb") as f:
                    yield f.read()
                os.remove(temp_file_path)
        except Exception as e:
            print(f"[STREAM ERROR] Error on line index {index}: {e}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)