import os
from dotenv import load_dotenv
load_dotenv()

import json
import pdfplumber
from gtts import gTTS
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Import your utility helper engines cleanly (including the multi-voice engine!)
from utils.chapter_extractor import extract_chapters
from utils.screenplay_engine import transform_page_to_screenplay
from utils.character_agent import get_character_response
from utils.voice_engine import build_multi_voice_audio  # <-- Fixed NameError

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["book"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files=files)


def clean_book_headers(raw_text):
    """Simple cleaner to strip out headers like '8 Harry Potter' or 'The Boy Who Lived 9'"""
    cleaned_lines = []
    for line in raw_text.split('\n'):
        if "harry potter" in line.lower() or "the boy who lived" in line.lower():
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

@app.route("/book/<filename>/<int:page_num>")
def read_book(filename, page_num):
    screenplay_script = []
    
    # Target file paths (Consider standardizing these to page numbers to avoid file mismatches)
    txt_filename = f"chapter_{page_num}.txt"
    filepath = os.path.join("chapters", txt_filename)

    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            text = clean_book_headers(raw_text)
            screenplay_script = transform_page_to_screenplay(text)
        else:
            text = f"Chapter file {txt_filename} not found. Please verify your extraction pipeline."
            
    except Exception as e:
        text = f"Error reading chapter file: {e}"

    files = os.listdir(UPLOAD_FOLDER)
    total_pages = len(os.listdir("chapters")) if os.path.exists("chapters") else 1

    return render_template(
        "reader.html",
        filename=filename,
        text=text,
        screenplay=screenplay_script, 
        page_num=page_num,
        total_pages=total_pages,
        files=files
    )

@app.route("/api/character-chat", methods=["POST"])
def character_chat():
    """Live JSON API mapping endpoint matching your reader.html fetch structure."""
    data = request.json
    character_name = data.get("character")
    user_message = data.get("message")
    
    reply = get_character_response(character_name, user_message)
    return jsonify({"reply": reply})


@app.route("/listen/<filename>/<int:page_num>")
def listen_page(filename, page_num):
    mode = request.args.get('mode', 'book') 
    txt_filepath = os.path.join("chapters", f"chapter_{page_num}.txt")
    json_path = os.path.join("chapter_data", f"chapter_{page_num}.json")

    if mode == 'screenplay':
        screenplay_script = []
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                screenplay_script = json.load(f).get("script", [])
        
        final_audio_path = os.path.join("static", "screenplay_drama.mp3")
        if screenplay_script:
            # Safely executes now that it's imported at the top layer
            build_multi_voice_audio(screenplay_script, final_audio_path)
        else:
            import edge_tts
            import asyncio
            asyncio.run(edge_tts.Communicate("Please load screenplay tab text first.", "en-US-ChristopherNeural").save(final_audio_path))
    else:
        text = ""
        if os.path.exists(txt_filepath):
            with open(txt_filepath, "r", encoding="utf-8") as f:
                text = clean_book_headers(f.read())
        if not text.strip(): text = "No text available."
        
        final_audio_path = os.path.join("static", "book_narrator.mp3")
        import edge_tts
        import asyncio
        asyncio.run(edge_tts.Communicate(text, "en-US-ChristopherNeural").save(final_audio_path))

    return redirect(url_for("read_book", filename=filename, page_num=page_num))

@app.route("/chapters")
def chapters():
    # Make sure this utility function returns a clean string or list matching your view requirements
    chapters_list = extract_chapters("uploads/harry-potter.pdf")
    return str(chapters_list)


if __name__ == "__main__":
    app.run(debug=True)

    

# # app.py
# import os
# import pdfplumber
# from gtts import gTTS
# from flask import Flask, render_template, request, redirect, url_for, jsonify

# # Import your newly structured utility helper engines cleanly!
# from utils.chapter_extractor import extract_chapters
# from utils.screenplay_engine import transform_page_to_screenplay
# from utils.character_agent import get_character_response

# app = Flask(__name__)
# UPLOAD_FOLDER = "uploads"

