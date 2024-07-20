import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import customtkinter as ctk
PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)
from GlobalAssets.Translator import Translator, Lang
from GlobalAssets.UIDimensions import UIDimensions

ctk.set_appearance_mode('dark')
ctk.ThemeManager.load_theme(os.path.join(PATH,'GlobalAssets','custom_theme.json'))
Translator.load_words(os.path.join(PATH,'GlobalAssets','custom_translations.json'))
Translator.set_default_lang(Lang.FI)
UIDimensions.load_words(os.path.join(PATH,'GlobalAssets','UI_dimensions.json'))