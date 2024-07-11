import hashlib


class SlideText:
    def __init__(self, text: str):
        self.text = text

    def __hash__(self):
        return hashlib.sha256(self.text.encode()).hexdigest()

    def __str__(self):
        return self.text
