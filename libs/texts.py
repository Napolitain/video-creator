from pathlib import Path
from typing import List

from libs.ai import AI
from libs.constants import root_dir
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
        self.data_dir = root_dir / "data"
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
            self.texts.append(text)

    def generate_audios(self) -> dict[str, Path]:
        """
        Generate audios for each text.
        If the audio is already cached and the hash is latest, skip.
        :return:
        """
        audios_lang_to_path = {}
        for text in self.texts:
            current_hashes = Text.hashes
            cached_hashes = text.generator_audiocache_hashes()
            # Check the hashes
            audio_dir = self.data_dir / "cache" / text.lang / "audio"
            i = 0
            with open(audio_dir / "hashes", "w") as f:
                for current_hash, cached_hash in zip(current_hashes, cached_hashes):
                    # add the audio path to the dictionary
                    audios_lang_to_path.setdefault(text.lang, []).append(audio_dir / f"{i}.mp3")
                    if current_hash != cached_hash:
                        slide_text = text.slides_text[i]
                        self.client.generate_audio(slide_text.text, audio_dir / f"{i}.mp3")
                    i += 1
                    f.write(f"{current_hash}\n")
        return audios_lang_to_path
