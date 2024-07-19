import customtkinter as ctk
import numpy as np


class BasketFrame(ctk.CTkFrame): # Inherits from CTkFrame

    def __init__(self, parent, black_hole, position, index, title, border_width, corner_radius, root):

        self.root = root
        self.title = title
        self.position = position
        self.index = index
        self.black_hole = black_hole

        self.parent_layout = parent
        self.products = []

        self.width = 300
        self.height = 230

        self.selecting = False # Indicating that this frame's image are being selected

        # Variabel for dislocating the images to avoid moving onto the rounded corners
        displacement = corner_radius - (corner_radius - border_width) / np.sqrt(2)
        self.parent = parent # Connect to parent frame
        self.images = [] # initialize empty list for product images

        # create a list for image positions

        self.positions = []

        h_jump = int((self.height - 2 * (border_width + displacement)) / 4) # Four rows
        w_jump = int((self.width - 2 * (border_width + displacement)) / 5) # Five columns -> max 4x5 = 20 items per basket

        self.spacing = (w_jump, h_jump) # horizontal & vertical gap in pixels between figures
        self.dislocation = (border_width + displacement, border_width + displacement)

        for j in range(0, 4):
            for i in range(0, 5):
                self.positions.append((self.dislocation[0] + w_jump * i, self.dislocation[1] + h_jump * j))

        # Initialize ctk.CTkFrame
        super().__init__(parent,
                         width = self.width,
                         height = self.height,
                         fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"],
                         border_width = border_width,
                         corner_radius = corner_radius)

        self.place(x = self.position[0], y = self.position[1])

        self.label_h = 25

        self.label_width = 150
        self.title_label = ctk.CTkLabel(parent, text = title, font = ('Helvetica', 16), text_color = 'black', fg_color = '#C2D8DC', height = 7, width = self.label_width, corner_radius= 10)
        self.title_entry = ctk.CTkEntry(parent, font = ('Helvetica', 16), text_color = 'black', fg_color = '#C2D8DC', height = 7, width = self.label_width, corner_radius = 0)

        self.title_label.place(x = self.position[0] + (self.width/2) - (self.label_width/2), y = self.position[1] - self.label_h)

        self.title_label.bind("<Button-1>", self.change_name)

    def change_name(self, event): # opens entry widget on top of title label for name change

        self.title_label.place_forget()
        self.title_entry.place(x = self.position[0] + (self.width / 2) - (self.label_width / 2), y = self.position[1] - self.label_h)
        self.title_entry.bind("<Return>", self.finish_name_change)
        self.root.bind('<Button-1>', self.finish_name_change)
        self.title_entry.focus_set() # Make entry widget active

    def finish_name_change(self, event):

        name = self.title_entry.get()    
        self.title_entry.place_forget()
        self.title_label.place(x = self.position[0] + (self.width/2) - (self.label_width/2), y = self.position[1] - self.label_h)
        self.title_label.configure(text = name)
        self.black_hole.button.configure(text = name)
        self.root.unbind('<Button-1>')
