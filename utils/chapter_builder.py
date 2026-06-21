from dialogue_detector import detect_dialogue
from speaker_identifier import identify_speaker

def build_chapter(sentences):

    chapter = []

    for sentence in sentences:

        kind = detect_dialogue(sentence)

        if kind == "narration":

            chapter.append({
                "type":"narration",
                "text":sentence
            })

        else:

            chapter.append({
                "type":"dialogue",
                "speaker":identify_speaker(sentence),
                "text":sentence
            })

    return chapter

