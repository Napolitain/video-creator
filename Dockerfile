FROM chainguard/python:latest-dev AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade setuptools
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt --user

FROM chainguard/python:latest

WORKDIR /app

# Make sure you update Python version in path
COPY --from=builder /home/nonroot/.local/lib/python3.12/site-packages /home/nonroot/.local/lib/python3.12/site-packages
COPY main.py main.py
COPY data/texts.txt data/texts.txt
COPY data/slides/ data/slides/

# Run the application
ENTRYPOINT ["python", "main.py"]
