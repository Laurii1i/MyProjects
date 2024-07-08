import tkinter as tk
from tkinter.ttk import Style
import os
import customtkinter as ctk
import webbrowser
from tkinter.ttk import Treeview
from PIL import Image, ImageTk
import pandas as pd
from image import *
from BlackHole import BlackHole
from BasketFrame import BasketFrame
from GlobalAssets.Translator import *

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH) # Root directory of the project


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

class layout3():

    def __init__(self, parent, content_frame, root):
        
        width, height = root.dimensions[0], (1-root.menu_bar_rel_h)*root.dimensions[1]
        self.root = root
        self.parent = parent
        self.content_frame = content_frame
        self.left_frame = ctk.CTkFrame(content_frame, height = height, width = root.layout3_left_width * width)
        corner_radius = 10
        self.middle_up_frame = ctk.CTkFrame(content_frame, fg_color = root.layout3_frame_color, height = root.layout3_middle_split1 * height, width = root.layout3_middle_width * width, corner_radius = corner_radius)

        self.middle_up_frame.images = [] # images are stored here
        self.middle_up_frame.selecting = False # Indicating if this frame's images are being selected

        self.middle_middle_frame = ctk.CTkFrame(content_frame, height = root.layout3_middle_split2 * height, width = root.layout3_middle_width * width)
        self.middle_bottom_frame = ctk.CTkFrame(content_frame, fg_color = root.layout3_frame_color, height = root.layout3_middle_split3 * height, width = root.layout3_middle_width * width)
        self.right_frame = ctk.CTkFrame(content_frame, height = height, width = root.layout3_right_width * width)
        self.right_frame.baskets = [] # These are baskets for products in the right most frame
        root.menu_bar.show_basket_button.configure(command = self.set_layout3)

        # Buttons into frames

        self.uusi_kori = ctk.CTkButton(self.left_frame, text = Translator.get_string('STR_UI_UUSI_KORI'), font = root.layout3_left_font, width = 0.965*(root.layout3_left_width * width), height = root.layout3_left_height, command = lambda: self.open_question_window('Nimeä kori'))
        self.uusi_kori.place(x = 0, y = root.layout3_left_pady)

        self.aseta_ale = ctk.CTkButton(self.left_frame, text = Translator.get_string('STR_UI_ASETA_ALENNUS'), font = root.layout3_left_font, width = 0.965*(root.layout3_left_width * width), height = root.layout3_left_height, command = self.set_discount)
        self.aseta_ale.place(x = 0, y = 2*root.layout3_left_pady + root.layout3_left_height)

        self.tallenna = ctk.CTkButton(self.left_frame, text = Translator.get_string('STR_UI_TALLENNA_SESSIO'), font = root.layout3_left_font, width = 0.965*(root.layout3_left_width * width), height = root.layout3_left_height)
        self.tallenna.place(x = 0, y = 3*root.layout3_left_pady + 2*root.layout3_left_height)


        # Middle middle frame

        text_box_width = 760
        text_box_height = 75
        button_width = 75
        padx = 10
        pady = 5
        self.description = ctk.CTkTextbox(self.middle_middle_frame, height = text_box_height, width = text_box_width, fg_color = self.root.layout3_frame_color, font = ('Helvetica', 17))
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
        self.middle_bottom_frame.product_label = tk.Label(self.middle_bottom_frame, bg= self.root.layout3_frame_color)

    def set_layout3(self):

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
        size = self.root.layout3_product_image_size

        if aspect_ratio > 1: # if figure is wider than higher
            new_width = size
            new_height = (height/width) * size
        else:
            new_height = size
            new_width = aspect_ratio * size

        resized_image =  img.resize((int(new_width), int(new_height)),Image.ANTIALIAS) # Resize image
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
class layout2:

    def __init__(self, parent, content_frame, root):

        width, height = root.dimensions[0], (1-root.menu_bar_rel_h)*root.dimensions[1]
        corner_radius = 10
        self.parent = parent
        self.root = root
        self.content_frame = content_frame

        self.left_frame = ctk.CTkFrame(self.content_frame, corner_radius=corner_radius, width = root.layout2_left_width*width, height = height)
        self.mid_frame = ctk.CTkFrame(self.content_frame, corner_radius=corner_radius, width = root.layout2_middle_width*width, height = height, fg_color = root.layout2_frame_color)
        self.right_frame = ctk.CTkFrame(self.content_frame, corner_radius=corner_radius, width = root.layout2_right_width*width, height = height, fg_color = root.layout2_frame_color)

        self.update_but = ctk.CTkButton(self.left_frame, text = Translator.get_string('STR_UI_PAIVITA'), corner_radius = corner_radius, height = root.layout2_left_button_height, width = root.layout2_left_width*width - 2*root.layout2_left_button_pad, font = root.layout2_left_font)
        self.info_table = ctk.CTkTextbox(self.left_frame, width = root.layout2_left_width*width - 2*root.layout2_left_button_pad)

        dbs = [db.strip('.db') for db in os.listdir(PATH+'/Databases') if db.endswith('.db')]
        self.provider_stringvar = tk.StringVar(value=dbs[0])
        self.provider = ctk.CTkOptionMenu(self.mid_frame, corner_radius = corner_radius, width = root.layout2_mid_menu_width, height = root.layout2_mid_menu_height, font = root.layout2_left_font, variable = self.provider_stringvar, values = dbs)

        self.read_db(f'{PATH}/Databases/{dbs[0]}.db')

        style = Style(root)
        style.theme_use("clam")
        style.configure("Treeview", background="light yellow", 
                fieldbackground="light yellow", foreground="black")
        self.tree = Treeview(self.mid_frame)

        self.scroll_bar = tk.Scrollbar(self.mid_frame, orient="vertical", command=self.tree.yview)
        
        self.scroll_bar.place_configure(height= root.layout2_treeview_height)
        self.tree.configure(yscrollcommand = self.scroll_bar.set)

        types = self.find_product_types('type')
        colors = self.find_product_types('color')
        sizes = self.find_product_types('size')
        self.name_search = ctk.CTkEntry(self.mid_frame)
        self.type_search = ctk.CTkComboBox(self.mid_frame, values = types)
        self.color_search = ctk.CTkComboBox(self.mid_frame, values = colors)
        self.size_search = ctk.CTkComboBox(self.mid_frame, values = sizes)
        self.add_product = ctk.CTkButton(self.mid_frame, text = Translator.get_string('STR_UI_LISAA_KORIIN'),  width = 150, height = 28, font = ('Helvetica', 15), command = self.add_product)
        self.filters = [self.name_search, self.type_search, self.color_search, self.size_search]
        self.search = ctk.CTkButton(self.mid_frame, bg_color = 'yellow', text = Translator.get_string('STR_UI_HAE_TUOTTEET'), command=self.fill_treeview, width = 150, height = 28, font = ('Helvetica', 15))
        self.img_label = ctk.CTkLabel(self.right_frame, width = root.layout2_right_width*width - 2*root.layout2_right_pad, height = root.layout2_right_width*width)
        self.info = ctk.CTkLabel(self.right_frame, bg_color = 'blue', width = root.layout2_right_width*width - 2*root.layout2_right_pad, height = 200)
        self.info_label = ctk.CTkLabel(self.mid_frame, text = '', text_color = 'black', font = ('Helvetica', 15))
        root.menu_bar.search_button.configure(command = self.set_layout2)

        self.read_columns()
        self.set_filters()
    def set_layout2(self):

        clear_frame(self.content_frame)

        width, height = self.root.dimensions[0], (1-self.root.menu_bar_rel_h)*self.root.dimensions[1]

        self.left_frame.place(x = 0, y = 0)
        self.mid_frame.place(x = self.root.layout2_left_width*width, y = 0)
        self.right_frame.place(x = self.root.layout2_left_width*width + 10 + self.root.layout2_middle_width*width, y = 0)

        self.update_but.place(x = 10, y = 10)
        self.info_table.place(x = self.root.layout2_left_button_pad, y = 2*self.root.layout2_left_button_pad + self.root.layout2_left_button_height)
        self.provider.place(x = (self.root.layout2_middle_width*width)/2 - self.root.layout2_mid_menu_width/2, y = 10)

        #self.name_search.place(x = 10, y = self.root.layout2_mid_menu_height + 50)
        #self.type_search.place(x = 200, y = self.root.layout2_mid_menu_height + 50)
        #self.color_search.place(x = 390, y = self.root.layout2_mid_menu_height + 50)
        self.search.place(x = self.root.layout2_middle_width*width - 172, y = self.root.layout2_mid_menu_height + 65)

        self.tree.place(x = 10, y = self.root.layout2_mid_menu_height + self.root.layout2_buttons_height + 60, height = self.root.layout2_treeview_height)
        self.info_label.place(x = 10, y = self.root.layout2_mid_menu_height + self.root.layout2_buttons_height + 65 + self.root.layout2_treeview_height)
        self.add_product.place(x = self.root.layout2_middle_width*width - 172, y = self.root.layout2_mid_menu_height + self.root.layout2_buttons_height + 65 + self.root.layout2_treeview_height)
        self.scroll_bar.place(x = self.root.layout2_middle_width  * width - 20, y = self.root.layout2_mid_menu_height + self.root.layout2_buttons_height + 60)
        self.img_label.place(x = self.root.layout2_right_pad, y = self.root.layout2_right_pad)
        self.info.place(x = self.root.layout2_right_pad, y = 2*self.root.layout2_right_pad + self.root.layout2_right_width*width)

    def find_product_types(self, type):
        
        try:
            names = self.db[type].tolist()
        except:
            names = []    
        return list(set(names))
    
    def read_db(self, path):

        self.db = pd.read_csv(path)

    def forget_filters(self):

        for filter in self.filters:
            filter.place_forget()

    def set_filters(self):
            
        self.forget_filters()
        self.color_search.set('')
        self.type_search.set('')
        self.size_search.set('')    

        cols = self.tree["columns"]
        length = (self.root.layout2_middle_width*self.root.dimensions[0]-40)/(len(cols)+1)
        
        self.name_search.place(x = 10, y = self.root.layout2_mid_menu_height + 65)
        self.name_search.configure(width = length-10)

        index = 1

        for col in cols[:-1]:
            if col == 'Tyyppi':
                self.type_search.place(x = 10 + index * length, y = self.root.layout2_mid_menu_height + 65)
                self.type_search.configure(width = length-10)
                index = index + 1

            elif col == 'Väri':    
                self.color_search.place(x = 10 + index * length, y = self.root.layout2_mid_menu_height + 65)
                self.color_search.configure(width = length-10)
                index = index + 1

            elif col == 'Koko':

                self.size_search.place(x = 10 + index * length, y = self.root.layout2_mid_menu_height + 65)
                self.size_search.configure(width = length-10)
                index = index + 1

    def read_columns(self):

        db_name = self.provider_stringvar.get()

        self.db = pd.read_csv(f'{PATH}/Databases/{db_name}.db')

        W = self.root.layout2_middle_width* self.root.dimensions[0] - 30

        self.columns = list(self.db.columns)

        to_be_shown = []

        for item in self.columns:
            if item == 'name' or item =='Name':
                to_be_shown.append('Tuotenimi')

            if item == 'type' or item == 'Type':
                to_be_shown.append('Tyyppi')

            if item == 'color' or item == 'Color':
                to_be_shown.append('Väri')

            if item == 'size' or item == 'Size':
                to_be_shown.append('Koko')

            if item == 'price' or item == 'Price':
                to_be_shown.append('Hinta')                

        self.tree["columns"] = to_be_shown[1:]
        self.tree.heading("#0", text=to_be_shown[0])

        for column in self.tree['columns']:
            self.tree.heading(column, text = column, anchor = 'center')
            self.tree.column(column, width= int(W/len(to_be_shown))) 

        self.tree.bind("<ButtonRelease-1>", lambda event: self.open_image(event))
        self.tree.bind("<Double-1>", lambda event: self.open_url(event)) # Web page open   

    def find_children_parent_relations(self, data_rows):

        parent_children = []
        has_been_seen = []

        for row in data_rows:
            product_name = row[0]
            if product_name not in has_been_seen:
                parent_children.append((row, []))
                has_been_seen.append(product_name)
            else:
                parent_children[-1][1].append(row)  
  
        return parent_children  
    
    def fill_treeview(self):

        self.clear_treeview()

        dataframe = self.db.sort_values(by = 'name') # must have order for find_children_parent_relations() to work
        
        dataframe = self.filter_dataframe(dataframe)
        data_rows = dataframe.to_numpy().tolist()

        data_parent_child = self.find_children_parent_relations(data_rows)

        for parent, children in data_parent_child:
            daddy = self.tree.insert('', 'end', text = parent[0], values = parent[1:])  
            for child in children:
                self.tree.insert(daddy, "end", text = child[0], values = child[1:])
        #else:
        #    for row in data_rows:
        #        self.tree.insert('', 'end', text = row[0], values = row[1:])  

        self.info_label.configure(text = f'{len(data_rows)} tuotetta löytyi.')
        return len(data_rows)

    def get_search_params(self):

        base = zip(['name', 'type', 'color', 'size'], self.filters)
        filters = []
        for datatype, search_object in base:

            if len(search_object.get().strip()) == 0:
                continue
            else:
                filters.append((datatype, search_object.get().strip()))
        return filters 

    def filter_dataframe(self, dataframe):

        filters = self.get_search_params()

        reduced_dataframe = dataframe.copy()

        for filter in filters:

            filter_type, value = filter

            if filter_type == 'name':
                reduced_dataframe = reduced_dataframe[reduced_dataframe['name'].str.contains(value, case=False, na=False)]
                continue    
            try:
                reduced_dataframe = reduced_dataframe[reduced_dataframe[filter_type] == value]
            except:
                pass
        return reduced_dataframe 

    def clear_treeview(self):   

        for item in self.tree.get_children():
            self.tree.delete(item)       

    def add_product(self):

        rows = self.tree.selection()

        list(self.db.columns)

        for row in rows:

            name = self.tree.item(row, 'text')
            data = list(self.tree.item(row, 'values'))
            data.insert(0, name)
            attributes = list(self.db.columns)

