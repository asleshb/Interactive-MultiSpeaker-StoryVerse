# import spacy


# class SentenceSplitter:
#     def __init__(self):
#         self.nlp = spacy.load("en_core_web_sm")

#     def split(self, text):
#         doc = self.nlp(text)

#         sentences = []

#         for sent in doc.sents:
#             sentence = sent.text.strip()

#             if sentence:
#                 sentences.append(sentence)

#         return sentences


import os
import json
import re
import spacy


class SentenceSplitter:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        self.chapter_folder = "chapters"

        self.output_folder = "sentence_data"

        os.makedirs(self.output_folder, exist_ok=True)


    def clean_text(self, text):

        text = re.sub(r"\n+", " ", text)

        text = re.sub(r"\s+", " ", text)

        text = text.strip()

        return text


    def split_chapter(self, chapter_text):

        chapter_text = self.clean_text(chapter_text)

        doc = self.nlp(chapter_text)

        sentences = []

        for index, sent in enumerate(doc.sents):

            sentence = sent.text.strip()

            if sentence:

                sentence_data = {
                    "sentence_id": index + 1,
                    "text": sentence
                }

                sentences.append(sentence_data)

        return sentences


    def process_all_chapters(self):

        files = sorted(os.listdir(self.chapter_folder))

        for file in files:

            if file.endswith(".txt"):

                chapter_path = os.path.join(
                    self.chapter_folder,
                    file
                )

                with open(
                    chapter_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    chapter_text = f.read()

                sentence_data = self.split_chapter(
                    chapter_text
                )

                output_name = file.replace(
                    ".txt",
                    ".json"
                )

                output_path = os.path.join(
                    self.output_folder,
                    output_name
                )

                with open(
                    output_path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        sentence_data,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                print(
                    f"{file} -> {output_name} saved successfully"
                )