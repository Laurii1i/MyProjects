import pandas as pd
from GlobalElements.Languages import Lang


class DefaultTranslator:

    def __init__(self, lang: Lang):

        assert isinstance(lang, Lang), "Expected 'lang' to be an instance of 'Lang' enumeration ERROR: #0001"
        self.df = self._create_data_frame()
        self.default_lang = lang

    def _create_data_frame(self):

        dictionary = {'STR_UI_PAIVITA_TIETOKANTA': ['Päivitä tietokanta', 'Uppdatera databas', 'Update database'],
                      'STR_UI_ETSI_TUOTTEITA': ['Etsi Tuotteita', 'Sök for producter', 'Search products'],
                      'STR_UI_LUO_TARJOUS': ['Luo Tarjous', 'Skapa erbjudande', 'Create offer'],
                      'STR_UI_PAIVITA': ['Päivitä', '', ''],
                      'STR_UI_HAE_TUOTTEET': ['Hae Tuotteet!', '', ''],
                      'STR_UI_LISAA_KORIIN': ['Lisää koriin', '', ''],
                      'STR_UI_UUSI_KORI': ['Uusi kori', '', ''],
                      'STR_UI_ASETA_ALENNUS': ['Aseta alennus', '', ''],
                      'STR_UI_TALLENNA_SESSIO': ['Tallenna sessio', '', ''],
                      'STR_UI_TALLENNA_KUVAUS': ['Tallenna\nkuvaus', '', '']} # ei enää jaksanu kääntää, laitetaan lisää ku tarvitaan
        languages = ['FI', 'SV', 'EN']
        return pd.DataFrame(data=dictionary, index=languages).T

    def get_string(self, keyword: str, lang: Lang = None) -> str:
        if lang is None:
            lang = self.default_lang

        series = self.df.iloc[:, lang]
        str_out = series.loc[keyword]
        if type(str_out) is str and (str_out != ''):
            return str_out
        else:
            return '['+keyword+']'

    def set_default_lang(self, lang: Lang):
        assert isinstance(lang, Lang), "Expected 'lang' to be an instance of 'Lang' enumeration ERROR: #0002"
        self.default_lang = lang


class CSVTranslator(DefaultTranslator):

    def _create_data_frame(self):
        return pd.read_csv('GlobalElements/Translations.csv', index_col=0)


global_translator = DefaultTranslator(Lang.FI)
