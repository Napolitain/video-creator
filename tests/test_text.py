import unittest

import pytest

from libs.ai import AI
from libs.text import Text


# Setup mock AI class
@pytest.fixture
def mocked_ai():
    ai_instance = AI(api_key="dummy_key", organization="dummy_org")
    with unittest.mock.patch.object(ai_instance, 'client') as mocked_client:
        # Mock the chat.completions.create method
        mocked_client.chat.completions.create.return_value = unittest.mock.MagicMock(
            choices=[unittest.mock.MagicMock(message={"content": "translated text"})]
        )
        # Mock the audio.speech.create method
        mocked_audio_response = unittest.mock.MagicMock()
        mocked_audio_response.stream_to_file = unittest.mock.MagicMock()
        mocked_client.audio.speech.create.return_value = mocked_audio_response

        yield ai_instance


@pytest.fixture
def text_instance(tmp_path):
    # Use tmp_path fixture provided by pytest for creating temporary directories
    root_dir = tmp_path
    return Text(lang="en", root_dir=root_dir)


def test_generator_cache_hashes():
    lang = "en"
    if lang is not None:
        dir = dir / f"-{lang}"
    hash_file = dir / "hashes"
