from utils.speaker_identifier import SpeakerIdentifier


def main():

    identifier = SpeakerIdentifier()

    identifier.process_all_files()


if __name__ == "__main__":

    main()