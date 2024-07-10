import argparse
import hashlib
import logging
import shutil
from pathlib import Path

from dotenv import load_dotenv
from moviepy.editor import *
from openai import OpenAI

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--lang", type=str, default="en")
    argparser.add_argument("--davinci", action="store_true", default=False)
    argparser.add_argument("--openai-api-key", type=str, default=None)
    argparser.add_argument("--openai-organization", type=str, default=None)
    args = argparser.parse_args()

    # Load OpenAI API keys from .env file
    if args.openai_api_key is not None:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    if args.openai_organization is not None:
        os.environ["OPENAI_ORGANIZATION"] = args.openai_organization
    if args.openai_api_key is None and args.openai_organization is None:
        load_dotenv()
    # Create OpenAI client
    client = OpenAI()
    # Unset OpenAI API keys from environment variables for memory safety
    os.unsetenv("OPENAI_API_KEY")
    os.unsetenv("OPENAI_ORGANIZATION")

    # Texts are stored in texts.txt file.
    # A part is defined by having text until \n-\n separator.
    # Example :
    # Text 1
    # -
    # Text 2
    data_docker_dir = Path(__file__).parent / "data_docker"
    if not data_docker_dir.exists():
        logging.fatal("Data directory does not exist. Run with volumes.")
    data_dir = Path(__file__).parent / "data"
    # if data is empty, copy from data_docker recursively
    if data_dir.exists() and not list(data_dir.iterdir()):
        for item in data_docker_dir.iterdir():
            if item.is_dir() and not (data_dir / item.name).exists():
                shutil.copytree(item, data_dir / item.name, symlinks=False)
            else:
                shutil.copy(item, data_dir, follow_symlinks=False)
    if not (data_dir / "texts.txt").exists():
        logging.fatal("Text file does not exist in data directory.")
    text_file = data_dir / "texts.txt"
    texts = []
    hashes_current = []
    with open(text_file, "r") as f:
        text = ""
        for line in f:
            if line == "-\n":
                texts.append(text)
                hashes_current.append(hashlib.sha256(text.encode()).hexdigest())
                text = ""
            else:
                text += line
        texts.append(text)
        hashes_current.append(hashlib.sha256(text.encode()).hexdigest())

    # Generates audio as well as metadata to indicate the last time update.
    cache_dir = data_dir / "cache"
    speech_dir = cache_dir / "audio"
    hash_file_path = speech_dir / f"hashes"
    if not cache_dir.exists():
        cache_dir.mkdir()
    if not speech_dir.exists():
        speech_dir.mkdir()
    if not hash_file_path.exists():
        hash_file_path.touch()
    hashes_cache = []
    audios = []
    with open(hash_file_path, "r") as f:
        read = f.readlines()
        for line in read:
            # Remove newline characters
            line = line.rstrip()
            hashes_cache.append(line)

    with open(hash_file_path, "w") as f:
        for i, text in enumerate(texts):
            # If the file already exists, and its metadata hash is identical to current metadata, skip
            speech_file_path = speech_dir / f"{i}.mp3"
            audios.append(speech_file_path)
            if speech_file_path.exists():
                try:
                    if hashes_cache[i] == hashes_current[i]:
                        f.write(hashes_current[i] + "\n")
                        continue
                except IndexError:
                    pass

            # Print filename to track progress
            print(speech_file_path)
            f.write(hashes_current[i] + "\n")
            # Generate audio
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                input=text
            )
            response.stream_to_file(speech_file_path)

    # Load slides
    slides = []
    slides_dir = data_dir / "slides"
    if not slides_dir.exists():
        slides_dir.mkdir()
    for slide in slides_dir.iterdir():
        # if file is .png, .jpg, or .jpeg
        if slide.suffix in [".png", ".jpg", ".jpeg"]:
            slides.append(slide)

    # Standardize the width and height of the slides by resizing them to the first slide's dimensions
    # The aspect ratio can be also changed by adding black bars to the sides or top and bottom if needed
    first_slide = slides[0]
    first_slide_img = ImageClip(str(first_slide))
    width, height = first_slide_img.size
    aspect_ratio = width / height

    # Generate video from slides and audio (audio must be concatenated)
    output_dir = data_dir / "out"
    if not output_dir.exists():
        # create output directory if it does not exist
        output_dir.mkdir()
    zipped_audios = zip(slides, audios)
    clips = []
    for i, (slide, audio) in enumerate(zipped_audios):
        # Print filename to track progress
        print(output_dir / f"{i}.mp4")
        # Generate video
        audioclip = AudioFileClip(str(audio))
        clip = ImageClip(str(slide)).set_duration(audioclip.duration)
        # Add black bars to the sides of the slide if the aspect ratio is different
        clip = clip.set_audio(audioclip)
        clips.append(clip)
    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(str(output_dir / "output.mp4"), codec="libx264", fps=24)
