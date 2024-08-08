import customtkinter as ctk
import tkinter as tk
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions

class MenuBar():

    def __init__(self, root):

        window_width = UIDimensions.get('MAIN_APP','X')
        window_height = UIDimensions.get('MAIN_APP','Y')
        menu_bar_font = (UIDimensions.get('DIM_UI_MENU_BAR','FONT'), UIDimensions.get('DIM_UI_MENU_BAR','FONT_SIZE'))

        self.menu_frame = ctk.CTkFrame(root,
                                       height = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE') * window_height,
                                       width = 1*window_width)
        self.menu_frame.pack()

        '''self.update_button = ctk.CTkButton(self.menu_frame,
                                           text = Translator.get_string('STR_UI_PAIVITA_TIETOKANTA'),
                                           font = menu_bar_font,
                                           width = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE'))
        self.update_button.grid(row = 0,
                                column = 0,
                                padx = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_PAD_ABSOLUTE'))'''
        
        self.search_button = ctk.CTkButton(self.menu_frame,
                                           text = Translator.get_string('STR_UI_ETSI_TUOTTEITA'),
                                           font = menu_bar_font,
                                           width = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE'))
        
        self.search_button.grid(row = 0,
                                column = 1,
                                padx = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_PAD_ABSOLUTE'))
        
        self.show_basket_button = ctk.CTkButton(self.menu_frame,
                                                text = Translator.get_string('STR_UI_LUO_TARJOUS'),
                                                font = menu_bar_font,
                                                width = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE'))
        
        self.show_basket_button.grid(row = 0, column = 2, padx = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_PAD_ABSOLUTE'))