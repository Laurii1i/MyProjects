import customtkinter as ctk
from MenuBar import MenuBar
from ContentFrame import ContentFrame


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
