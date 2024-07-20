import tkinter as tk
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk
import os
from BasketFrame import BasketFrame
import time
from GlobalAssets.UIDimensions import UIDimensions


PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH) # Root directory of the project

class image():

    def __init__(self, frame, position, index, path, parent_layout, side_length, root, discount, product_data) -> None:
        
        self.product_data = product_data
        self.discount = discount
        self.root = root
        self.path = path
        self.parent_layout = parent_layout
        self.index = index # this variable indicates the ordering. Used in place swapping
        self.position = position # position on the screen 
        self.frame = frame # middle_up_frame
        self.selected = False # Variable for image selection
        self.on_show = False # Variable indicating if this image is shown in middle_bottom_frame
        self.original_image = Image.open(path).convert("RGBA")

        original_width, original_height =  self.original_image.size
        aspect_ratio = original_width/original_height
        if aspect_ratio > 1: # if figure is wider than higher
            new_width = side_length
            new_height = (original_height/original_width) * side_length
        else:
            new_height = side_length
            new_width = aspect_ratio * side_length

        resized_image =  self.original_image.resize((int(new_width), int(new_height)),Image.Resampling.LANCZOS) # Resize image
        self.photo = ImageTk.PhotoImage(resized_image)
        self.label = tk.Label(self.frame,
                              image=self.photo,
                              bg= ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode], # TODO: keksi joku parempi ratkaisu
                              width = side_length,
                              height = side_length)
        self.label.place(x = self.position[0], y = self.position[1]) # place the label into coordinates of self.position 


        # Bind mouse events

        self.label.bind("<ButtonPress-1>", self.on_start_drag)
        self.label.bind("<ButtonRelease-1>", lambda event: self.on_release(event, self.parent_layout.black_holes + [self.parent_layout.delete_hole]))
        
        self.label.bind("<B1-Motion>", lambda event: self.on_drag(event, self.parent_layout.black_holes + [self.parent_layout.delete_hole]))

        # initialize dragging variables 

        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.read_description()

    def read_description(self):
        
        path = os.path.join(PATH,'Descriptions', self.product_data['webpage'], self.product_data['name']+'.txt')
        print(path)
        if os.path.isfile(path):
            with open(path, 'r') as file:
                writing = file.read()
                if '<color>' in writing:
                    writing = writing.replace('<color>', self.product_data['color'])
                if '<size>' in writing:
                    writing = writing.replace('<size>', self.product_data['size'])

                self.description = writing    
        else:
            self.set_default_description()        

    def set_default_description(self):

        string = ''

        for key, value in self.product_data.items():
            if key != 'price' and key != 'number':
                string = string + f'{value}, '

        string = string[:-2] + '.'
        self.description = string

    def move_image(self, dx, dy): # Move an increment 

        x = self.label.winfo_x() + dx
        y = self.label.winfo_y() + dy
        self.label.place(x=x, y=y)

    def move_to(self, final_location, ini_loc): # move to final_location from ini_loc with animation

        substeps = UIDimensions.get('DIM_UI_MOVEMENT_ANIMATION','ANIMATION_STEPS') # location points in the animation
        total_time = UIDimensions.get('DIM_UI_MOVEMENT_ANIMATION','ANIMATION_SPEED') # total time for the animation
        time_between_steps = int((total_time / substeps)*1000) # convert to milliseconds for after() function
        vector = np.array(final_location) - np.array(ini_loc) # Vector pointing from init_loc to final_location
        increment = vector/substeps # Create increment vector

        placements = []
        for i in range(substeps+1): # generate location points in between the start and finish locations
            placements.append(i*increment+ini_loc)

        for i, pos in enumerate(placements):
            x,y = pos[0], pos[1]
            def place_label(x=x, y=y): # Define wrapper
                self.label.place(x = x, y = y)

            
            self.parent_layout.root.after(time_between_steps*i, place_label) # Create many function calls with after to create animation


    def on_start_drag(self, event): # Initialize dragging by saving mouse location

        for frame in self.parent_layout.right_frame.baskets + [self.parent_layout.middle_up_frame]:
            frame.selecting = False # Initialize false selecting variable

        self.start_x = event.x_root
        self.start_y = event.y_root 
        self.label.lift() # make image under drag to show on top other images
        self.parent_layout.lift_black_holes() # make black_holes show on top of dragged image
        self.parent_layout.delete_hole.button.lift()
        self.frame.selecting = True # Update selecting to the frame in which the image is being clicked on

    def on_drag(self, event, black_holes):


        if not self.selected: # If image under drag is not selected, de-select other images
            self.parent_layout.de_select_images()

        self.dragging = True

        selected = [image for image in self.frame.images if image.selected] # put all selected figures into a list

        if len(selected) == 0:
            selected.append(self)
        event_loc = (event.x_root, event.y_root) # event location in global coordinates

        for hole in black_holes:
            if hole.event_is_in(event_loc): # If cursor is located on top of a black hole
                if not hole.enlarged: # Make black hole bigger
                    hole.enlarge()
                    break
            elif hole.enlarged and not hole.event_is_in(event_loc): # if cursor has left the black hole, return it to its original size 
                hole.return_size() 
                break

        if self.dragging:
            dx = event.x_root - self.start_x # calculate movement sice last event call
            dy = event.y_root - self.start_y
            self.start_x = event.x_root # update new initial location
            self.start_y = event.y_root

            if len(selected) == 1: # If we are only moving one figure
                self.move_image(dx, dy)
            else:    
                for image in selected: # else move all selected figures
                    image.move_image(dx, dy)


    def drag_on_black_hole(self, event_loc, black_hole) -> bool: # Return true if dragged image is on the input black hole, false else
        pass

    def event_is_in(self, image, event_loc): # return true if mouse is on top of image at a given instance. False if none

        x,y = event_loc

        x_left = image.label.winfo_rootx()
        x_right = x_left + image.label.winfo_width()

        y_up = image.label.winfo_rooty()
        y_down = y_up + image.label.winfo_height()

        if (x > x_left and x < x_right) and (y > y_up and y < y_down):
            return True

        else: return False


    def on_release(self, event, black_holes): 

        in_basket =  isinstance(self.frame, BasketFrame)
        event_loc = (self.label.winfo_x(), self.label.winfo_y()) # frame coordinates
        event_global = (event.x_root, event.y_root) # global coordinates for black hole checking, because of spagetti code

        selected = [image for image in self.frame.images if image.selected] # @@@@ CHANGED @@@

        if len(selected) == 0: # if none was selected, append the figure under drag
            selected.append(self)

         # list containing all the images except the one under dragging
        all_but_self = [image for image in self.frame.images] # @@@@ CHANGED @@@
        all_but_self.remove(self)


        if not self.dragging:
            if not self.selected: # If not selected, select the image

                control_state = bool(event.state & 0x4) # True if control key was pressed, false else
                self.select_image(control_state)
            else:
                self.de_select_image() # else, de-select it
        else:
            for hole in black_holes: # Check if button release was on top of a black hole
                if hole.event_is_in(event_global):
                    hole.return_size() # Return to normal size
                    self.dragging = False
                    hole.execute(selected, self.frame) # execute black hole command
                    return

            if len(selected) == 1: # Enable re-ordering only if one image is being dragged
                for image in all_but_self: # Check for release event on top of other images
                    if image.event_is_in(image, event_global):   # If release event was on some other image, re-order images                     
                        to_index = image.index
                        self.parent_layout.re_order_images(self.frame, self, to_index)
                        break
                if self.is_outside(event_global) and in_basket: # If we have dragged the image outside of the basket, return home
                    self.parent_layout.go_home([self],event_global)
                    self.dragging = False
                    return
                else: # If release event was not on any other images, just return the images to its home square      
                    self.move_to(self.position, event_loc)
                    self.dragging = False
                    return
            else:
                if in_basket and self.is_outside(event_global):
                    self.parent_layout.go_home(selected,event_global)
                    self.dragging = False
                    return
                for image in selected: # else move all selected figures
                    location = (image.label.winfo_x(), image.label.winfo_y())
                    image.move_to(image.position, location)  
                    self.dragging = False  
            self.dragging = False # finally change dragging variable to false

    def select_image(self, control_state):

        print(self.index)

        self.parent_layout.set_product_image(self) # set large product image to middle_bottom_frame

        if not control_state: # If control key was not pressed, de-select all other images
            self.parent_layout.de_select_images() # De-select other product images

        # If images are selected in other frames, deselect them
        for frame in self.parent_layout.right_frame.baskets + [self.parent_layout.middle_up_frame]:
            for image in frame.images:
                if not frame.selecting and image.selected:
                    image.de_select_image()

        if not self.selected:
            self.selected = True # state variable to selected
            self.label.configure(bg = ctk.ThemeManager.theme["CustomFrameHightlight"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode])  # background to light blue to indicate that

    def de_select_image(self):

        if self.selected:

            self.selected = False # state variable to de-selected
            self.label.configure(bg = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode]) # background to light yellow to indicate that
    
    def is_outside(self, location):

        x, y = location
        x_low = self.frame.winfo_rootx()
        x_high = x_low + self.frame.winfo_width()

        y_low = self.frame.winfo_rooty()
        y_high = y_low + self.frame.winfo_height()

        if x_low < x < x_high and y_low < y <y_high:
            return False
        
        else: return True

    def black_hole(self):
        print('blacked')    