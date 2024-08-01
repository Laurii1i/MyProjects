import customtkinter as ctk
from UI.MenuBar import MenuBar
from UI.ContentFrame import ContentFrame
from GlobalAssets.UIDimensions import UIDimensions


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # Initiation

        self.title(UIDimensions.get('MAIN_APP', 'TITLE'))

        x = UIDimensions.get('MAIN_APP', 'X')
        y = UIDimensions.get('MAIN_APP', 'Y')
        self.geometry(f'{x}x{y}')

    # @@@@@ SETTINGS @@@@@

        # Create upper menu-bar

        self.menu_bar = MenuBar(self)

        # set content frame under the menu bar
        self.content_frame = ContentFrame(self)
