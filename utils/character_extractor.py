import spacy

nlp = spacy.load("en_core_web_sm")

def extract_characters(chapter_text):

    doc = nlp(chapter_text)

    characters = set()

    for ent in doc.ents:

        if ent.label_ == "PERSON":

            characters.add(ent.text)

    return list(characters)