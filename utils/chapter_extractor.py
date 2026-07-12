import pdfplumber
import re
import json
import os


def extract_chapters(filepath):

    chapters = []

    chapter_pattern = re.compile(
        r".*CHAPTER\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY).*",
        re.IGNORECASE
    )

    with pdfplumber.open(filepath) as pdf:

        total_pages = len(pdf.pages)

        for page_num in range(total_pages):

            page = pdf.pages[page_num]

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for i, line in enumerate(lines):

                line = line.strip()

                if chapter_pattern.match(line):

                    title = ""

                    # Usually the next line contains the chapter title
                    if i + 1 < len(lines):
                        title = lines[i + 1].strip()

                    chapters.append({
                        "chapter_heading": line,
                        "name": title,
                        "start_page": page_num + 1
                    })

                    break

    # Calculate ending pages
    for i in range(len(chapters)-1):

        chapters[i]["end_page"] = chapters[i+1]["start_page"] - 1

    if chapters:
        chapters[-1]["end_page"] = total_pages

    # -----------------------------
    # Save chapters to JSON
    # -----------------------------

    book_name = os.path.splitext(
        os.path.basename(filepath)
    )[0]

    os.makedirs("chapter_data", exist_ok=True)

    json_path = os.path.join(
        "chapter_data",
        f"{book_name}.json"
    )

    with open(json_path, "w", encoding="utf-8") as f:

        json.dump(
            chapters,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"Chapter data saved to {json_path}")



    return chapters

def load_chapters(filepath):

    book_name = os.path.splitext(
        os.path.basename(filepath)
    )[0]

    json_path = os.path.join(
        "chapter_data",
        f"{book_name}.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:

        chapters = json.load(f)

    return chapters