#image(self.middle_up_frame, position, index, path, self, side_length = 100, root = self.root, discount = 20, product_data = ['HanaX', '900€', 'Chrome']))
            datas = {attributes[i]: data[i] for i in range(len(attributes)) if attributes[i] in ('name', 'size', 'color', 'price', 'number', 'webpage')}

            img_frame = self.root.content_frame.layout3.middle_up_frame
            index = len(img_frame.images)
            position = img_frame.positions[index]

            company = self.provider_stringvar.get()
            path = PATH +f'\\Figures\\{company}\\'

            if company == 'Tapwell':

                to_search = [datas['number']]

            if company == 'Haven':

                color = datas[1]
                to_search = [name, f"{datas['name']}_{datas['color']}"]

            for srch in to_search:
                if os.path.isfile(path+srch+'.png'):
                    path = path+srch+'.png'
                    break
            else:
                print('Image not found!')
                return        
            img_frame.images.append(image(img_frame, position = position, index = index, path = path, parent_layout = self.root.content_frame.layout3, side_length = 100, root = self.root, discount = 0, product_data = datas))
        
        if len(rows) != 1:
            self.info_label.configure(text = f'{len(rows)} tuotetta lisättiin koriin.')
        else:
            self.info_label.configure(text = f"{datas['name']} lisättiin koriin.")
    def open_image(self, event):
   
        self.img_label.configure(text = '')
        item = self.tree.identify_row(event.y)
        datas = self.tree.item(item, "values")

        if len(datas) == 0:
            return
        
        name = self.tree.item(item, 'text')

        company = self.provider_stringvar.get()
        path = PATH +f'\\Figures\\{company}\\'

        if company == 'Tapwell':

            to_search = [datas[3]]

        if company == 'Haven':

            color = datas[1]
            to_search = [name, f'{name}_{color}']

        for srch in to_search:
            if os.path.isfile(path+srch+'.png'):
                image = Image.open(path+srch+'.png').convert("RGBA")
                
                width, height = image.size
                aspect_ratio = width / height
                if height > width:
                    new_height = self.img_label.winfo_height()
                    new_width = int(aspect_ratio * new_height)
                else:
                    
                    new_width = self.img_label.winfo_width()
                    new_height = int((1/aspect_ratio) * new_width)
                    
                resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
                self.ctk_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size = (new_width, new_height))

                self.img_label.configure(image = self.ctk_image)
                #self.img_label.image = self.ctk_image
  

    def open_url(self, event):

        item = self.tree.identify_row(event.y)  

        vals = self.tree.item(item, "values")

        for val in vals:
            if 'www.' in val:
                webbrowser.open_new(val)  

class ContentFrame():

    def __init__(self, root):
        
        window_width, window_height = root.dimensions
        self.root = root

        self.content_frame = ctk.CTkFrame(root, height=0.95*window_height, width = 1*window_width)
        self.content_frame.pack(pady = 10, padx = 10)

        # Tarjouksen luontiin vaadittavat widgetit

        self.layout3 = layout3(self, self.content_frame, root)
        self.layout2 = layout2(self, self.content_frame, root)

