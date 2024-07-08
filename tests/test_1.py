import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import *

class TestDataTransformation(unittest.TestCase):

    def test_runko(self):
        self.assertEqual(0, 0)
        self.assertEqual(1, 1)

    def test_Lang(self):
        self.assertEqual(Lang.FI, 'FI')
        self.assertEqual(Lang.SV, 'SV')
        self.assertEqual(Lang.EN, 'EN')

    def test_DefaultTranslator(self):
        ##CORRECT DATA
        self.assertEqual(Translator.get_string('STR_UI_PAIVITA_TIETOKANTA', Lang.FI), 
                         'Päivitä tietokanta')
        self.assertEqual(Translator.get_string('STR_UI_PAIVITA_TIETOKANTA', Lang.EN), 
                         'Update database')
        self.assertEqual(Translator.get_string('STR_UI_LUO_TARJOUS', Lang.SV), 
                         'Skapa erbjudande')
        
        self.assertEqual(Translator.get_string('STR_UI_PAIVITA_TIETOKANTA'), 
                         'Päivitä tietokanta')
        
        Translator.set_default_lang(Lang.SV)
        self.assertEqual(Translator.get_string('STR_UI_PAIVITA_TIETOKANTA'), 
                         'Uppdatera databas')
        Translator.set_default_lang(Lang.FI)

        ##INCORRECT DATA
        self.assertEqual(Translator.default_lang, Lang.FI)
        with self.assertRaises(AssertionError):
            self.assertEqual(Translator.default_lang, Lang.SV)
        with self.assertRaises(AssertionError):
            self.assertEqual(Translator.default_lang, Lang.EN)

        self.assertEqual(Translator.get_string('STR_UI_PAIVITA', Lang.SV), 
                         '[STR_UI_PAIVITA]')
        
        with self.assertRaises(KeyError):
            Translator.get_string('STR_UI_HAE_TUOTTEET', Lang.SV)

if __name__ == '__main__':
    unittest.main()