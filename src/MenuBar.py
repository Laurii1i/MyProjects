import customtkinter as ctk
import tkinter as tk
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions

class MenuBar():

    def __init__(self, root):

        window_width, window_height = root.dimensions
        menu_bar_rel_h = UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION')
        menu_bar_font_size = root.menu_bar_font_size
        menu_bar_font = root.menu_bar_font
        menu_bar_button_width = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE')
        menu_bar_button_pad = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_PAD_ABSOLUTE')

        self.menu_frame = ctk.CTkFrame(root, height = menu_bar_rel_h * window_height, width = 1*window_width)
        self.menu_frame.pack()

        self.update_button = ctk.CTkButton(self.menu_frame,
                                           text = Translator.get_string('STR_UI_PAIVITA_TIETOKANTA'),
                                           font = (menu_bar_font, menu_bar_font_size), width = menu_bar_button_width)
        self.update_button.grid(row = 0,
                                column = 0,
                                padx = menu_bar_button_pad)

        self.search_button = ctk.CTkButton(self.menu_frame, text = Translator.get_string('STR_UI_ETSI_TUOTTEITA'), font = (menu_bar_font, menu_bar_font_size), width = menu_bar_button_width)
        self.search_button.grid(row = 0, column = 1, padx = menu_bar_button_pad)

        self.show_basket_button = ctk.CTkButton(self.menu_frame, text = Translator.get_string('STR_UI_LUO_TARJOUS'), font = (menu_bar_font, menu_bar_font_size), width = menu_bar_button_width)
        self.show_basket_button.grid(row = 0, column = 2, padx = menu_bar_button_pad)