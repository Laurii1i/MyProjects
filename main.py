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
        # Geometry settings

        self.menu_bar_rel_h = UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION')

        # Menu bar font size and type and button width

        self.menu_bar_font_size = 20
        self.menu_bar_font = 'Helvetica'
        self.menu_bar_button_width = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_WIDTH_ABSOLUTE')
        self.menu_bar_button_pad = UIDimensions.get('DIM_UI_MENU_BAR','BUTTON_PAD_ABSOLUTE')

        # content frame settings

        # layout2 settings

        self.layout2_left_width = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')
        self.layout2_middle_width = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')
        self.layout2_right_width = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')

        self.layout2_left_button_pad = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_PAD_ABSOLUTE')
        self.layout2_left_button_height = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_HEIGHT_ABSOLUTE')
        self.layout2_frame_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]
        self.layout2_left_font = ('Helvetica', 20)

        self.layout2_mid_menu_width = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_WIDTH_ABSOLUTE')
        self.layout2_mid_menu_height = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE')
        self.layout2_buttons_height = UIDimensions.get('DIM_UI_LAYOUT2','BUTTONS_HEIGHT_ABSOLUTE')

        self.layout2_treeview_height = UIDimensions.get('DIM_UI_LAYOUT2','TREEVIEW_HEIGHT_ABSOLUTE')

        self.layout2_right_pad = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE')

        # layout3 settings
        self.layout3_frame_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]
        self.layout3_highlight_color = ctk.ThemeManager.theme["CustomFrameHightlight"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]
        self.layout3_left_width = UIDimensions.get('DIM_UI_LAYOUT3','LEFT_WIDTH_FRACTION')
        self.layout3_middle_width = UIDimensions.get('DIM_UI_LAYOUT3','MIDDLE_WIDTH_FRACTION')
        self.layout3_right_width = UIDimensions.get('DIM_UI_LAYOUT3','RIGHT_WIDTH_FRACTION')

        self.layout3_middle_split1 = UIDimensions.get('DIM_UI_LAYOUT3','MIDDLE_SPLIT1_FRACTION')
        self.layout3_middle_split2 = UIDimensions.get('DIM_UI_LAYOUT3','MIDDLE_SPLIT2_FRACTION')  
        self.layout3_middle_split3 = UIDimensions.get('DIM_UI_LAYOUT3','MIDDLE_SPLIT3_FRACTION') 

        # Movement animation
        self.animation_speed = UIDimensions.get('DIM_UI_MOVEMENT_ANIMATION','ANIMATION_SPEED') 
        self.animation_steps = UIDimensions.get('DIM_UI_MOVEMENT_ANIMATION','ANIMATION_STEPS') 

        # Product image size
        self.layout3_product_image_size = UIDimensions.get('DIM_UI_LAYOUT3','PRODUCT_IMAGE_SIZE_ABSOLUTE')

        # Font for the left buttons
        self.layout3_left_font = ('Helvetica', 20)

        #pady for left buttons
        self.layout3_left_pady = UIDimensions.get('DIM_UI_LAYOUT3','LEFT_PADY_ABSOLUTE')
        # height for left buttons
        self.layout3_left_height = UIDimensions.get('DIM_UI_LAYOUT3','LEFT_HEIGHT_ABSOLUTE')
        # Create upper menu-bar

        self.menu_bar = MenuBar(self)
        
        # set content frame under the menu bar
        self.content_frame = ContentFrame(self)

if __name__ == '__main__':

    application = App()
    application.mainloop()