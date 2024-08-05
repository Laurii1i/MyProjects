import customtkinter as ctk
import tkinter as tk
from tkinter.ttk import Style, Treeview
from PIL import Image
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions
from image import *
import webbrowser
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

class EtsiTuotteita:

    def __init__(self, parent, content_frame, root):

        width = UIDimensions.get('MAIN_APP','X')
        height = (1-UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION'))*UIDimensions.get('MAIN_APP','Y')
        corner_radius = 10
        etsi_tuotteita_left_font = (UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','PAIVITA_FONT'), UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','PAIVITA_FONT_SIZE'))
        self.parent = parent
        self.root = root
        self.content_frame = content_frame

        self.left_frame = ctk.CTkFrame(self.content_frame, 
                                       corner_radius=corner_radius, 
                                       width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width, 
                                       height = height)
        self.mid_frame = ctk.CTkFrame(self.content_frame, 
                                      corner_radius=corner_radius, 
                                      width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*width, 
                                      height = height, 
                                      fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"])
        self.right_frame = ctk.CTkFrame(self.content_frame, 
                                        corner_radius=corner_radius, 
                                        width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_WIDTH_FRACTION')*width, 
                                        height = height, 
                                        fg_color = ctk.ThemeManager.theme["CustomFrameBackground"]["fg_color"])

        self.update_but = ctk.CTkButton(self.left_frame, 
                                        text = Translator.get_string('STR_UI_PAIVITA'), 
                                        corner_radius = corner_radius, 
                                        height = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_HEIGHT_ABSOLUTE'), 
                                        width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE'), 
                                        font = etsi_tuotteita_left_font)
        self.info_table = ctk.CTkTextbox(self.left_frame, 
                                         width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE'))

        dbs = [db.strip('.db') for db in os.listdir(os.path.join(PATH,'Databases')) if db.endswith('.db')]
        self.provider_stringvar = tk.StringVar(value=dbs[0])
        self.provider = ctk.CTkOptionMenu(self.mid_frame, 
                                          corner_radius = corner_radius, 
                                          width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_WIDTH_ABSOLUTE'), 
                                          height = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE'), 
                                          font = etsi_tuotteita_left_font, 
                                          variable = self.provider_stringvar, 
                                          values = dbs)

        self.read_db(os.path.join(PATH,'Databases',f'{dbs[0]}.db'))

        self.db_name = dbs[0]
        style = Style(root)
        style.theme_use("clam")
        style.configure("Treeview", background="light yellow", 
                fieldbackground="light yellow", foreground="black")

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
                                    text = Translator.get_string('STR_UI_HAE_TUOTTEET'), 
                                    command=self.fill_treeview, 
                                    width = 150, 
                                    height = 28, 
                                    font = ('Helvetica', 15))
        self.img_label = ctk.CTkLabel(self.right_frame, 
                                      text = '',
                                      width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE'), 
                                      height = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_WIDTH_FRACTION')*width)
        self.info = ctk.CTkLabel(self.right_frame, 
                                 width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE'), 
                                 height = 200,
                                 font = ('Helvetica', 15),
                                 wraplength = 400)
        self.info_label = ctk.CTkLabel(self.mid_frame, text = '', text_color = 'black', font = ('Helvetica', 15))
        root.menu_bar.search_button.configure(command = self.set_layout)

        self.read_columns()
        self.set_filters()
    def set_layout(self):

        clear_frame(self.content_frame)

        width = UIDimensions.get('MAIN_APP','X')
        height = (1-UIDimensions.get('DIM_UI_MENU_BAR','HEIGHT_FRACTION'))*UIDimensions.get('MAIN_APP','Y')

        self.left_frame.place(x = 0, y = 0)
        self.mid_frame.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width, 
                             y = 0)
        self.right_frame.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width + 10 + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*width, 
                               y = 0)

        self.update_but.place(x = 10, 
                              y = 10)
        self.info_table.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE'), 
                              y = 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_HEIGHT_ABSOLUTE'))
        self.provider.place(x = (UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*width)/2 - UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_WIDTH_ABSOLUTE')/2, 
                            y = 10)

        #self.name_search.place(x = 10, y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        #self.type_search.place(x = 200, y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        #self.color_search.place(x = 390, y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 50)
        self.search.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*width - 172, 
                          y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)

        self.info_label.place(x = 10, 
                              y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','BUTTONS_HEIGHT_ABSOLUTE') + 65 + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.add_product.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*width - 172, 
                               y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','BUTTONS_HEIGHT_ABSOLUTE') + 65 + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','TREEVIEW_HEIGHT_ABSOLUTE'))
    
        self.img_label.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE'), 
                             y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE'))
        self.info.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE'), 
                        y = 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_PAD_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','RIGHT_WIDTH_FRACTION')*width)

    def find_product_types(self, type):
        
        try:
            names = self.db[type].tolist()
        except:
            names = []  
    
        listy = list(set(names))

        stripped = []
        for item in listy:
            stripped.append(item.strip())

        if ' ' in stripped:
            listy.remove(' ')
        if '' in stripped:
            stripped.remove('')    
        return stripped
    
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
        length = (UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*UIDimensions.get('MAIN_APP','X')-40)/(len(cols)+1)
        
        self.name_search.place(x = 10, 
                               y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
        self.name_search.configure(width = length-10)

        index = 1

        for col in cols[:-1]:
            if col == 'Tyyppi':
                self.type_search.place(x = 10 + index * length, 
                                       y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.type_search.configure(width = length-10)
                index = index + 1

            elif col == 'Väri':    
                self.color_search.place(x = 10 + index * length, 
                                        y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.color_search.configure(width = length-10)
                index = index + 1

            elif col == 'Koko':

                self.size_search.place(x = 10 + index * length, 
                                       y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.size_search.configure(width = length-10)
                index = index + 1

    def read_columns(self):

        if hasattr(self, 'tree'):
            self.tree.destroy()
            self.scroll_bar.destroy()

        width = UIDimensions.get('MAIN_APP','X')
        self.tree = Treeview(self.mid_frame)
        self.scroll_bar = tk.Scrollbar(self.mid_frame, orient="vertical", command=self.tree.yview)
        
        self.scroll_bar.place_configure(height= UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.tree.configure(yscrollcommand = self.scroll_bar.set)

        self.tree.place(x = 10, 
                        y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','BUTTONS_HEIGHT_ABSOLUTE') + 60, 
                        height = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','TREEVIEW_HEIGHT_ABSOLUTE'))
        self.scroll_bar.place(x = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')  * width - 20, 
                              y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','BUTTONS_HEIGHT_ABSOLUTE') + 60)
    
        # Read the CSV file with na_filter set to False
        self.db = pd.read_csv(os.path.join(PATH,'Databases',f'{self.db_name}.db'), na_filter=False)

        W = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')* UIDimensions.get('MAIN_APP','X') - 30

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

        
        column_width = int(W/(len(to_be_shown)))
        self.tree["columns"] = to_be_shown[1:]
        self.tree.heading("#0", text=to_be_shown[0])

        self.tree.column("#0", width = column_width, minwidth = 50)

        for column in self.tree['columns']:
            self.tree.heading(column, text = column, anchor = 'center')
            self.tree.column(column, width = column_width, minwidth = 40)

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

        if self.provider_stringvar.get() != self.db_name:
            self.db_name = self.provider_stringvar.get()
            self.read_columns()
            self.set_filters()
            colors = self.find_product_types('color')
            types = self.find_product_types('type')
            self.color_search.configure(values = colors)
            self.type_search.configure(values = types)

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

        self.tree.delete(*self.tree.get_children())       

    def add_product(self):

        rows = self.tree.selection()

        for row in rows:

            name = self.tree.item(row, 'text')
            data = list(self.tree.item(row, 'values'))
            data.insert(0, name)
            attributes = list(self.db.columns)

            datas = {attributes[i]: data[i] for i in range(len(attributes)) if attributes[i] in ('name', 'size', 'color', 'price', 'number', 'webpage', 'info')}

            img_frame = self.root.content_frame.luo_tarjous.middle_up_frame
            index = len(img_frame.images)
            position = img_frame.positions[index]

            company = self.db_name
            path = PATH +f'\\Figures\\{company}\\'

            if company == 'Tapwell':

                to_search = [datas['number']]

            if company == 'Haven':

                color = datas['color']
                info = datas['info']

                if not 'H2⁄' in name:
                    to_search = [name, f'{name}_{color}']

                else:  

                    if 'MIRROR' in name or 'CABINET' in name:
                        name = name.split(' ')[0]           
                        add1 = 'CABINET' if 'MIRROR CABINET' in info else 'MIRROR'    
                        add2 = 'STONE-TOP' if 'STONE TOP' in info else 'PORCELAIN'

                        ADD = f'+{add1}+{add2}'
                        to_search = [f'{name}{ADD}_{color}']
                    else:
                        to_search = [name, f'{name}_{color}']

                self.info.configure(text = info)

            if company == 'INR':
                to_search = [datas['name']]
            
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
   
        self.info.configure(text = '')
        self.img_label.configure(image = '')
        item = self.tree.identify_row(event.y)
        datas = self.tree.item(item, "values")

        if len(datas) == 0:
            return
        
        name = self.tree.item(item, 'text')

        company = self.db_name

        path = os.path.join(PATH, 'Figures', company)

        if company == 'Tapwell':

            to_search = [datas[3]]

        print(datas)
        if company == 'Haven':

            color = datas[1]
            info = datas[-1]

            if not 'H2⁄' in name:
                to_search = [name, f'{name}_{color}']

            else:  

                if 'MIRROR' in name or 'CABINET' in name:
                    name = name.split(' ')[0]           
                    add1 = 'CABINET' if 'MIRROR CABINET' in info else 'MIRROR'    
                    add2 = 'STONE-TOP' if 'STONE TOP' in info else 'PORCELAIN'

                    ADD = f'+{add1}+{add2}'
                    to_search = [f'{name}{ADD}_{color}']
                else:
                    to_search = [name, f'{name}_{color}']

            self.info.configure(text = info)

        if company == 'INR':
            color = datas[1]
            info = datas[-1]
            to_search = [name]
            self.info.configure(text = info)
            
        for srch in to_search:

            figure_path = os.path.join(path,f'{srch}.png')
            if os.path.isfile(figure_path):
                image = Image.open(figure_path).convert("RGBA")
                
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
  

    def open_url(self, event):

        item = self.tree.identify_row(event.y)  

        vals = self.tree.item(item, "values")

        for val in vals:
            if 'www.' in val:
                webbrowser.open_new(val)  