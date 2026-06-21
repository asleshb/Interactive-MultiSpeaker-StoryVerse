import os
import pdfplumber
from gtts import gTTS
from flask import Flask, render_template, request, redirect, url_for
from utils.chapter_extractor import extract_chapters


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

@app.route("/book/<filename>/<int:page_num>")
def read_book(filename, page_num):

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    text = ""

    try:

        with pdfplumber.open(filepath) as pdf:

            total_pages = len(pdf.pages)

            if page_num < 1:
                page_num = 1

            if page_num > total_pages:
                page_num = total_pages

            page = pdf.pages[page_num - 1]

            text = page.extract_text()

            if text is None:
                text = "No text found on this page."

    except Exception as e:

        text = f"Unable to read PDF.\n\nError:\n{e}"

        total_pages = 1

    # Get all uploaded books for sidebar
    files = os.listdir(UPLOAD_FOLDER)

    return render_template(
        "reader.html",
        filename=filename,
        text=text,
        page_num=page_num,
        total_pages=total_pages,
        files=files
    )


@app.route("/listen/<filename>/<int:page_num>")
def listen_page(filename, page_num):

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    text = ""

    with pdfplumber.open(filepath) as pdf:

        page = pdf.pages[page_num - 1]

        text = page.extract_text()

    tts = gTTS(text)

    audio_path = os.path.join("static", "audio.mp3")

    tts.save(audio_path)

    return redirect(url_for(
        "read_book",
        filename=filename,
        page_num=page_num
    ))

# @app.route("/analyze")
# def analyze():

#     filepath = "uploads/sherlock.pdf"

#     chapter_text = extract_chapter(
#         filepath,
#         1,
#         5
#     )

#     sentences = split_sentences(chapter_text)

#     chapter = build_chapter(sentences)

#     characters = extract_characters(chapter_text)

#     return render_template(
#         "chapter_analysis.html",
#         chapter=chapter,
#         characters=characters
#     )


@app.route("/chapters")
def chapters():

    chapters = extract_chapters(
        "uploads/harry-potter.pdf"
    )

    return str(chapters)



if __name__ == "__main__":
    app.run(debug=True)