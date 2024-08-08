import unittest
import sys
import os
import customtkinter as ctk
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import *
from GlobalAssets.Translator import Translator, Lang

class TestDataTransformation(unittest.TestCase):

    def test_runko(self):
        self.assertEqual(0, 0)
        self.assertEqual(1, 1)

    def test_Lang(self):
        self.assertEqual(Lang.FI, 'FI')
        self.assertEqual(Lang.SV, 'SV')
        self.assertEqual(Lang.EN, 'EN')

    def test_Translator(self):
        ##CORRECT DATA
        self.assertEqual(Translator.get_string('STR_UI_LUO_UUSI_TUOTE', Lang.FI), 
                         'Luo oma tuote')
        self.assertEqual(Translator.get_string('STR_UI_LUO_UUSI_TUOTE', Lang.EN), 
                         'Create a new product')
        self.assertEqual(Translator.get_string('STR_UI_LUO_TARJOUS', Lang.SV), 
                         'Skapa erbjudande')
        
        self.assertEqual(Translator.get_string('STR_UI_LUO_UUSI_TUOTE'), 
                         'Luo oma tuote')
        
        Translator.set_default_lang(Lang.SV)
        self.assertEqual(Translator.get_string('STR_UI_LUO_UUSI_TUOTE'), 
                         'Skapa en ny produkt')
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
    
    def test_custom_theme(self):
        self.assertEqual(ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"], ["#EAF2F8", "#739FA6"])

if __name__ == '__main__':
    unittest.main()