import os
import json
import spacy


class SpeakerIdentifier:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        self.input_folder = "dialogue_data"

        self.output_folder = "speaker_data"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        self.previous_speaker = "Narrator"

        self.speech_verbs = {

            "say",
            "ask",
            "reply",
            "answer",
            "whisper",
            "shout",
            "cry",
            "yell",
            "murmur",
            "exclaim",
            "remark",
            "continue",
            "add",
            "call",
            "announce",
            "insist",
            "admit",
            "suggest",
            "warn",
            "promise",
            "explain",
            "agree",
            "complain",
            "laugh",
            "sob",
            "gasp",
            "grumble"
        }


    def find_speaker(self, sentence, is_dialogue):

        if not is_dialogue:

            self.previous_speaker = "Narrator"

            return "Narrator"


        doc = self.nlp(sentence)


        # Method 1
        # Dependency Parsing + POS Tagging + Lemmatization

        for token in doc:

            if (
                token.lemma_.lower() in self.speech_verbs
                and token.pos_ == "VERB"
            ):

                for child in token.children:

                    if child.dep_ == "nsubj":

                        self.previous_speaker = child.text

                        return child.text


        # Method 2
        # Named Entity Recognition

        for entity in doc.ents:

            if entity.label_ == "PERSON":

                self.previous_speaker = entity.text

                return entity.text


        # Method 3
        # Consecutive Dialogue Tracking

        return self.previous_speaker


    def process_file(self, file_name):

        input_path = os.path.join(
            self.input_folder,
            file_name
        )


        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        results = []


        for item in data:

            speaker = self.find_speaker(

                item["text"],
                item["is_dialogue"]

            )


            item["speaker"] = speaker

            results.append(item)


        output_path = os.path.join(

            self.output_folder,

            file_name

        )


        with open(

            output_path,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                results,

                f,

                indent=4,

                ensure_ascii=False

            )


        print(

            f"{file_name} saved successfully."

        )


    def process_all_files(self):

        files = sorted(

            os.listdir(

                self.input_folder

            )

        )


        for file in files:

            if file.endswith(".json"):

                self.process_file(

                    file

                )