# @app.route("/", methods=["GET", "POST"])
# def home():
#     if request.method == "POST":
#         file = request.files["book"]
#         if file:
#             filepath = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(filepath)
#     files = os.listdir(UPLOAD_FOLDER)
#     return render_template("index.html", files=files)


# def clean_book_headers(raw_text):
#     """Simple cleaner to strip out headers like '8 Harry Potter' or 'The Boy Who Lived 9'"""
#     cleaned_lines = []
#     for line in raw_text.split('\n'):
#         # Ignore lines that are just headers or page tracks
#         if "harry potter" in line.lower() or "the boy who lived" in line.lower():
#             continue
#         cleaned_lines.append(line)
#     return "\n".join(cleaned_lines)

# @app.route("/book/<filename>/<int:page_num>")
# def read_book(filename, page_num):
#     screenplay_script = []
    
#     # 1. Look for your pre-extracted text file directly (e.g., chapters/chapter_1.txt)
#     txt_filename = f"chapter_{page_num}.txt"
#     filepath = os.path.join("chapters", txt_filename)

#     try:
#         if os.path.exists(filepath):
#             with open(filepath, "r", encoding="utf-8") as f:
#                 raw_text = f.read()
            
#             # 2. Strip out page numbers and book headers (e.g., '8 Harry Potter')
#             text = clean_book_headers(raw_text)
            
#             # 3. Pass clean story text to screenplay cook file (screenplay_engine.py)
#             screenplay_script = transform_page_to_screenplay(text)
#         else:
#             text = f"Chapter file {txt_filename} not found. Please run your extraction script first."
            
#     except Exception as e:
#         text = f"Error reading chapter file: {e}"

#     # Get file list for your sidebar
#     files = os.listdir(UPLOAD_FOLDER)
    
#     # Calculate how many chapter files you have inside the folder
#     total_pages = len(os.listdir("chapters")) if os.path.exists("chapters") else 1

#     # 4. Render everything to your reader template tab panes
#     return render_template(
#         "reader.html",
#         filename=filename,
#         text=text,
#         screenplay=screenplay_script, 
#         page_num=page_num,
#         total_pages=total_pages,
#         files=files
#     )

# @app.route("/api/character-chat", methods=["POST"])
# def character_chat():
#     """Live JSON API mapping endpoint matching your reader.html fetch structure."""
#     data = request.json
#     character_name = data.get("character")
#     user_message = data.get("message")
    
#     # Offload the prompt generation to our character agent utility file
#     reply = get_character_response(character_name, user_message)
#     return jsonify({"reply": reply})


# @app.route("/listen/<filename>/<int:page_num>")
# def listen_page(filename, page_num):
#     mode = request.args.get('mode', 'book') 
#     txt_filepath = os.path.join("chapters", f"chapter_{page_num}.txt")
#     json_path = os.path.join("chapter_data", f"chapter_{page_num}.json")

#     if mode == 'screenplay':
#         screenplay_script = []
#         if os.path.exists(json_path):
#             with open(json_path, "r", encoding="utf-8") as f:
#                 screenplay_script = json.load(f).get("script", [])
        
#         final_audio_path = os.path.join("static", "screenplay_drama.mp3")
#         if screenplay_script:
#             build_multi_voice_audio(screenplay_script, final_audio_path)
#         else:
#             import edge_tts
#             import asyncio
#             asyncio.run(edge_tts.Communicate("Please load screenplay tab text first.", "en-US-ChristopherNeural").save(final_audio_path))
#     else:
#         text = ""
#         if os.path.exists(txt_filepath):
#             with open(txt_filepath, "r", encoding="utf-8") as f:
#                 text = clean_book_headers(f.read())
#         if not text.strip(): text = "No text available."
        
#         final_audio_path = os.path.join("static", "book_narrator.mp3")
#         import edge_tts
#         import asyncio
#         asyncio.run(edge_tts.Communicate(text, "en-US-ChristopherNeural").save(final_audio_path))

#     return redirect(url_for("read_book", filename=filename, page_num=page_num))

# @app.route("/chapters")
# def chapters():
#     chapters = extract_chapters("uploads/harry-potter.pdf")
#     return str(chapters)


# if __name__ == "__main__":
#     app.run(debug=True)
