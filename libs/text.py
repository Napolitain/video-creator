from typing import List

from libs.ai import AI
from libs.constants import root_dir
from libs.slide_text import SlideText


class Text:
    """
    A text is a list of paragraphs that are displayed in a slide.
    """
    hashes = []

    def __init__(self, lang: str):
        self.lang = lang

        self.data_dir = root_dir / "data"
        self.cache_dir = self.data_dir / "cache"
        if not self.cache_dir.exists():
            self.cache_dir.mkdir()
        self.lang_dir = self.cache_dir / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()
        self.audio_dir = self.lang_dir / "audio"
        if not self.audio_dir.exists():
            self.audio_dir.mkdir()
        self.text_dir = self.lang_dir / "text"
        if not self.text_dir.exists():
            self.text_dir.mkdir()

        self.slides_text: List[SlideText] = []

    def load_text(self, is_input: bool):
        """
        Load texts from a file like texts.txt, and compute hashes for each text block.
        TODO: Separate caching mechanism to make the function more modular and safe.
        :param is_input: if True, load texts from data directory, otherwise from text directory inside lang.
        :return:
        """
        self.slides_text: List[SlideText] = []
        if is_input:
            text_file = self.data_dir / "texts.txt"
        else:
            text_file = self.text_dir / "texts.txt"
        try:
            with open(text_file, "r", encoding="utf-8") as f:
                text = ""
                i = 0
                for line in f:
                    if line == "-\n":
                        slide_text = SlideText(text)
                        self.slides_text.append(slide_text)
                        text = ""
                        i += 1
                    else:
                        text += line
                slide_text = SlideText(text)
                self.slides_text.append(slide_text)
            if is_input:
                Text.hashes = self.generator_current_hashes()
        except FileNotFoundError:
            if is_input:
                # Input text file should always exist!
                raise FileNotFoundError("Text file does not exist in data directory.")
            else:
                # Create tmp text file to get original text and its hashes
                tmp = Text("en")
                tmp.load_text(True)
                client = AI()
                # Iterate over each text block and translate it
                for slide_text in tmp.slides_text:
                    translated_text, hash_current = client.translate(slide_text.text, self.lang)
                    self.slides_text.append(SlideText(translated_text))
                # save text to text_dir
                self.save_text_file(self.slides_text)

    def save_text_file(self, slides_text: List[SlideText]):
        """
        Save texts to a file like texts.txt, and save hashes to a file like hashes.
        :param slides_text: list of texts to save
        :param hashes: list of hashes to save
        :return:
        """
        text_file = self.text_dir / "texts.txt"
        hash_file = self.text_dir / "hashes"
        with open(text_file, "w", encoding="utf-8") as f:
            with open(hash_file, "w", encoding="utf-8") as g:
                i = 0
                for t, h in zip(slides_text, Text.hashes):
                    if i == len(slides_text) - 1:
                        f.write(t.text)
                        g.write(h)
                    else:
                        f.write(t.text + "\n-\n")
                        g.write(h + "\n")
                        i += 1

    def generator_current_hashes(self) -> List[str]:
        """
        Generate hashes for each slide text.
        :return: list of hashes
        """
        return [slide_text.hash() for slide_text in self.slides_text]

    def generator_textcache_hashes(self) -> List[str]:
        """
        Generate hashes for each slide text in cache.
        :return: list of hashes
        """
        hash_file = self.text_dir / "hashes"
        if not hash_file.exists():
            return ["" for _ in self.slides_text]
        return [line.rstrip() for line in open(hash_file, "r")]

    def generator_audiocache_hashes(self) -> List[str]:
        """
        Generate hashes for each audio file in cache.
        :return: list of hashes
        """
        hash_file = self.audio_dir / "hashes"
        if not hash_file.exists():
            return ["" for _ in self.slides_text]
        return [line.rstrip() for line in open(hash_file, "r")]

