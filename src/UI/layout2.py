import customtkinter as ctk
import tkinter as tk
from tkinter.ttk import Style, Treeview
from PIL import Image
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions
from image import *
import pandas as pd

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

class layout2:

    def __init__(self, parent, content_frame, root):

        width = UIDimensions.get('MAIN_APP','X')
        height = (1-UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION'))*UIDimensions.get('MAIN_APP','Y')
        corner_radius = 10
        layout2_left_font = (UIDimensions.get('DIM_UI_LAYOUT2','PAIVITA_FONT'), UIDimensions.get('DIM_UI_LAYOUT2','PAIVITA_FONT_SIZE'))
        self.parent = parent
        self.root = root
        self.content_frame = content_frame

        self.left_frame = ctk.CTkFrame(self.content_frame, 
                                       corner_radius=corner_radius, 
                                       width = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')*width, 
                                       height = height)
        self.mid_frame = ctk.CTkFrame(self.content_frame, 
                                      corner_radius=corner_radius, 
                                      width = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*width, 
                                      height = height, 
                                      fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"])
        self.right_frame = ctk.CTkFrame(self.content_frame, 
                                        corner_radius=corner_radius, 
                                        width = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')*width, 
                                        height = height, 
                                        fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"])

        self.update_but = ctk.CTkButton(self.left_frame, 
                                        text = Translator.get_string('STR_UI_PAIVITA'), 
                                        corner_radius = corner_radius, 
                                        height = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_HEIGHT_ABSOLUTE'), 
                                        width = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_PAD_ABSOLUTE'), 
                                        font = layout2_left_font)
        self.info_table = ctk.CTkTextbox(self.left_frame, 
                                         width = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_PAD_ABSOLUTE'))

        dbs = [db.strip('.db') for db in os.listdir(os.path.join(PATH,'Databases')) if db.endswith('.db')]
        self.provider_stringvar = tk.StringVar(value=dbs[0])
        self.provider = ctk.CTkOptionMenu(self.mid_frame, 
                                          corner_radius = corner_radius, 
                                          width = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_WIDTH_ABSOLUTE'), 
                                          height = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE'), 
                                          font = layout2_left_font, 
                                          variable = self.provider_stringvar, 
                                          values = dbs)

        self.read_db(os.path.join(PATH,'Databases',f'{dbs[0]}.db'))

        style = Style(root)
        style.theme_use("clam")
        style.configure("Treeview", background="light yellow", 
                fieldbackground="light yellow", foreground="black")
        self.tree = Treeview(self.mid_frame)

        self.scroll_bar = tk.Scrollbar(self.mid_frame, orient="vertical", command=self.tree.yview)
        
        self.scroll_bar.place_configure(height= UIDimensions.get('DIM_UI_LAYOUT2','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.tree.configure(yscrollcommand = self.scroll_bar.set)

        types = self.find_product_types('type')
        colors = self.find_product_types('color')
        sizes = self.find_product_types('size')
        self.name_search = ctk.CTkEntry(self.mid_frame)
        self.type_search = ctk.CTkComboBox(self.mid_frame, 
                                           values = types)
        self.color_search = ctk.CTkComboBox(self.mid_frame, 
                                            values = colors)
        self.size_search = ctk.CTkComboBox(self.mid_frame, 
                                           values = sizes)
        self.add_product = ctk.CTkButton(self.mid_frame, 
                                         text = Translator.get_string('STR_UI_LISAA_KORIIN'), 
                                         width = 150, 
                                         height = 28, 
                                         font = ('Helvetica', 15), 
                                         command = self.add_product)
        self.filters = [self.name_search, self.type_search, self.color_search, self.size_search]
        self.search = ctk.CTkButton(self.mid_frame, 
                                    bg_color = 'yellow', 
                                    text = Translator.get_string('STR_UI_HAE_TUOTTEET'), 
                                    command=self.fill_treeview, 
                                    width = 150, 
                                    height = 28, 
                                    font = ('Helvetica', 15))
        self.img_label = ctk.CTkLabel(self.right_frame, 
                                      width = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE'), 
                                      height = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')*width)
        self.info = ctk.CTkLabel(self.right_frame, 
                                 bg_color = 'blue', 
                                 width = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE'), 
                                 height = 200)
        self.info_label = ctk.CTkLabel(self.mid_frame, text = '', text_color = 'black', font = ('Helvetica', 15))
        root.menu_bar.search_button.configure(command = self.set_layout2)

        self.read_columns()
        self.set_filters()
    def set_layout2(self):

        clear_frame(self.content_frame)

        width = UIDimensions.get('MAIN_APP','X')
        height = (1-UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION'))*UIDimensions.get('MAIN_APP','Y')

        self.left_frame.place(x = 0, y = 0)
        self.mid_frame.place(x = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')*width, 
                             y = 0)
        self.right_frame.place(x = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_WIDTH_FRACTION')*width + 10 + UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*width, 
                               y = 0)

        self.update_but.place(x = 10, 
                              y = 10)
        self.info_table.place(x = UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_PAD_ABSOLUTE'), 
                              y = 2*UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_PAD_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','LEFT_BUTTON_HEIGHT_ABSOLUTE'))
        self.provider.place(x = (UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*width)/2 - UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_WIDTH_ABSOLUTE')/2, 
                            y = 10)

        #self.name_search.place(x = 10, y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        #self.type_search.place(x = 200, y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        #self.color_search.place(x = 390, y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        self.search.place(x = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*width - 172, 
                          y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 65)

        self.tree.place(x = 10, 
                        y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','BUTTONS_HEIGHT_ABSOLUTE') + 60, 
                        height = UIDimensions.get('DIM_UI_LAYOUT2','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.info_label.place(x = 10, 
                              y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','BUTTONS_HEIGHT_ABSOLUTE') + 65 + UIDimensions.get('DIM_UI_LAYOUT2','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.add_product.place(x = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*width - 172, 
                               y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','BUTTONS_HEIGHT_ABSOLUTE') + 65 + UIDimensions.get('DIM_UI_LAYOUT2','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.scroll_bar.place(x = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')  * width - 20, 
                              y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','BUTTONS_HEIGHT_ABSOLUTE') + 60)
        self.img_label.place(x = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE'), 
                             y = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE'))
        self.info.place(x = UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE'), 
                        y = 2*UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_PAD_ABSOLUTE') + UIDimensions.get('DIM_UI_LAYOUT2','RIGHT_WIDTH_FRACTION')*width)

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
        length = (UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')*UIDimensions.get('MAIN_APP','X')-40)/(len(cols)+1)
        
        self.name_search.place(x = 10, 
                               y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 65)
        self.name_search.configure(width = length-10)

        index = 1

        for col in cols[:-1]:
            if col == 'Tyyppi':
                self.type_search.place(x = 10 + index * length, 
                                       y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.type_search.configure(width = length-10)
                index = index + 1

            elif col == 'Väri':    
                self.color_search.place(x = 10 + index * length, 
                                        y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.color_search.configure(width = length-10)
                index = index + 1

            elif col == 'Koko':

                self.size_search.place(x = 10 + index * length, 
                                       y = UIDimensions.get('DIM_UI_LAYOUT2','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.size_search.configure(width = length-10)
                index = index + 1

    def read_columns(self):

        db_name = self.provider_stringvar.get()

        self.db = pd.read_csv(os.path.join(PATH,'Databases',f'{db_name}.db'))

        W = UIDimensions.get('DIM_UI_LAYOUT2','MIDDLE_WIDTH_FRACTION')* UIDimensions.get('MAIN_APP','X') - 30

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

            img_frame = self.root.content_frame.luo_tarjous.middle_up_frame
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
            img_frame.images.append(image(img_frame, position = position, index = index, path = path, parent_layout = self.root.content_frame.luo_tarjous, side_length = 100, root = self.root, discount = 0, product_data = datas))
        
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
                    
                resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.ctk_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size = (new_width, new_height))

                self.img_label.configure(image = self.ctk_image)
                #self.img_label.image = self.ctk_image
  

    def open_url(self, event):

        item = self.tree.identify_row(event.y)  

        vals = self.tree.item(item, "values")

        for val in vals:
            if 'www.' in val:
                webbrowser.open_new(val)  