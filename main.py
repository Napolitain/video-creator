import argparse
import logging
import shutil

from dotenv import load_dotenv
from moviepy.editor import *

from libs.ai import AI
from libs.constants import *
from libs.texts import Texts

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    # Language of the text input (default: English, options are languages codes and "ai")
    argparser.add_argument("--lang", type=str, default="en", choices=langs.keys(), required=False)
    # Language of the text output (default: English, options can be multiple selections)
    argparser.add_argument("--langs-out", default=["en"], nargs="+", choices=langs.keys() - {"ai"}, required=False)
    # Create a Davinci project
    argparser.add_argument("--davinci", action="store_true", default=False, required=False)
    # OpenAI API key and organization
    argparser.add_argument("--openai-api-key", type=str, default=None, required=False)
    argparser.add_argument("--openai-organization", type=str, default=None, required=False)
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

    # Input language must be in the output languages, at first position
    if args.lang not in args.langs_out:
        args.langs_out.insert(0, args.lang)
    else:
        args.langs_out.remove(args.lang)
        args.langs_out.insert(0, args.lang)

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
        if slide.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            slides.append(slide)

    # Standardize the width and height of the slides by resizing them to the first slide's dimensions
    # The aspect ratio can be also changed by adding black bars to the sides or top and bottom if needed
    first_slide = slides[0]
    first_slide_img = ImageClip(str(first_slide))
    width, height = first_slide_img.size
    aspect_ratio = width / height

    # Generate video from slides and audio (audio must be concatenated)
    for lang_out in args.langs_out:
        # Get hashes from original and compare to out/hashes-lang_out. If they are the same, skip.
        try:
            hashes_original = texts.texts[0].generator_current_hashes()
            skip = True
            with open(data_dir / "out" / f"hashes-{lang_out}", "r", encoding="utf-8") as f:
                i = 0
                for line in f:
                    if hashes_original[i] != line.strip():
                        skip = False
                        break
                    i += 1
        except FileNotFoundError:
            skip = False
        if skip:
            continue
        # Create output directory
        output_dir = data_dir / "out"
        if not output_dir.exists():
            output_dir.mkdir()
        # Create video
        zipped_audios = zip(slides, audios[lang_out])
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
        video.write_videofile(
            str(output_dir / f"output-{lang_out}.mp4"),
            codec="png",
            fps=30,
        )
        # Save hashes
        with open(data_dir / "out" / f"hashes-{lang_out}", "w", encoding="utf-8") as f:
            for i, h in enumerate(hashes_original):
                if i == len(hashes_original) - 1:
                    f.write(f"{h}")
                else:
                    f.write(f"{h}\n")
