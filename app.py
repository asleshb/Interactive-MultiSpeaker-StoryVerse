import os
import json
import pdfplumber
from dotenv import load_dotenv
from gtts import gTTS
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response

load_dotenv()

# =========================================================================
# 📦 Utility Imports
# =========================================================================
from utils.chapter_extractor import extract_chapters
from utils.screenplay_engine import transform_page_to_screenplay
from utils.character_agent import get_character_response

# Dynamic streaming generator imported directly from your updated builder module
from utils.audio_builder import generate_audio_stream 

# =========================================================================
# ⚙️ Flask Configuration
# =========================================================================
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================================================================
# 🛠️ Helper Functions
# =========================================================================
def clean_book_headers(raw_text):
    """Simple cleaner to strip out headers like '8 Harry Potter' or 'The Boy Who Lived 9'"""
    cleaned_lines = []

    for line in raw_text.split("\n"):
        if (
            "harry potter" in line.lower()
            or "the boy who lived" in line.lower()
        ):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# =========================================================================
# 🛣️ Application Routes
# =========================================================================

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["book"]

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

    files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    return render_template("index.html", files=files)


@app.route("/book/<filename>/<int:page_num>")
def read_book(filename, page_num):
    screenplay_script = []
    txt_filename = f"chapter_{page_num}.txt"
    filepath = os.path.join("chapters", txt_filename)

    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            text = clean_book_headers(raw_text)
            screenplay_script = transform_page_to_screenplay(text)
        else:
            text = (
                f"Chapter file {txt_filename} not found. "
                "Please verify your extraction pipeline."
            )
    except Exception as e:
        text = f"Error reading chapter file: {e}"

    files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    total_pages = (
        len(os.listdir("chapters"))
        if os.path.exists("chapters")
        else 1
    )

    return render_template(
        "reader.html",
        filename=filename,
        text=text,
        screenplay=screenplay_script,
        page_num=page_num,
        total_pages=total_pages,
        files=files,
    )


@app.route("/api/character-chat", methods=["POST"])
def character_chat():
    data = request.json
    character_name = data.get("character")
    user_message = data.get("message")

    reply = get_character_response(character_name, user_message)
    return jsonify({"reply": reply})


@app.route("/listen/<filename>/<int:page_num>")
def listen_page(filename, page_num):
    txt_filepath = os.path.join("chapters", f"chapter_{page_num}.txt")
    json_dir = "chapter_data"
    json_path = os.path.join(json_dir, f"chapter_{page_num}.json")
    screenplay_script = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                screenplay_script = json.load(f).get("script", [])
        except Exception as e:
            print(f"Error reading JSON schema: {e}")
    if not screenplay_script and os.path.exists(txt_filepath):
        try:
            with open(txt_filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            cleaned_text = clean_book_headers(raw_text)
            screenplay_script = transform_page_to_screenplay(cleaned_text)
            os.makedirs(json_dir, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({"script": screenplay_script}, f, indent=4)
        except Exception as e:
            print(f"Error compiling script structure: {e}")
    return redirect(url_for("read_book", filename=filename, page_num=page_num, play_stream="true"))

@app.route("/api/stream-audio/<int:page_num>")
def stream_audio(page_num):
    json_path = os.path.join("chapter_data", f"chapter_{page_num}.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            screenplay_script = json.load(f).get("script", [])
        if screenplay_script:
            return Response(generate_audio_stream(screenplay_script), mimetype="audio/mp3")
    return Response("Audio script missing or empty", status=404)

# =========================================================================
# 🚀 Main Launch Control
# =========================================================================
if __name__ == "__main__":
    app.run(debug=True)