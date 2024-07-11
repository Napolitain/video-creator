from pathlib import Path
from typing import List

from libs.ai import AI
from libs.text import Text


class Texts:
    """
    A list of Text in different languages.
    """

    def __init__(self, lang="en", langs=None):
        self.lang_in = lang
        if langs is None:
            self.langs_out = ["en"]
        else:
            self.langs_out = langs
        self.data_dir = Path(__file__).parent / "data"
        self.texts: List[Text] = []
        self.client = AI()

    def generate_texts(self):
        """
        Generate texts for each language.
        If the language is the same as the input language, load the text from the data directory.
        :return:
        """
        self.texts = []
        for lang_out in self.langs_out:
            text = Text(lang_out)
            if self.lang_in == lang_out:
                text.load_text(True)
            else:
                text.load_text(False)

    def generate_audios(self) -> dict[str, Path]:
        """
        Generate audios for each text.
        If the audio is already cached and the hash is latest, skip.
        :return:
        """
        audios_lang_to_path = {}
        for text in self.texts:
            current_hashes = text.generator_current_hashes()
            cached_hashes = text.generator_audiocache_hashes()
            skip = False
            # Check the hashes
            for current_hash, cached_hash in zip(current_hashes, cached_hashes):
                if current_hash == cached_hash:
                    skip = True
                    break
            if skip:
                continue
            audio_dir = self.data_dir / "cache" / text.lang / "audio"
            for i, slide_text in enumerate(text.slides_text):
                self.client.generate_audio(slide_text.text, audio_dir / f"{i}.mp3")
            audios_lang_to_path[text.lang] = audio_dir
        return audios_lang_to_path