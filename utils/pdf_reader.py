import pdfplumber
import os


def extract_chapter_text(filepath, start_page, end_page, chapter_number):

    chapter_text = ""

    with pdfplumber.open(filepath) as pdf:

        for page_num in range(start_page-1, end_page):

            page = pdf.pages[page_num]

            text = page.extract_text()

            if text:
                chapter_text += text
                chapter_text += "\n\n"

    # Save chapter
    filename = f"chapter_{chapter_number}.txt"

    save_path = os.path.join(
        "chapters",
        filename
    )

    with open(save_path, "w", encoding="utf-8") as f:

        f.write(chapter_text)

    return chapter_text  