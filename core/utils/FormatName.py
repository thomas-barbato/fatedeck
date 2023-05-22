import re
import random


class RegexpFormat:
    def __init__(self, name):
        self.name = name

    def get_data(self):
        return re.sub(r"[0-9][A-Z][a-z]", "", self.name), f"{self.name}#{random.randint(99, 9999)}"
