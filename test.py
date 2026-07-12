import os
import sys

# 1. Inject the folder directly into the script's active runtime path environment
# This guarantees pydub finds it the absolute millisecond it initializes!
ffmpeg_dir = r"C:\ffmpeg\ffmpeg-8.1.2-essentials_build\bin"
if os.path.exists(ffmpeg_dir):
    os.environ["PATH"] += os.pathsep + ffmpeg_dir
    print(f"[ENVIRONMENT SET] Added {ffmpeg_dir} to runtime PATH.")
else:
    print(f"[ENVIRONMENT ERROR] Could not find folder: {ffmpeg_dir}")
    sys.exit(1)

# 2. NOW it is safe to import pydub (Warnings will vanish!)
import asyncio
import edge_tts
from pydub import AudioSegment

print("--- STARTING ISOLATED EDGE-TTS MULTI-VOICE TEST ---")

# Explicit fallback assignments (Good practice to keep alongside environment patch)
ffmpeg_actual_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
ffprobe_actual_path = os.path.join(ffmpeg_dir, "ffprobe.exe")

if os.path.exists(ffmpeg_actual_path) and os.path.exists(ffprobe_actual_path):
    AudioSegment.converter = ffmpeg_actual_path
    AudioSegment.ffprobe = ffprobe_actual_path
    print("[FFMPEG CHECK] Success! Connected explicitly to ffmpeg and ffprobe binaries.")
else:
    print("[FFMPEG CHECK] Error! Files missing inside the directory.")
    sys.exit(1)

# --- The rest of your script remains exactly the same ---
test_screenplay = [
    {"speaker": "Narrator", "text": "The dark, quiet street of Privet Drive was completely still."},
    {"speaker": "Mr. Dursley", "text": "What is going on out there? Who is whispering at this hour?!"},
    {"speaker": "Dumbledore", "text": "I should have known you would be here, Professor McGonagall."},
    {"speaker": "Mrs. Dursley", "text": "Oh dear, I hope the neighbors didn't hear that mechanical rumble."},
    {"speaker": "Narrator", "text": "A sudden low breeze swept over the clean stone walls."}
]

VOICE_MAP = {
    "Narrator": "en-US-ChristopherNeural",
    "Mr. Dursley": "en-GB-RyanNeural",
    "Mrs. Dursley": "en-GB-SoniaNeural",
    "Dumbledore": "en-US-GuyNeural",
    "Default": "en-US-ChristopherNeural"
}

async def generate_line_audio(text, speaker, temp_path):
    selected_voice = VOICE_MAP.get(speaker, VOICE_MAP["Default"])
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(temp_path)

def run_audio_pipeline():
    temp_files = []
    
    for idx, line in enumerate(test_screenplay):
        speaker = line["speaker"]
        text = line["text"]
        temp_line_path = f"temp_line_{idx}.mp3"
        
        print(f"-> edge-tts calling voice for: {speaker:12} | Text: '{text[:30]}...'")
        asyncio.run(generate_line_audio(text, speaker, temp_line_path))
        temp_files.append(temp_line_path)

    print("\n[STITCHING] Handing the clips over to FFmpeg to glue back-to-back...")
    combined_audio = AudioSegment.empty()
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            segment = AudioSegment.from_mp3(file_path)
            combined_audio += segment + AudioSegment.silent(duration=400)

    output_file = "test_output.mp3"
    combined_audio.export(output_file, format="mp3")
    print(f"[SUCCESS] Multi-voice file created! Saved as: '{output_file}'")

    for file_path in temp_files:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    run_audio_pipeline()