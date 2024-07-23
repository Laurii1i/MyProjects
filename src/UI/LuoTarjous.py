import customtkinter as ctk
import tkinter as tk
from UI.BlackHole import BlackHole
from UI.BasketFrame import BasketFrame
from PIL import Image, ImageTk
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions
import numpy as np
from image import *

def clear_frame(frame):

    for widget in frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame) or isinstance(widget, tk.Frame):

            if widget.winfo_manager() == 'pack':
                widget.pack_forget()
            elif widget.winfo_manager() == 'grid':
                widget.grid_forget()
            elif widget.winfo_manager() == 'place':
                widget.place_forget()
            else:
                # Handle the case when widget has no geometry manager
                pass

class LuoTarjous():

    def __init__(self, parent, content_frame, root):
        
        width = UIDimensions.get('MAIN_APP','X')
        height = (1-UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION'))*UIDimensions.get('MAIN_APP','Y')
        luo_tarjous_left_font = (UIDimensions.get('DIM_UI_LUO_TARJOUS','FONT'), UIDimensions.get('DIM_UI_LUO_TARJOUS','FONT_SIZE'))
        self.root = root
        self.parent = parent
        self.content_frame = content_frame
        self.left_frame = ctk.CTkFrame(content_frame, 
                                       height = height, 
                                       width = UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_WIDTH_FRACTION') * width)
        corner_radius = 10
        self.middle_up_frame = ctk.CTkFrame(content_frame, 
                                            fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"], 
                                            height = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_SPLIT1_FRACTION') * height, 
                                            width = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_WIDTH_FRACTION') * width,
                                            corner_radius = corner_radius)

        self.middle_up_frame.images = [] # images are stored here
        self.middle_up_frame.selecting = False # Indicating if this frame's images are being selected

        self.middle_middle_frame = ctk.CTkFrame(content_frame, 
                                                height = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_SPLIT2_FRACTION') * height, 
                                                width = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_WIDTH_FRACTION') * width)
        self.middle_bottom_frame = ctk.CTkFrame(content_frame, 
                                                fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"], 
                                                height = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_SPLIT3_FRACTION') * height, 
                                                width = UIDimensions.get('DIM_UI_LUO_TARJOUS','MIDDLE_WIDTH_FRACTION') * width)
        self.right_frame = ctk.CTkFrame(content_frame, 
                                        height = height, 
                                        width = UIDimensions.get('DIM_UI_LUO_TARJOUS','RIGHT_WIDTH_FRACTION') * width)
        self.right_frame.baskets = [] # These are baskets for products in the right most frame
        root.menu_bar.show_basket_button.configure(command = self.set_layout)

        # Buttons into frames

        self.uusi_kori = ctk.CTkButton(self.left_frame, 
                                       text = Translator.get_string('STR_UI_UUSI_KORI'), 
                                       font = luo_tarjous_left_font, 
                                       width = 0.965*(UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_WIDTH_FRACTION') * width), 
                                       height = UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_HEIGHT_ABSOLUTE'), 
                                       command = lambda: self.open_question_window('Nimeä kori'))
        self.uusi_kori.place(x = 0, 
                             y = UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_PADY_ABSOLUTE'))

        self.aseta_ale = ctk.CTkButton(self.left_frame, text = Translator.get_string('STR_UI_ASETA_ALENNUS'), 
                                       font = luo_tarjous_left_font, 
                                       width = 0.965*(UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_WIDTH_FRACTION') * width), 
                                       height = UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_HEIGHT_ABSOLUTE'), 
                                       command = self.set_discount)
        self.aseta_ale.place(x = 0, 
                             y = 2*UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_PADY_ABSOLUTE') + UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_HEIGHT_ABSOLUTE'))

        self.tallenna = ctk.CTkButton(self.left_frame, 
                                      text = Translator.get_string('STR_UI_TALLENNA_SESSIO'), 
                                      font = luo_tarjous_left_font, 
                                      width = 0.965*(UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_WIDTH_FRACTION') * width), 
                                      height = UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_HEIGHT_ABSOLUTE'))
        self.tallenna.place(x = 0, 
                            y = 3*UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_PADY_ABSOLUTE') + 2*UIDimensions.get('DIM_UI_LUO_TARJOUS','LEFT_HEIGHT_ABSOLUTE'))


        # Middle middle frame

        text_box_width = 760
        text_box_height = 75
        button_width = 75
        padx = 10
        pady = 5
        self.description = ctk.CTkTextbox(self.middle_middle_frame,
                                          height = text_box_height,
                                          width = text_box_width,
                                          fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"],
                                          font = ('Helvetica', 17))
        self.description.place(x=0, y = pady)

        self.save_descript = ctk.CTkButton(self.middle_middle_frame, height = text_box_height, width = button_width, text = Translator.get_string('STR_UI_TALLENNA_KUVAUS'), font = ('Helvetica', 17), command = self.write_description)
        self.save_descript.place(x = padx + text_box_width, y = pady)


        # Positions for product images
        self.middle_up_frame.spacing = (100,100) # Gap between figures (x, and y directions)

        disloc = corner_radius * (1-(1/np.sqrt(2))) # Figure dislocation to avoid clipping onto the rounded corners
        self.middle_up_frame.dislocation = (disloc, disloc) # dislocating figures

        self.middle_up_frame.positions = []
        for y in range(0, 10*self.middle_up_frame.spacing[1], self.middle_up_frame.spacing[1]):
            for x in range(0,7*self.middle_up_frame.spacing[0], self.middle_up_frame.spacing[0]):
                self.middle_up_frame.positions.append((self.middle_up_frame.dislocation[0] + x, self.middle_up_frame.dislocation[1] + y))

        # Black hole grid

        self.middle_up_frame.black_hole_grid = []

        for i in range(6):
             self.middle_up_frame.black_hole_grid.append((768, 10 + 50*i))

        # Basket frame grid
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        width = 300
        height = 230
        pady = 30
        padx = 15
        self.right_frame.basket_frame_grid = []

        for j in range(3):
            for i in range(2):
                self.right_frame.basket_frame_grid.append((15+i*(300+15), 30+j*(230+30)))

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Create black holes  
        self.black_holes = []

        # Trash bin button
        self.delete_hole = BlackHole((768,319), index = None, parent = self.middle_up_frame, parent_layout = self, text = 'Poista', color = 'dark red', type = 'sink', root = self.root)

        # Middle_bottom_frame

        self.middle_bottom_frame.data_labels = [] # alustetaan data labelit tuotetiedoille
        for _ in range(5):
            self.middle_bottom_frame.data_labels.append(ctk.CTkLabel(self.middle_bottom_frame, text = '', font = ('Helvetica', 25)))  

        self.middle_bottom_frame.discount_label = ctk.CTkLabel(self.middle_bottom_frame, text = '', font = ('Helvetica', 25))

            # Product image label (large image)
        self.middle_bottom_frame.product_label = tk.Label(self.middle_bottom_frame, bg= ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"][ctk.AppearanceModeTracker.appearance_mode])
        #TODO: voisko täs tehä joku self.middle_bottom_frame.product_label.configure(bg= ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"])?

    def set_layout(self):

        clear_frame(self.content_frame)
        self.left_frame.grid(row = 0, column = 0, rowspan = 3, padx = 10)
        self.middle_up_frame.grid(row = 0, column = 1, padx = 0)
        self.middle_middle_frame.grid(row = 1, column = 1)
        self.middle_bottom_frame.grid(row = 2, column = 1)
        self.right_frame.grid(row = 0, column = 2, rowspan = 3)

    def index_to_position(self, index, frame): # Returns coordinates for image in middle_up_frame by its ordering index

        items_per_row = 7

        y = frame.dislocation[1] + frame.spacing[1] * int(index / items_per_row)

        x = frame.dislocation[0] + frame.spacing[0] * (index % items_per_row)

        return (x,y)
    
    def place_image(self, position, index, path, product_data):

        self.middle_up_frame.images.append(image(self.middle_up_frame, position, index, path, self, side_length = 100, root = self.root, discount = 20, product_data = product_data))

    def delete_images(self, images, frame):

        for image in images:
            frame.images.remove(image)
            image.label.destroy()
            del image    

    def concatenate_images(self, frame): # after removing images, this concatenates the remaining ones 
        
        images = frame.images

        indexes = [img.index for img in images]

        try:
            places = list(range(0, max(indexes)+1))
        except: # If all of the figures were removed, the max() function will fail, hence except and return
            return    

        vacancies = []

        for place in places:
            if place not in indexes:
                vacancies.append(place)

        for image in images:

            to_be_moved = len([x for x in vacancies if x < image.index])  
            new_index = image.index - to_be_moved
            new_pos = image.frame.positions[new_index]

            image.move_to(new_pos, image.position) 

            image.position = new_pos
            image.index = new_index

    def de_select_images(self): # de-select all images in middle-up frame

        for basket in self.right_frame.baskets:
            for image in basket.images:
                if image.selected:
                    image.de_select_image()
        for image in self.middle_up_frame.images:
            if image.selected == True:
                image.de_select_image()

    def select_images(self): # selects all images in middle-up frame

        for image in self.middle_up_frame.images:
            if image.selected == False:
                image.select_image()     

    def re_order_images(self, frame, swapper_image, to_index): # swapper_image is the image which is moved into the line. Swap_index indicates the location where the image is moved

        # Get all images which have equal or larger order index than the to_index.
        # Get all the images which have a smaller order index than the from_index
        from_index = swapper_image.index

        if to_index < swapper_image.index: # swapper image is being moved up
            to_be_moved = [image for image in frame.images if ((image.index >= to_index) and (image.index < from_index))]
            to_be_moved.sort(key = lambda i: i.index) # put images in order

            swapper_ini_loc = (swapper_image.label.winfo_x(), swapper_image.label.winfo_y())
            swapper_image.move_to(to_be_moved[0].position, swapper_ini_loc) # Move to swapped location
            swapper_image.index = to_index # change index of the swapper image
            swapper_goes_to = tuple(to_be_moved[0].position) # Save the position where swapper image goes

            for i, image in enumerate(to_be_moved):

                image.index = image.index + 1
                try: # Get the position of the next image in the line
                    new_location = to_be_moved[i+1].position
                except IndexError: # If we are dealing with the last image, get the position of the swapper image
                    new_location = swapper_image.position

                image.move_to(new_location, image.position) 
                image.position = new_location   

            swapper_image.position = swapper_goes_to # finally update the swapper image position

        else:    
            to_be_moved = [image for image in frame.images if ((image.index <= to_index) and (image.index > from_index))]
            to_be_moved.sort(key = lambda i: i.index) # put images in order

            swapper_ini_loc = (swapper_image.label.winfo_x(), swapper_image.label.winfo_y())
            swapper_image.move_to(to_be_moved[-1].position, swapper_ini_loc) # Move to swapped location
            swapper_image.index = to_index # change index of the swapper image
            swapper_goes_to = tuple(to_be_moved[-1].position) # Save the position where swapper image goes

            positions = [img.position for img in to_be_moved]

            for i, image in enumerate(to_be_moved):

                image.index = image.index - 1
                if i == 0:
                    new_location = swapper_image.position                    
                else:
                    new_location = positions[i-1]

                image.move_to(new_location, image.position) 
                image.position = new_location   

            swapper_image.position = swapper_goes_to # finally update the swapper image position        

    def re_order_black_holes(self, swapper_hole, to_index): # swapper_image is the image which is moved into the line. Swap_index indicates the location where the image is moved

        frame = self.middle_up_frame
        # Get all holes which have equal or larger order index than the to_index.
        # Get all the holes which have a smaller order index than the from_index
        from_index = swapper_hole.index

        if to_index < swapper_hole.index: # swapper hole is being moved up
            to_be_moved = [hole for hole in self.black_holes if ((hole.index >= to_index) and (hole.index < from_index))]
            to_be_moved.sort(key = lambda i: i.index) # put holes in order

            swapper_ini_loc = (swapper_hole.button.winfo_x(), swapper_hole.button.winfo_y())
            swapper_hole.move_to(to_be_moved[0].position, swapper_ini_loc) # Move to swapped location
            swapper_hole.index = to_index # change index of the swapper hole
            swapper_goes_to = tuple(to_be_moved[0].position) # Save the position where swapper hole goes

            for i, hole in enumerate(to_be_moved):

                hole.index = hole.index + 1
                try: # Get the position of the next hole in the line
                    new_location = to_be_moved[i+1].position
                except IndexError: # If we are dealing with the last image, get the position of the swapper image
                    new_location = swapper_hole.position

                hole.move_to(new_location, hole.position) 
                hole.position = new_location   

            swapper_hole.position = swapper_goes_to # finally update the swapper image position

        else:    
            to_be_moved = [hole for hole in self.black_holes if ((hole.index <= to_index) and (hole.index > from_index))]
            to_be_moved.sort(key = lambda i: i.index) # put holes in order

            swapper_ini_loc = (swapper_hole.button.winfo_x(), swapper_hole.button.winfo_y())
            swapper_hole.move_to(to_be_moved[-1].position, swapper_ini_loc) # Move to swapped location
            swapper_hole.index = to_index # change index of the swapper hole
            swapper_goes_to = tuple(to_be_moved[-1].position) # Save the position where swapper hole goes

            positions = [img.position for img in to_be_moved]

            for i, hole in enumerate(to_be_moved):

                hole.index = hole.index - 1
                if i == 0:
                    new_location = swapper_hole.position                    
                else:
                    new_location = positions[i-1]

                hole.move_to(new_location, hole.position) 
                hole.position = new_location   

            swapper_hole.position = swapper_goes_to # finally update the swapper hole position            

        # Re order baskets accordingly

        for hole in self.black_holes:
            if hole.index != hole.basket_frame.index:
                hole.basket_frame.index = hole.index
                x, y = self.right_frame.basket_frame_grid[hole.index][0], self.right_frame.basket_frame_grid[hole.index][1]
                hole.basket_frame.position = (x,y)
                hole.basket_frame.place(x = x, y = y)
                hole.basket_frame.title_label.place(x = x + (hole.basket_frame.width/2) - (hole.basket_frame.label_width/2), y = hole.basket_frame.position[1] - hole.basket_frame.label_h)

    def go_home(self, images, location):
        
        frame = images[0].frame
        try: # take max index. If middle_up_frame is empty, index = 0
            index = max([im.index for im in self.middle_up_frame.images]) + 1 
        except:
            index = 0    

        x_global, y_global = location
        x_frame, y_frame = self.middle_up_frame.winfo_rootx(), self.middle_up_frame.winfo_rooty()

        position = (x_global - x_frame, y_global - y_frame) # coordinate transform from global to middle_up_frame coordinates

        # Create a copy to the middle_up_frame of the moved image
        for i, img in enumerate(images):
            new_image = image(self.middle_up_frame, position, index+i, img.path, self, side_length = 100, root = self.root, discount = img.discount,  product_data = img.product_data)
            self.middle_up_frame.images.append(new_image)
            new_image.move_to(self.middle_up_frame.positions[index+i], position)
            new_image.position = self.middle_up_frame.positions[index+i]

        # Delete and concatenate basket frame images
        self.delete_images(images, frame)
        self.concatenate_images(frame)

    def lift_black_holes(self):

        for black_hole in self.black_holes:
            black_hole.button.lift()

    def set_product_image(self, image):

        image.on_show = True # Indicate that  this image is being shown

        try:
            self.on_show_img.on_show = False # Make the previous image on_show variable false to indicate removal
        except: 
            pass    
        self.on_show_img = image # Update on_show image object

        img = image.original_image # non re-sized image

        width, height = img.size

        aspect_ratio = width/height
        size = UIDimensions.get('DIM_UI_LUO_TARJOUS','PRODUCT_IMAGE_SIZE_ABSOLUTE')

        if aspect_ratio > 1: # if figure is wider than higher
            new_width = size
            new_height = (height/width) * size
        else:
            new_height = size
            new_width = aspect_ratio * size

        resized_image =  img.resize((int(new_width), int(new_height)),Image.Resampling.LANCZOS) # Resize image
        self.product_photo = ImageTk.PhotoImage(resized_image)
        self.middle_bottom_frame.product_label.configure(width = size, height = size, image = self.product_photo)
        self.middle_bottom_frame.product_label.place(x = 10, y = 10) # place the label into coordinates of self.position 
        
        # place data labels

        disloc_x, disloc_y = size+50, 40

        prod_data = []
        order = ('name', 'color', 'size', 'price')

        for item in order:
            for key, val in image.product_data.items():
                
                if item == key:
                    if item == 'price':
                        val = val + '€'
                    prod_data.append(val)
                    break

        for i, data in enumerate(prod_data):
            
            if data == '':
                continue
            else:
                data_label = self.middle_bottom_frame.data_labels[i]
                data_label.configure(text = data)
                data_label.place(x = disloc_x, y = disloc_y)
                disloc_y = disloc_y + 30

        self.middle_bottom_frame.discount_label.configure(text = f'Alennus {image.discount}%')
        self.middle_bottom_frame.discount_label.place(x = disloc_x, y = 320)

        self.description.delete("1.0", tk.END)
        self.description.insert(tk.END, image.description)

    def new_black_hole(self, name):

        index = len(self.black_holes)

        position = self.middle_up_frame.black_hole_grid[index]

        black_hole = BlackHole(position = position, index = index, parent = self.middle_up_frame, parent_layout = self, text = name, color = '#C2D8DC', type = 'wormhole', root = self.root)
        self.black_holes.append(black_hole)

        if len(self.right_frame.baskets) == 0:
            index = 0
        else:
            index = max(self.right_frame.baskets, key = lambda x: x.index).index + 1 # Get current max index and add one

        position = self.right_frame.basket_frame_grid[index]
        b_frame = BasketFrame(self.right_frame, black_hole, position = position, index = index, title = name, border_width = 5, corner_radius = 20, root = self.root)
        black_hole.basket_frame = b_frame # connect black hole and its basketfame
        self.right_frame.baskets.append(b_frame)

    def exit_top_level(self, event = None): # closes the pop-up window with enter key press

        name = self.top_lvl_entry.get()
        self.top_lvl.destroy()
        self.new_black_hole(name)

    def open_question_window(self, string):

        if len(self.black_holes) == 6: # max 6 holes is allowed right now 
            return

        self.top_lvl = tk.Toplevel(self.root)
        self.top_lvl.bind("<Return>", self.exit_top_level) # bind enter key press to the pop-up window
        self.top_lvl.geometry("200x100+750+450")
        self.top_lvl_label = ctk.CTkLabel(self.top_lvl, text = string, font = ('Helvetica', 20), text_color = 'black')   
        self.top_lvl_entry = ctk.CTkEntry(self.top_lvl, width = 150, corner_radius = 20)
        self.top_lvl_label.pack() 
        self.top_lvl_entry.pack()
        self.top_lvl_entry.focus_set()

    def open_discount_window(self, string, all_images):

        self.top_lvl = tk.Toplevel(self.root)
        self.top_lvl.bind("<Return>", lambda event: self.exit_discount(all_images)) # bind enter key press to the pop-up window
        self.top_lvl.geometry("200x100+750+450") # place it in the middle with size 200x100
        self.top_lvl_label = ctk.CTkLabel(self.top_lvl, text = string, font = ('Helvetica', 20), text_color = 'black')   
        self.top_lvl_entry = ctk.CTkEntry(self.top_lvl, width = 150, corner_radius = 20)
        self.top_lvl_label.pack() 
        self.top_lvl_entry.pack()
        self.top_lvl_entry.focus_set()

    def exit_discount(self, images, event = None):

        selected_images = [image for image in images if image.selected]
        discount = self.top_lvl_entry.get()
        
        try:
            float(discount)
        except:
            self.top_lvl_label.configure(text = 'Vain numerot kelpaavat!')
            self.top_lvl_label.configure(font = ('Helvetica', 15))
            return  
          
        for image in selected_images:
            image.discount = discount

        try:
            if self.on_show_img in selected_images:
                self.middle_bottom_frame.discount_label.configure(text = f'Alennus {discount}%')
        except:
            pass        
        self.top_lvl.destroy()    

    def set_discount(self):

        all_images = [image for image in self.middle_up_frame.images if image.selected] # sisältää aluksi vain middle_up_framen kuvat, seuraavassa luupissa lisätään loput basketframeista

        for basket in self.right_frame.baskets:
            for image in basket.images:
                if image.selected:
                    all_images.append(image)

        if len(all_images) == 0:
            self.aseta_ale.configure(text = 'Valitse tuote!')
            self.root.after(1000, lambda: self.aseta_ale.configure(text = 'Aseta Ale'))
            return
        self.open_discount_window('Anna alennus', all_images)

    def delete_black_hole(self, black_hole):

        index = black_hole.index
        basket_frame = black_hole.basket_frame
        images = list(basket_frame.images) # Shallow copy to avoid problems  

        # Move images in the basket frame home
        if len(images) != 0:
            self.go_home(images, (basket_frame.winfo_rootx(),basket_frame.winfo_rooty()))    

        # Delete black hole

        self.black_holes.remove(black_hole)
        black_hole.button.destroy()
        del black_hole

        # Delete basketframe

        self.right_frame.baskets.remove(basket_frame)  
        basket_frame.title_label.destroy() 
        basket_frame.destroy()
        del basket_frame

        # Concatenate black holes

        for hole in self.black_holes:
            if hole.index > index:
                new_index = hole.index - 1
                new_pos = self.middle_up_frame.black_hole_grid[new_index]
                hole.move_to(new_pos, hole.position)

                hole.index = new_index
                hole.position = new_pos

        # Concatenate basket frames
            
        for basket in self.right_frame.baskets:
            if basket.index > index:
                new_index = basket.index - 1
                new_pos = self.right_frame.basket_frame_grid[new_index]
                
                basket.place(x = new_pos[0], y = new_pos[1])
                basket.index = new_index
                basket.position = new_pos   

                basket.title_label.place(x = new_pos[0] + (basket.width/2) - (basket.label_width/2), y = new_pos[1] - basket.label_h)          

    def write_description(self):

        image = self.on_show_img
        path = os.path.join(PATH,'Descriptions', image.product_data['webpage'], image.product_data['name']+'.txt')

        writing = self.description.get("1.0", tk.END)
        
        try:
            color = image.product_data['color']
            if color in writing:
                writing = writing.replace(color, '<color>')
        except:
            pass    

        try:
            size = image.product_data['size']
            if size in writing:
                writing = writing.replace(size, '<size>')
        except:
            pass    

        with open(path, 'w') as file:
            file.write(writing)
        image.description = self.description.get("1.0", tk.END)