import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GlobalElements.Languages import Lang
from GlobalElements.Translators import *

class TestDataTransformation(unittest.TestCase):

    def test_runko(self):
        self.assertEqual(0, 0)
        self.assertEqual(1, 1)

    def test_Lang(self):
        self.assertEqual(Lang.FI, 0)
        self.assertEqual(Lang.SV, 1)
        self.assertEqual(Lang.EN, 2)

    def test_DefaultTranslator(self):
        ##CORRECT DATA
        default_translator = DefaultTranslator(Lang.FI)
        self.assertEqual(default_translator.get_string('STR_UI_PAIVITA_TIETOKANTA', Lang.FI), 
                         'Päivitä tietokanta')
        self.assertEqual(default_translator.get_string('STR_UI_PAIVITA_TIETOKANTA', Lang.EN), 
                         'Update database')
        self.assertEqual(default_translator.get_string('STR_UI_LUO_TARJOUS', Lang.SV), 
                         'Skapa erbjudande')
        
        self.assertEqual(default_translator.get_string('STR_UI_PAIVITA_TIETOKANTA'), 
                         'Päivitä tietokanta')

        ##INCORRECT DATA
        self.assertEqual(default_translator.default_lang, Lang.FI)
        with self.assertRaises(AssertionError):
            self.assertEqual(default_translator.default_lang, Lang.SV)
        with self.assertRaises(AssertionError):
            self.assertEqual(default_translator.default_lang, Lang.EN)
        
        with self.assertRaises(AssertionError) as context1:
            default_translator2 = DefaultTranslator(0)
        self.assertEqual("Expected 'lang' to be an instance of 'Lang' enumeration ERROR: #0001", str(context1.exception))

        ##MISSING DATA
        default_translator3 = DefaultTranslator(Lang.FI)
        dictionary = {'STR_UI_PAIVITA_TIETOKANTA': ['Päivitä tietokanta', 'Uppdatera databas', 'Update database'],
                        'STR_UI_ETSI_TUOTTEITA': ['Etsi Tuotteita', 'Sök for producter', 'Search products'],
                        'STR_UI_LUO_TARJOUS': ['Luo Tarjous', '', 'Create offer']} #Pointti on se, että tämä on tyhjä ruotsinkielisessä käännöksessä
        languages = ['FI','SV','EN']
        default_translator3.df = pd.DataFrame(data=dictionary, index=languages).T
        self.assertEqual(default_translator3.get_string('STR_UI_LUO_TARJOUS', Lang.SV), 
                         '[STR_UI_LUO_TARJOUS]')

if __name__ == '__main__':
    unittest.main()