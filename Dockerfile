FROM chainguard/python:latest-dev AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade setuptools && \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt --user

FROM chainguard/python:latest

WORKDIR /app

# Make sure you update Python version in path
COPY --from=builder /home/nonroot/.local/lib/python3.12/site-packages /home/nonroot/.local/lib/python3.12/site-packages
COPY main.py main.py
COPY data/texts.txt data_docker/texts.txt
COPY data/slides/ data_docker/slides/

# Run the application
ENTRYPOINT ["python", "main.py"]
