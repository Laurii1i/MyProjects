import customtkinter as ctk
from MenuBar import MenuBar
from ContentFrame import ContentFrame
from GlobalAssets.UIDimensions import UIDimensions


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # Initiation

        self.title(UIDimensions.get('MAIN_APP', 'TITLE'))
        self.geometry(f'{UIDimensions.get('MAIN_APP', 'X')}x{UIDimensions.get('MAIN_APP', 'Y')}')

    # @@@@@ SETTINGS @@@@@

        # Create upper menu-bar

        self.menu_bar = MenuBar(self)

        # set content frame under the menu bar
        self.content_frame = ContentFrame(self)
