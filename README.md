# video-creator

### Description

The goal of the project is to be able to create video automatically using automated scripts and TTS tools.
It should also be compatible with Davinci Resolve.

### Development

#### Requirements

- Docker

#### Build

```bash
docker build -t videocreator .
```

#### Run

```bash
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY --rm -v "${PWD}"/data:/app/data videocreator
```

### Usage

```bash
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY --rm -v "${PWD}"/data:/app/data ghcr.io/Napolitain/videocreator:latest
```
