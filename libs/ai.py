import hashlib
from pathlib import Path

from openai import OpenAI


def singleton(cls):
    """
    Singleton decorator
    :param cls: class to make singleton
    :return: get_instance function
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class AI:
    """
    OpenAI client to interact with OpenAI API
    """
    def __init__(self, api_key: str = None, organization: str = None):
        self.client = OpenAI(api_key=api_key, organization=organization)

    def translate(self, text: str, lang: str) -> tuple[str, str]:
        """
        Ask chatgpt-3.5 turbo to translate text to lang
        :param text: text to translate
        :param lang: language to translate to
        :return: translated text and hash of the text to avoid translating the same text
        """
        stream = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Translate '{text}' to {lang}."}],
            stream=False,
        )
        print(f"AI: Translated to {lang}")
        return stream.choices[0].message.content, hashlib.sha256(text.encode()).hexdigest()

    def generate_audio(self, text: str, speech_file_path: Path):
        """
        Generate audio from text and save it to speech_file_path
        :param text: text to generate audio from
        :param speech_file_path: path to save the audio
        :return: hash of the text to avoid regenerating the same audio
        """
        response = self.client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=text
        )
        response.stream_to_file(speech_file_path)
        print(f"AI: Generated audio for {speech_file_path.name}")
        return hashlib.sha256(text.encode()).hexdigest()
