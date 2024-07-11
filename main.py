import argparse
import logging
import shutil
from pathlib import Path

from dotenv import load_dotenv
from moviepy.editor import *

from libs.ai import AI
from libs.constants import *
from libs.texts import Texts

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    # Language of the text input (default: English, options are languages codes and "ai")
    argparser.add_argument("--lang", type=str, default="en", choices=langs.keys())
    # Language of the text output (default: English, options can be multiple selections)
    argparser.add_argument("--langs-out", default=["en"], nargs="+", choices=langs.keys() - {"ai"})
    # Create a Davinci project
    argparser.add_argument("--davinci", action="store_true", default=False)
    # OpenAI API key and organization
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
    client = AI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORGANIZATION"))
    # Unset OpenAI API keys from environment variables for memory safety
    os.unsetenv("OPENAI_API_KEY")
    os.unsetenv("OPENAI_ORGANIZATION")

    # Init
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

    # Generate texts and audios
    texts = Texts(lang=args.lang, langs=args.langs_out)
    texts.generate_texts()  # Translate texts if needed
    audios = texts.generate_audios()  # Generate audios for texts

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
    for lang_out in args.langs_out:
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
        video.write_videofile(str(output_dir / f"output-{lang_out}.mp4"), codec="libx264", fps=30)
