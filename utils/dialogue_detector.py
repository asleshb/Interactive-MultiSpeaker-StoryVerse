import os
import json
import spacy


class DialogueDetector:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        self.input_folder = "sentence_data"

        self.output_folder = "dialogue_data"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        self.dialogue_verbs = {

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


    def is_dialogue(self, sentence):

        doc = self.nlp(sentence)

        has_quotes = False

        has_person = False

        has_speech_verb = False

        has_subject_speech_verb = False


        # Quote detection
        if '"' in sentence or "'" in sentence:

            has_quotes = True


        # Named Entity Recognition
        for entity in doc.ents:

            if entity.label_ == "PERSON":

                has_person = True

                break


        # POS Tagging + Dependency Parsing
        for token in doc:

            # POS tagging
            if (
                token.lemma_.lower() in self.dialogue_verbs
                and token.pos_ == "VERB"
            ):

                has_speech_verb = True

                # Dependency parsing
                for child in token.children:

                    if child.dep_ == "nsubj":

                        has_subject_speech_verb = True

                        break


        score = 0


        if has_quotes:

            score += 3


        if has_person:

            score += 1


        if has_speech_verb:

            score += 2


        if has_subject_speech_verb:

            score += 2


        return score >= 3


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

            sentences = json.load(f)


        results = []


        for item in sentences:

            text = item["text"]

            item["is_dialogue"] = self.is_dialogue(
                text
            )

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