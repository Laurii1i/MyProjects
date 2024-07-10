import json


class UIDimensions:

    values: dict = {}  # contains all words in all languages

    @classmethod
    def load_words(cls, json_ui_dimensions_path: str):
        with open(json_ui_dimensions_path, "r") as f:
            cls.values = json.load(f)

    @classmethod
    def get(cls, keyword_group: str, keyword_element: str) -> str:
        str_out = cls.values[keyword_group][keyword_element]
        return str_out
