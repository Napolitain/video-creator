FROM python:slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY data/texts.txt data/texts.txt
COPY data/slides/ data/slides/

RUN python -m ensurepip --upgrade
RUN python -m pip install --upgrade setuptools
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Run the application
CMD ["python", "main.py"]
