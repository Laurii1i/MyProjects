import customtkinter as ctk
from image import *
from UI.layout3 import layout3
from UI.layout2 import layout2

class ContentFrame():

    def __init__(self, root):
        
        window_width = UIDimensions.get('MAIN_APP','X')
        window_height = UIDimensions.get('MAIN_APP','Y')
        self.root = root

        self.content_frame = ctk.CTkFrame(root, height=0.95*window_height, width = 1*window_width)
        self.content_frame.pack(pady = 10, padx = 10)

        # Tarjouksen luontiin vaadittavat widgetit

        self.layout3 = layout3(self, self.content_frame, root)
        self.layout2 = layout2(self, self.content_frame, root)

