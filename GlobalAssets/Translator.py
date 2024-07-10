import json
from enum import StrEnum


class Lang(StrEnum):
    FI = 'FI'
    SV = 'SV'
    EN = 'EN'


class Translator:

    words: dict = {}  # contains all words in all languages
    default_lang: Lang = Lang.FI

    @classmethod
    def load_words(cls, json_translations_path: str):
        with open(json_translations_path, "r", encoding="utf-8") as f:
            cls.words = json.load(f)

    @classmethod
    def get_string(cls, keyword: str, lang: Lang = None) -> str:
        if lang is None:
            lang = cls.default_lang
        str_out = cls.words[keyword][lang]
        if type(str_out) is str and (str_out != ''):
            return str_out
        else:
            return '[' + keyword + ']'

    @classmethod
    def set_default_lang(cls, lang: Lang):
        assert isinstance(lang, Lang), "Expected 'lang' to be an instance of 'Lang' enumeration ERROR: #0002"
        cls.default_lang = lang
