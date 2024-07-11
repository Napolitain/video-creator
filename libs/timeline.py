from pathlib import Path

from libs.texts import Texts


class Timeline:
    """
    A timeline is a list of texts that are displayed in a sequence, audios, metadata, effects...
    It should be compatible to Davinci in principle.
    """

    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.texts: Texts = Texts()
        self.audios = []



