from tkinter import *
import customtkinter as ctk
from MenuBar import MenuBar
from ContentFrame import ContentFrame
import os
from GlobalAssets.Translator import Translator, Lang
from GlobalAssets.UIDimensions import UIDimensions

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH) # Root directory of the project

ctk.set_appearance_mode('dark')
ctk.ThemeManager.load_theme(os.path.join(PATH,'GlobalAssets','custom_theme.json'))
Translator.load_words(os.path.join(PATH,'GlobalAssets','custom_translations.json'))
Translator.set_default_lang(Lang.FI)
UIDimensions.load_words(os.path.join(PATH,'GlobalAssets','UI_dimensions.json'))


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # Initiation

        self.title('Tap_project3')
        self.dimensions = (1700, 900)
        self.geometry(f'{self.dimensions[0]}x{self.dimensions[1]}')

    # @@@@@ SETTINGS @@@@@

        # Menu bar font size and type and button width

        self.menu_bar_font_size = 20
        self.menu_bar_font = 'Helvetica'

        # content frame settings

        # layout2 settings

        self.layout2_frame_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]
        self.layout2_left_font = ('Helvetica', 20)

        # layout3 settings
        self.layout3_frame_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]
        self.layout3_highlight_color = ctk.ThemeManager.theme["CustomFrameHightlight"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]

        # Font for the left buttons
        self.layout3_left_font = ('Helvetica', 20)

        # Create upper menu-bar

        self.menu_bar = MenuBar(self)
        
        # set content frame under the menu bar
        self.content_frame = ContentFrame(self)

if __name__ == '__main__':

    application = App()
    application.mainloop()