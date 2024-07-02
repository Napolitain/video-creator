FROM python:slim

WORKDIR /app

# Install dependencies
ADD requirements.txt /app/requirements.txt
ADD main.py /app/main.py

RUN python -m ensurepip --upgrade
RUN python -m pip install --upgrade setuptools
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Run the application
CMD ["python", "main.py"]
