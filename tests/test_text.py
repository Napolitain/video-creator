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

def test_text_init_creates_directories(text_instance):
    """
    Test that the Text class __init__ method creates necessary directories.
    """
    assert text_instance.data_dir.exists()
    assert text_instance.cache_dir.exists()
    assert text_instance.lang_dir.exists()
    assert text_instance.audio_dir.exists()
    assert text_instance.text_dir.exists()

def test_load_text_input_true_loads_texts(text_instance, tmp_path):
    """
    Test the load_text method with is_input=True to ensure it loads texts correctly.
    """
    # Setup: Create a texts.txt file in the data directory
    texts_file = tmp_path / "data" / "texts.txt"
    texts_file.write_text("Hello\n-\nWorld\n")
    # Test
    text_instance.load_text(is_input=True)
    assert len(text_instance.slides_text) == 2  # Expecting two SlideText instances

def test_load_text_input_false_handles_file_not_found(text_instance):
    """
    Test the load_text method with is_input=False to ensure it handles FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        text_instance.load_text(is_input=False)