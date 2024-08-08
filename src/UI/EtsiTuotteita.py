import customtkinter as ctk
import tkinter as tk
from tkinter.ttk import Style, Treeview
from PIL import Image
from GlobalAssets.Translator import Translator
from GlobalAssets.UIDimensions import UIDimensions
from image import *
import webbrowser
import pandas as pd
import shutil

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
                                        text = Translator.get_string('STR_UI_LUO_UUSI_TUOTE'), 
                                        corner_radius = corner_radius, 
                                        height = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_HEIGHT_ABSOLUTE'), 
                                        width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE'), 
                                        font = etsi_tuotteita_left_font,
                                        command = self.create_own_product)
        
        self.info_table = ctk.CTkTextbox(self.left_frame, 
                                         width = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_WIDTH_FRACTION')*width - 2*UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','LEFT_BUTTON_PAD_ABSOLUTE'))

        self.info_table.insert(ctk.END, "Jan mitä vittuu me laitetaan tänne")
        dbs = [db.strip('.db') for db in os.listdir(os.path.join(PATH,'Databases')) if db.endswith('.db')]

        try: # Laitetaan Omat viimeiseksi
            dbs.remove('Omat')
            dbs.append('Omat')
        except:
            pass

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
        companies = self.find_product_types('company')
        self.name_search = ctk.CTkEntry(self.mid_frame)
        self.type_search = ctk.CTkComboBox(self.mid_frame, 
                                           values = types)
        self.color_search = ctk.CTkComboBox(self.mid_frame, 
                                            values = colors)
        self.size_search = ctk.CTkComboBox(self.mid_frame, 
                                           values = sizes)
        
        self.company_search = ctk.CTkComboBox(self.mid_frame,
                                              values = companies)

        self.add_product = ctk.CTkButton(self.mid_frame, 
                                         text = Translator.get_string('STR_UI_LISAA_KORIIN'), 
                                         width = 150, 
                                         height = 28, 
                                         font = ('Helvetica', 15), 
                                         command = self.add_product)
        self.filters = [self.name_search, self.type_search, self.color_search, self.size_search, self.company_search]
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
                                 font = ('Helvetica', 20),
                                 text = '',
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

        self.db = pd.read_csv(path, encoding='utf-8')

    def forget_filters(self):

        for filter in self.filters:
            filter.place_forget()

    def set_filters(self):
            
        self.forget_filters()
        self.color_search.set('')
        self.type_search.set('')
        self.size_search.set('')
        self.company_search.set('')    

        cols = self.tree["columns"]
        length = (UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MIDDLE_WIDTH_FRACTION')*UIDimensions.get('MAIN_APP','X')-40)/(len(cols)+1)
        
        self.name_search.place(x = 10, 
                               y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
        self.name_search.configure(width = length-10)

        index = 1

        for col in cols[:-1]:

            if col == 'Toimittaja':

                self.company_search.place(x = 10 + index + length, y = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','MID_MENU_HEIGTH_ABSOLUTE') + 65)
                self.company_search.configure(width = length - 10)
                index += 1

            elif col == 'Tyyppi':
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
        self.db = pd.read_csv(os.path.join(PATH,'Databases',f'{self.db_name}.db'), na_filter=False, encoding='utf-8')

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
           
            if self.db_name == 'Omat' and item in ['company', 'Company']:
                to_be_shown.append('Toimittaja')
        
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
            sizes = self.find_product_types('size')
            companies = self.find_product_types('company')

            self.color_search.configure(values = colors)
            self.type_search.configure(values = types)
            self.company_search.configure(values = companies)
            self.size_search.configure(values = sizes)

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

        base = zip(['name', 'type', 'color', 'size', 'company'], self.filters)
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

            datas = {attributes[i]: data[i] for i in range(len(attributes)) if attributes[i] in ('name', 'size', 'color', 'price', 'number', 'company', 'info', 'description')}

            img_frame = self.root.content_frame.luo_tarjous.middle_up_frame
            index = len(img_frame.images)
            position = img_frame.positions[index]

            company = self.db_name

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
        
            if company == 'Omat':
                fig_name = data[-1]
                to_search = [fig_name]

            for srch in to_search:

                if  '.png' in srch or '.jpeg' in srch or '.JPEG' in srch or '.jpg' in srch:
                    file_path = os.path.join(PATH, 'Figures', company, f'{srch}')
                else:
                    file_path = os.path.join(PATH, 'Figures', company, f'{srch}.png')  

                if os.path.isfile(file_path):
                    break
            else:
                print('Image not found!')
                return  
            print(datas)      
            img_frame.images.append(image(img_frame, position = position, index = index, path = file_path, parent_layout = self.root.content_frame.luo_tarjous, side_length = 100, root = self.root, discount = 0, product_data = datas))
        
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

        if company == 'Omat':
            fig_name = datas[-1]
            description = datas[-2]
            to_search = [fig_name]    
            self.info.configure(text = description.replace('¤', ','))

        for srch in to_search:

            if '.png' in srch or '.jpg' in srch or '.jpeg' in srch or '.JPG' in srch:
                figure_path = os.path.join(path,f'{srch}')
            else:    
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

    def create_own_product(self):

        pad_y1 = 3
        pad_y2 = 10
        pad_x = 5 

        font_size = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','POP-UP_FONT_SIZE')
        font_size_text = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA','POP-UP_TEXT_SIZE')
        fontt = UIDimensions.get('DIM_UI_ETSI_TUOTTEITA', 'PAIVITA_FONT')

        font = (fontt, font_size)
        font_text = (fontt, font_size_text)

        self.popup = tk.Toplevel(self.root, bg = "#1e1e1e")

        self.popup.title("Luo oma tuote")
        self.popup.geometry("900x326")

        self.popup.name = ctk.CTkLabel(self.popup, text = 'Tuotenimi', font = font)
        self.popup.name.grid(row = 0, column = 0, padx = pad_x, pady = pad_y1)
         
        self.popup.company = ctk.CTkLabel(self.popup, text = 'Toimittaja', font = font)
        self.popup.company.grid(row = 0, column = 1, padx = pad_x, pady = pad_y1)

        self.popup.type = ctk.CTkLabel(self.popup, text = 'Tyyppi', font = font)
        self.popup.type.grid(row = 0, column = 2, padx = pad_x, pady = pad_y1)

        self.popup.color = ctk.CTkLabel(self.popup, text = 'Väri', font = font)
        self.popup.color.grid(row = 0, column = 3, padx = pad_x, pady = pad_y1)

        self.popup.size = ctk.CTkLabel(self.popup, text = 'Koko', font = font)
        self.popup.size.grid(row = 0, column = 4, padx = pad_x, pady = pad_y1)

        self.popup.price = ctk.CTkLabel(self.popup, text = 'Hinta', font = font)
        self.popup.price.grid(row = 0, column = 5, padx = pad_x, pady = pad_y1)

        # Rivivaihto

        self.popup.name_entry = ctk.CTkEntry(self.popup)
        self.popup.name_entry.grid(row = 1, column = 0, padx = pad_x)

        self.popup.company_entry = ctk.CTkComboBox(self.popup)
        self.popup.company_entry.configure(values=["INR", "Svedbergs", "Haven", "Tapwell", 'Duravit', 'IDO', 'Geberit', 'Gessi', 'INK', 'Oras', 'Axor', 'Temal', 'Smedbo', 'Hietakari', 'Vieser', 'Rejdesign'])
        self.popup.company_entry.grid(row = 1, column = 1, padx = pad_x)
        self.popup.company_entry.set("")

        self.popup.type_entry = ctk.CTkEntry(self.popup, font = font)
        self.popup.type_entry.grid(row = 1, column = 2, padx = pad_x, pady = pad_y1)

        self.popup.color_entry = ctk.CTkEntry(self.popup)
        self.popup.color_entry.grid(row = 1, column = 3, padx = pad_x,)

        self.popup.size_entry = ctk.CTkEntry(self.popup)
        self.popup.size_entry.grid(row = 1, column = 4, padx = pad_x)

        self.popup.price_entry = ctk.CTkEntry(self.popup)
        self.popup.price_entry.grid(row = 1, column = 5, padx = pad_x)

        self.popup.description = ctk.CTkTextbox(self.popup, fg_color = '#739FA6', width = 890, font = font_text)
        self.popup.description.grid(row = 2, column = 0, columnspan = 6, rowspan = 3, pady = pad_y2)

        self.popup.add_figure = ctk.CTkButton(self.popup, font = font_text, text = 'Lisää kuva', command = self.set_figure_to_own_product)
        self.popup.add_figure.grid(row = 7, column = 0, padx = pad_x)

        self.popup.info_label = ctk.CTkLabel(self.popup, text = '', font = ('Helvetica', 17))
        self.popup.info_label.grid(row = 7, column = 1, columnspan = 4)

        self.popup.create = ctk.CTkButton(self.popup, text = 'Luo tuote', font=font, fg_color = '#006400', command = self.save_own_product)
        self.popup.create.grid(row = 7, column = 5, padx = pad_x)

        self.own_figure_name = ' '

        self.popup.lift()
        self.popup.focus_force()

    def save_own_product(self):

        name = self.popup.name_entry.get().strip()

        if name == '':
            self.popup.info_label.configure(text = 'Tuotteella tulee olla nimi')  
            self.root.after(3000, lambda: self.popup.info_label.configure(text=''))
            return

        company = self.popup.company_entry.get().strip()
        type = self.popup.type_entry.get().strip()
        color = self.popup.color_entry.get().strip()
        size = self.popup.size_entry.get().strip()
        price = self.popup.price_entry.get().strip()

        try:
            float(price)
        except:
            self.popup.info_label.configure(text = 'Vain numerot kelpaavat hinnaksi')  
            self.root.after(3000, lambda: self.popup.info_label.configure(text=''))
            return

        description = self.popup.description.get("1.0", "end").strip()
        figure = self.own_figure_name

        description = description.replace('\n', ' ')
        description = description.replace('  ', ' ')
        description = description.replace(',', '¤')

        data = (name, company, type, color, size, price, description, figure)

        data_String = ''

        for item in data:
            if item == '':
                data_String = data_String + ' ,'
            else:
                data_String = data_String + f'{item},' 

        data_String = data_String[:-1]

        with open(os.path.join(PATH, 'Databases', 'Omat.db'), 'a', encoding='utf-8') as file:
            file.write(data_String + '\n')

        self.popup.destroy()

    def set_figure_to_own_product(self):
        # Open a file dialog to select an image
        file_source = tk.filedialog.askopenfilename(
            title="Open an Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )

        self.popup.lift()
        self.popup.focus_force()

        if not file_source:
            print("No file selected.")
            return None

        # Directory where the files will be copied
        target_dir = os.path.join(PATH, 'Figures', 'Omat')

        # List all files in the target directory
        files = os.listdir(target_dir)

        indices = []
        for file in files:
            try:
                indices.append((int(file.split('.')[0]), file.split('.')[-1]))
            except ValueError:
                pass  # Skip files that don't fit the expected pattern

        if indices:
            # Get the maximum index and determine the new file name
            max_index, filetype = max(indices, key=lambda x: x[0])
            new_index = max_index + 1
        else:
            # Start from index 1 if the directory is empty or no valid files found
            new_index = 1
            filetype = file_source.split('.')[-1]  # Use the source file's extension

        file_name = f"{new_index}.{filetype}"
        file_target = os.path.join(target_dir, file_name)

        # Copy the file to the target directory with the new name
        shutil.copy(file_source, file_target)

        self.own_figure_name = str(new_index) + f'.{filetype}'

        self.popup.info_label.configure(text = 'Kuva tallennettiin')
        self.root.after(3000, lambda: self.popup.info_label.configure(text=''))
            