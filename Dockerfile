FROM python:latest

WORKDIR /app

# Install dependencies
ADD requirements.txt /app/requirements.txt
ADD main.py /app/main.py

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Run the application
CMD ["python", "main.py"]
