from tkinter import *
import customtkinter as ctk
from MenuBar import MenuBar
from ContentFrame import ContentFrame
import os

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH) # Root directory of the project

ctk.set_appearance_mode('dark')

class App(ctk.CTk):
    
    def __init__(self):

        super().__init__()

        # Initiation

        self.title('Tap_project3')
        self.dimensions = (1700, 900)
        self.geometry(f'{self.dimensions[0]}x{self.dimensions[1]}')
        
    # @@@@@ SETTINGS @@@@@
        # Geometry settings

        self.menu_bar_rel_h = 0.05

        # Menu bar font size and type and button width

        self.menu_bar_font_size = 20
        self.menu_bar_font = 'Helvetica'
        self.menu_bar_button_width = 200
        self.menu_bar_button_pad = 5

        # content frame settings

        #layout2 settings

        self.layout2_left_width = 0.15
        self.layout2_middle_width = 0.5
        self.layout2_right_width = 0.35

        self.layout2_left_button_pad = 10
        self.layout2_left_button_height = 50
        self.layout2_frame_color = '#739FA6'
        self.layout2_left_font = ('Helvetica', 20)

        self.layout2_mid_menu_width = 200
        self.layout2_mid_menu_height = 50
        self.layout2_buttons_height = 35

        self.layout2_treeview_height = 500

        self.layout2_right_pad = 10


        #layout3 settings
        self.layout3_frame_color = '#739FA6'
        self.layout3_highlight_color = '#75B2BB'
        self.layout3_left_width = 0.1
        self.layout3_middle_width = 0.5
        self.layout3_right_width = 0.4

        self.layout3_middle_split1 = 0.45
        self.layout3_middle_split2 = 0.1   
        self.layout3_middle_split3 = 0.45  

        # Movement animation
        self.animation_speed = 0.2
        self.animation_steps = 200

        # Product image size
        self.layout3_product_image_size = 350

        # Font for the left buttons
        self.layout3_left_font = ('Helvetica', 20)

        #pady for left buttons
        self.layout3_left_pady = 5
        # height for left buttons
        self.layout3_left_height = 60
        # Create upper menu-bar

        self.menu_bar = MenuBar(self)
        
        # set content frame under the menu bar
        self.content_frame = ContentFrame(self)

if __name__ == '__main__':

    application = App()
    application.mainloop()