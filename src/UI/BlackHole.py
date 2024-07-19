import customtkinter as ctk
import numpy as np
from image import image
from GlobalAssets.UIDimensions import UIDimensions


class BlackHole():

    def __init__(self, position, index, parent, parent_layout, text, color, type, root):

        self.root = root
        self.width = 75
        self.fontsize = 20
        self.position = position
        self.index = index
        self.parent_layout = parent_layout

        self.type = type

        if type == 'sink':  # Make delete button larger
            self.height = 60
            b_width = 0
            text_col = 'white'
        else:
            self.height = 40
            b_width = 3
            text_col = 'black'

        self.button = ctk.CTkButton(parent,
                                    text=text,
                                    width=self.width,
                                    height=self.height,
                                    font=('Helvetica', self.fontsize),
                                    corner_radius=10,
                                    fg_color=color,
                                    border_width=b_width,
                                    text_color=text_col,
                                    border_color='#052329')
        self.button.place(x=position[0],
                          y=position[1])

        #root.after(5, func = self.resize)
        self.enlarged = False  # Variable indicating if the black hole is enlarged or not

        self.button.bind("<ButtonPress-1>", self.on_start_drag)
        self.button.bind("<ButtonRelease-1>", self.on_release)
        
        self.button.bind("<B1-Motion>", self.on_drag)

    def resize(self):
        if self.button.winfo_reqwidth() > self.width:
            self.button.configure(font=('Helvetica',
                                        self.fontsize-1))
            self.fontsize=self.fontsize -1
            self.root.after(5, func=self.resize)
        return

    def event_is_in(self, event_loc):  # Returns true if event is located inside the black hole, false else
        x,y = event_loc

        x_left = self.button.winfo_rootx()
        x_right = x_left + self.button.winfo_width()

        y_up = self.button.winfo_rooty()
        y_down = y_up + self.button.winfo_height()
        

        if (x > x_left and x < x_right) and (y > y_up and y < y_down):
            return True

        else: return False

    def enlarge(self):
        
        self.enlarged = True
        self.button.configure(width = int(1.1*self.width), height = int(1.1*self.height))

    def return_size(self):

        self.enlarged = False
        self.button.configure(width = self.width, height = self.height)

    def execute(self, x, frame): # execute self.function    

        if self.type == 'sink':
            self.parent_layout.delete_images(x, frame)

        elif self.type == 'wormhole':
            
            self.add_to_basket_frame(x)
            self.parent_layout.delete_images(x, frame)  

        
        self.parent_layout.concatenate_images(frame)

    def add_to_basket_frame(self, images):

        try:
            max_index = max([i.index for i in self.basket_frame.images])
        except:
            max_index = -1    

        for i, img in enumerate(images):   
            index = max_index + 1 + i # Take highest existing image index, add one. If more than 1 image is being added, also add the index of the list
            self.basket_frame.images.append(image(self.basket_frame, self.basket_frame.positions[index], index, img.path, self.parent_layout, side_length = 50, root = self.root, discount = img.discount,  product_data = img.product_data))


    def move_hole(self, dx, dy): # Move an increment 

        x = self.button.winfo_x() + dx
        y = self.button.winfo_y() + dy
        self.button.place(x=x, y=y)
            
    def on_start_drag(self, event): # Initialize dragging by saving mouse location

        self.start_x = event.x_root
        self.start_y = event.y_root 
        self.button.lift() # make black hole under drag to show on top other images
        self.parent_layout.delete_hole.button.lift()

    def on_drag(self, event):

        self.dragging = True
        event_loc = (event.x_root, event.y_root)
        sinkhole = self.parent_layout.delete_hole

        if self.dragging:
            if sinkhole.event_is_in(event_loc):
                sinkhole.enlarge()
            elif sinkhole.enlarged and not sinkhole.event_is_in(event_loc): 
                sinkhole.return_size()
            dx = event.x_root - self.start_x # calculate movement sice last event call
            dy = event.y_root - self.start_y
            self.start_x = event.x_root # update new initial location
            self.start_y = event.y_root
            self.move_hole(dx, dy)



    def on_release(self, event): 

        event_loc = (self.button.winfo_x(), self.button.winfo_y())
        event_global = (event.x_root, event.y_root) # global coordinates for black hole checking, because of spagetti code

        other_holes = list(self.parent_layout.black_holes)
        sinkhole = self.parent_layout.delete_hole
        try: 
            other_holes.remove(self) # this fails if sinkhole is being dragged
        except:
            self.move_to(self.position, event_loc) # move sinkhole home
            self.dragging = False
            return


        if not self.dragging:
            return # to be added functionalities
        else:

            if sinkhole.event_is_in(event_global): # Jos release event on poista napin päällä
                sinkhole.return_size()
                self.parent_layout.delete_black_hole(self)
            else:
                for hole in other_holes: # Check if button release was on top of a black hole
                    if hole.event_is_in(event_global):
                        self.dragging = False
                        self.parent_layout.re_order_black_holes(self, hole.index)
                        return
                else:
                    self.move_to(self.position, event_loc)
                    self.dragging = False


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

            def place_button(x=x, y=y): # Define wrapper
                self.button.place(x = x, y = y)
            
            self.parent_layout.root.after(time_between_steps*i, place_button) # Create many function calls with after to create animation     

   