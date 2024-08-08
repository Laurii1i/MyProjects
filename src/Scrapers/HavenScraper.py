import re
import time
import pandas as pd
import os
from bs4 import BeautifulSoup
from CommonScraper import CommonScraper
import requests 

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)
PATH = os.path.join(PATH, '..')

class HavenScraper(CommonScraper):

    def __init__(self):

        super().__init__()
        self.company_name = 'Haven'
        self.website_url = 'https://haven-system.com'
        self.db_path = os.path.join(PATH, 'Databases', f'{self.company_name}.db')

    def scrape(self) -> pd.DataFrame:

        base = self.website_url

        lighting = 'https://haven-system.com/catalogue/tillbehor/lighting/'
        faucets = 'https://haven-system.com/catalogue/tillbehor/blandare/'
        interiors = 'https://haven-system.com/catalogue/tillbehor/inredning/'
        knobs = 'https://haven-system.com/catalogue/tillbehor/handtag_knoppar/'
        wall_cabinet = 'https://haven-system.com/catalogue/badrumsskap/vaggskap/'
        high_cabinet = 'https://haven-system.com/catalogue/badrumsskap/hogskap/'
        mirror_cabinet = 'https://haven-system.com/catalogue/badrumsspegel/spegelskap/'
        mirror = 'https://haven-system.com/catalogue/badrumsspegel/spegel/'
        H3_1 = 'https://haven-system.com/catalogue/H3/oval/'
        H3_2 = 'https://haven-system.com/catalogue/H3/spegelskap/'
        H2 = 'https://haven-system.com/catalogue/H2/'
        H2_MC = 'https://haven-system.com/catalogue/H2/spegelskap/'
        H2_M = 'https://haven-system.com/catalogue/H2/oval/'

        existing_images = os.listdir(PATH+'/Figures/Haven')
        existing_images = [fig.strip('.png') for fig in existing_images]

        db_structure = ('name','type','color', 'size', 'price','number','url','company', 'info')

        db_dict = {item: [] for item in db_structure}


        response  = requests.get(lighting)
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanel1 = soup.find(class_ = "BigImages Col2 clearfix")
            prodpanel2 = soup.find(class_ = "BigImages Col3 clearfix")

            prodpanel3 = soup.find(class_ = "BigImages Col4 clearfix")
            if prodpanel3 is not None:
                print(f'Haven: Uusi tuotepaneeli löytynyt osoitteessa {lighting}. Tämän paneelin tuotteita ei lisätä tietokantaan.\n')

            for panel in [prodpanel1, prodpanel2]:
                big_imgs = panel.find_all(class_ = 'BigImage')
                for big_img in big_imgs:
                    
                    banner = big_img.find("strong").get_text()
                    lamp_and_name = banner.split('-')[0].strip()
                    name = lamp_and_name.split(' ')[-1]

                    placement = banner.split('-')[-1].strip()
                    
                    image_src = big_img.find('img').get('src')
                    image = requests.get(base+image_src)
                    if name not in existing_images:
                        print(f'new image found {name}')
                        with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img:
                            img.write(image.content)
                        
                    data = big_img.find_all("div")[-1].get_text()
                    info = data.split('PRICE')[0].strip('\r\n')
                    price = data.split('EUR')[-1].strip()
                    db_dict['name'].append(name)
                    db_dict['type'].append('Lamppu')
                    db_dict['color'].append(' ')
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(lighting)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info+f'. Placement: {placement}')
        else:
            print(f'Sivulle {lighting} ei päästy. Response status code {response.status_code}.\n')


        #  KNOBS
        try:
            response  = requests.get(knobs)
        except:
            print(f'Haven: Yhteys katkaistu {knobs}. Datanhaku ei onnistu.\n') 
            return   
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanel_up = soup.find(class_ = "BigImages Col4 clearfix")
            prodpanel_down = soup.find(class_ =  "BigImages Col2 clearfix")

            big_imgs1 = prodpanel_up.find_all(class_ = 'BigImage')
            big_imgs2 = prodpanel_down.find_all(class_= 'BigImage')
            if len(big_imgs1) != 4:
                print(f'Haven: Uusia tuotteita löytyi osoitteesta {knobs}. Datan parsiminen saattaa epäonnistua.')
            if len(big_imgs2) != 2:
                print(f'Haven: Uusia tuotteita löytyi osoitteesta {knobs}. Datan parsiminen saattaa epäonnistua.')
            
            big_imgs = big_imgs1 + big_imgs2
            for big_img in big_imgs:
                
                banner = big_img.find("strong").get_text()
                name = banner.split(' ')[-1]
                
                #image_src = big_img.find('img').get('src')
                #image = requests.get(base+image_src)
                #if name not in existing_images:
                #    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img:
                #        img.write(image.content)
                #    print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  

                data = big_img.find_all("div")[-1].get_text()
                colors = data.split('\n')[:2]

                colors = [col.strip('\r') for col in colors]
                colors = [col.split('⁄') for col in colors]
                final_colors = []
                for color in colors:

                    for subcolor in color:
                        if subcolor == '':
                            continue
                        final_colors.append(subcolor)

                price = data.split('EUR')[-1].strip()
                size = data.split('\n')[2]
                size = ' '.join(size.split(' ')[1:]).strip('\r')
                
                for color in final_colors:   

                    db_dict['name'].append(name)
                    db_dict['type'].append('Kahva')
                    db_dict['color'].append(color)
                    db_dict['size'].append(size)
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(knobs)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(' ')
        else:
            print(f'Sivulle {knobs} ei päästy. Response status code {response.status_code}.\n')
        #print(pd.DataFrame(db_dict).iloc[-1])

        # faucets

        try:
            response  = requests.get(faucets)
        except:
            print(f'Haven: Yhteys katkaistu {faucets}. Datanhaku ei onnistu.\n') 
            return   
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all(class_ = "BigImage")

            if len(images) != 8:
                print(f'Haven: odotetun 8:n sijasta löytyi {len(images)} tuotetta osoitteesta {faucets}. Datan parsiminen saattaa epäonnistua.\n')
            
            pop_ups = [image for image in images if 'POP-UP' in image.get_text()]
            images = [image for image in images if 'POP-UP' not in image.get_text()]

            for image in images:
                
                name = image.find("strong").get_text()           
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if name not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
                
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                info = data[0]

                colors = data[1].split('⁄')

                for color in colors:
                    if color in data[2]:
                        price = data[2].split('⁄')[0].split('EUR')[-1].strip()
                    else:
                        price = data[3].split('⁄')[0].split('EUR')[-1].strip()    
                    
                    db_dict['name'].append(name)
                    db_dict['type'].append('Hana')
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(faucets)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)
            
            colors = ['CHROME','BRASS','MATTE BLACK','COPPER']
            for i, pop_up in enumerate(pop_ups):

                name = pop_up.find(class_ = 'ForMob').get_text()           
                #image_src = pop_up.find('img').get('src')
                #img = requests.get(base+image_src)
                #if name not in existing_images:
                #    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{colors[i]}.png', 'wb') as img2:
                #        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 

                if i != 0:
                    continue
                data = pop_up.find_all("div")[-1].get_text().split('\n')
                data = [j.strip('\r') for j in data]  

                info = data[0]
                colors = data[1].split('⁄')
                for color in colors:
                    for item in data:         
                        if not 'EUR' in item:
                            continue
                        if '⁄'+color in item and 'EUR' in item:
                            price = item.split('⁄')[0].split('EUR')[-1].strip()
                            break
                        elif 'BRUSHED' in item and color == 'MATTE BLACK':
                            price = item.split('⁄')[0].split('EUR')[-1].strip()
                            break
                        else:
                            price = item.split('⁄')[0].split('EUR')[-1].strip() 

                    db_dict['name'].append(name)
                    db_dict['type'].append('Tulppa')
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(faucets)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)

        else:
            print(f'Sivulle {knobs} ei päästy. Response status code {response.status_code}.\n')
        

        # Interiors

        try:
            response  = requests.get(interiors)
        except:
            print(f'Haven: Yhteys katkaistu {interiors}. Datanhaku ei onnistu.\n') 
            return  
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanel1 = soup.find(class_ = "BigImages Col2 clearfix")
            prodpanel2 = soup.find(class_ = "BigImages Col3 clearfix")

            images1 = prodpanel1.find_all(class_ = 'BigImage')
            images2 = prodpanel2.find_all(class_ = 'BigImage')

            if len(images1+images2) != 5:
                print(f'Odotetun 5:n sijasta löytyi {len(images1+images2)} tuotetta sivulla {interiors}.\n')

            for image in images1+images2:
                
                name = image.find("strong").get_text() 
                if name == 'TOOLBOX':
                    name = 'TOOLBOX A3.21'          
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if name not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
                
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                colors = []
                colors.append(data[0].split('IN')[-1].strip())
                if 'ALSO AVAILABLE' in data[1]:
                    extra_colors = data[1].split('IN')[-1].split('AND')
                    for col in extra_colors:
                        colors.append(col.strip())
                
                price = data[-1].split('EUR')[-1].strip()

                for color in colors:  
                    
                    db_dict['name'].append(name)
                    db_dict['type'].append('Sisätila')
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(interiors)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(' ')
        else:
            print(f'Sivulle {interiors} ei päästy. Response status code {response.status_code}.\n')     

        # wall cabinet
        try:
            response  = requests.get(wall_cabinet)
        except:
            print(f'Haven: Yhteys katkaistu {wall_cabinet}. Datanhaku ei onnistu.\n') 
            return  
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanel1 = soup.find(class_ = "BigImages Col5 clearfix")
            prodpanel2 = soup.find(class_ = "BigImages Col2 clearfix")

            images1 = prodpanel1.find_all(class_ = 'BigImage')
            images2 = prodpanel2.find_all(class_ = 'BigImage')

            if len(images1+images2) != 7:
                print(f'Odotetun 7:n sijasta löytyi {len(images1+images2)} tuotetta sivulla {wall_cabinet}.\n')

            for image in images1+images2:
                
                name = image.find("strong").get_text()          
                
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                price = data[-1].split('EUR')[-1].strip()

                if image in images1:    
                    size = data[1]
                    color = data[0].split(',')[-1].strip()
                else:
                    color = data[1]
                    size = data[2]    
                    
                db_dict['name'].append(name)
                db_dict['type'].append('Seinäkaappi')
                db_dict['color'].append(color)
                db_dict['size'].append(size)
                db_dict['price'].append(price)
                db_dict['number'].append(' ')
                db_dict['url'].append(wall_cabinet)
                db_dict['company'].append('Haven')
                db_dict['info'].append(' ')
                
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if f'{name}_{color}' not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}_{color}.png".\n')  
                
        else:
            print(f'Sivulle {wall_cabinet} ei päästy. Response status code {response.status_code}.\n')       

        # high cabinet

        try:
            response  = requests.get(high_cabinet)
        except:
            print(f'Haven: Yhteys katkaistu {high_cabinet}. Datanhaku ei onnistu.\n') 
            return  
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanels1 = soup.find_all(class_ = "BigImages Col5 clearfix")
            prodpanels2 = soup.find_all(class_ = "BigImages Col2 clearfix")

            images = []
            for prodpanel in prodpanels1+prodpanels2:
                for img in prodpanel.find_all(class_ = 'BigImage'):
                    images.append(img)

            if len(images) != 14:
                print(f'Odotetun 14:n sijasta löytyi {len(images)} tuotetta sivulla {high_cabinet}.\n')

            for image in images:
                
                name = image.find("strong").get_text()          

                
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                price = data[-1].split('EUR')[-1].strip()

                if 'INCLUDING' in data[0] or 'WOOD' not in data[0]:
                    color = data[1]
                    size = data[2]
                else:
                    color = data[0].split(',')[-1].strip()   
                    size = data[1] 

                    
                db_dict['name'].append(name)
                db_dict['type'].append('Korkea kaappi')
                db_dict['color'].append(color)
                db_dict['size'].append(size)
                db_dict['price'].append(price)
                db_dict['number'].append(' ')
                db_dict['url'].append(high_cabinet)
                db_dict['company'].append('Haven')
                db_dict['info'].append(' ')
        
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if f'{name}_{color}' not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                        img2.write(img.content)
                    print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')

        else:
            print(f'Sivulle {high_cabinet} ei päästy. Response status code {response.status_code}.\n')            

        try:
            response  = requests.get(mirror_cabinet)

        except:
            print(f'Haven: Yhteys katkaistu {mirror_cabinet}. Datanhaku ei onnistu.\n') 
            return  
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanels = soup.find_all(class_ = "BigImages Col2 clearfix")
            images = []
            for prodpanel in prodpanels:
                for img in prodpanel.find_all(class_ = 'BigImage'):
                    images.append(img)

            if len(images) != 4:
                print(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {mirror_cabinet}.\n')

            for image in images:
                
                name = image.find("strong").get_text()  

                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if f'{name}' not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')

                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]

                info = data[0]

                data_tuples = []
                for item in data:
                    if 'WOOD' in item or 'WHITE' in item or 'WARM' in item:
                        colors = item.split('⁄')
                    if 'PRICE' in item:
                        model = item.split(',')[0]
                        size = item.split(',')[1]
                        price = item.split(',')[-1].split('EUR')[-1].strip()
                        data_tuples.append((name, model, size, price))

                for tupl in data_tuples:
                    for color in colors:

                        name, model, size, price = tupl
                        db_dict['name'].append(name)
                        db_dict['type'].append('Peilikaappi')
                        db_dict['color'].append(color)
                        db_dict['size'].append(size)
                        db_dict['price'].append(price)
                        db_dict['number'].append(' ')
                        db_dict['url'].append(mirror_cabinet)
                        db_dict['company'].append('Haven')
                        db_dict['info'].append(info)
        
        else:
            print(f'Sivulle {mirror_cabinet} ei päästy. Response status code {response.status_code}.\n')
        
        # Mirrors

        try:
            response  = requests.get(mirror)
        except:
            print(f'Haven: Yhteys katkaistu {mirror}. Datanhaku ei onnistu.\n') 
            return  
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prodpanel1 = soup.find_all(class_ = "BigImages Col2 clearfix")
            prodpanel2 = soup.find_all(class_ = "BigImages Col3 clearfix")
            prodpanel3 = soup.find_all(class_ = "BigImages Col4 clearfix")

            images = []

            for panel in prodpanel1 + prodpanel2 + prodpanel3:
                for img in panel.find_all(class_ = 'BigImage'):
                    images.append(img)

            if len(images) != 17:
                print(f'Odotetun 17:n sijasta löytyi {len(images)} tuotetta sivulla {mirror}.\n')

            for image in images:
                
                header = image.find("strong").get_text().split('—')  

                if len(header) == 2:
                    name, color = header
                else:
                    try:
                        name, color = header[0].split('370')
                    except:
                        name, color = header[0].split('–')        
                name.strip()
                color.strip()
                if 'FRAME' in color:
                    color = color.split('FRAME')[-1].strip()
   
                if color in ['SQUARE', 'OVAL']:
                    color = ' ' 
 
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if name not in existing_images:
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
                
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]

                price = data[-1].split('EUR')[-1].strip()
                info = data[0]
                if 'MM,' in data[1]:
                    size = data[1].split(',')[0]
                    info = info + '. ' + data[1].split('MM,')[-1]
                else:
                    size = data[1]   
   
                if name == 'M4⁄LIGHT':
                    size = ' '
                    tyyppi = 'Lamppu'
                    color = 'MATTE BLACK'
                else:
                    tyyppi = 'Peili'  

                db_dict['name'].append(name)
                db_dict['type'].append(tyyppi)
                db_dict['color'].append(color)
                db_dict['size'].append(size)
                db_dict['price'].append(price)
                db_dict['number'].append(' ')
                db_dict['url'].append(mirror)
                db_dict['company'].append('Haven')
                db_dict['info'].append(info)

        else:
                print(f'Sivulle {mirror} ei päästy. Response status code {response.status_code}.\n')
        
        # H3_1

        try:
            response  = requests.get(H3_1)
        except:
            print(f'Haven: Yhteys katkaistu {H3_1}. Datanhaku ei onnistu.\n') 
            return  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            panel = soup.find(class_ = 'Shems Col4 clearfix')
            images = panel.find_all(class_ = 'Shema')
            
            if len(images) != 4:
                print(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {H3_1}.\n')

            colors = ['WHITE', 'WARM GREY']
            for image in images:

                for color in colors:

                    name = image.find("strong").get_text().split('—')[0]   
                    if '/' in name:
                        name = name.replace('/','⁄')   
                    image_src = image.find('img').get('src')

                    if color != 'WHITE':
                        image_src = image_src.replace('White', 'Warm grey')
                    img = requests.get(base+image_src)

                    if f'{name}_{color}' not in existing_images:        
                        with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                            img2.write(img.content)
                        print(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
                    data = image.find_all("div")[-1].get_text().split('\n')
                    data = [i.strip('\r') for i in data]
                    
                    info = ' '.join(data[:2])
                    price = data[2].split('EUR')[-1].strip()

                    tyyppi = 'Lavuaari' if 'PORCE' in name else 'H3-Kaappi'

                    db_dict['name'].append(name)
                    db_dict['type'].append(tyyppi)
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H3_1)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)  

            panel = soup.find(class_ = 'BigImages Col2 clearfix')
            porcelains = panel.find_all(class_ = 'BigImage')
            if len(porcelains) != 2:
                print(f'Odotetun 2:n altaan sijasta löytyi {len(porcelains)} tuotetta sivulla {H3_1}.\n')

            for porce in porcelains:
                name = porce.find("strong").get_text()   
                data = porce.find_all("div")[-1].get_text()
                if '600, 800, 1000, AND 1400 MM' in data:
                    sizes = ['600 MM', '800 MM', '1000 MM', '1400 MM']
                else:
                    sizes = ['600 MM', '800 MM']   

                for size in sizes: 
                    duals = 'DUAL SINKS.' if size == '1400 MM' else ' '  
                    depth = '465 MM' if name == 'PORCELAIN P2⁄60—140' else '405 MM'
                    info = duals +f'Depth {depth}. THICKNESS 15 MM. PRICE INCLUDED IN H3-CABINETS. 35 MM MIXER COMPAITIBILITY'
                    price = ' '
                    db_dict['name'].append(name)
                    db_dict['type'].append('H3-Kaappi')
                    db_dict['color'].append(' ')
                    db_dict['size'].append(size)
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H3_1)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info) 

                    image_src = porce.find('img').get('src')
                    img = requests.get(base+image_src)

                    if f'{name}' not in existing_images:        
                        with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                            img2.write(img.content)
                        #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
        else:
            print(f'Sivulle {H3_1} ei päästy. Response status code {response.status_code}.\n')     

        # H3_2

        try:
            response  = requests.get(H3_2)
        except:
            print(f'Haven: Yhteys katkaistu {H3_2}. Datanhaku ei onnistu.\n') 
            return  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            panel = soup.find(class_ = 'Shems Col4 clearfix')
            images = panel.find_all(class_ = 'Shema')
            
            if len(images) != 4:
                print(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {H3_1}.\n')

            colors = ['WHITE', 'WARM GREY']
            for image in images:

                for color in colors:

                    name = image.find("strong").get_text().split('—')[0]   
                    if '/' in name:
                        name = name.replace('/','⁄')   
                    image_src = image.find('img').get('src')

                    if color != 'WHITE':
                        image_src = image_src.replace('White', 'Warm grey')
                    img = requests.get(base+image_src)

                    if f'{name}_{color}' not in existing_images:        
                        with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                            img2.write(img.content)
                        print(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
                    data = image.find_all("div")[-1].get_text().split('\n')
                    data = [i.strip('\r') for i in data]
                    
                    info = ' '.join(data[:2])
                    info = info.replace('HADLE', 'HANDLE')
                    price = data[2].split('EUR')[-1].strip()

                    tyyppi = 'Lavuaari' if 'PORCE' in name else 'H3-Kaappi'

                    db_dict['name'].append(name)
                    db_dict['type'].append(tyyppi)
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H3_2)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)  

            
        else:
            print(f'Sivulle {H3_2} ei päästy. Response status code {response.status_code}.\n') 

        

        # H2

        try:
            response  = requests.get(H2)
        except:
            print(f'Haven: Yhteys katkaistu {H2}. Datanhaku ei onnistu.\n') 
            return  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            col2 = soup.find_all(class_ = 'BigImages Col2 clearfix')[1:-1]
            col3 = soup.find_all(class_ = 'BigImages Col3 clearfix')

            images = []
            for panel in col2+col3:
                for img in panel.find_all(class_ = 'BigImage'):
                    images.append(img)

        
            if len(images) != 10:
                print(f'Odotetun 10:n sijasta löytyi {len(images)} tuotetta sivulla {H2}.\n')

            for image in images:

                name = image.find("strong").get_text().strip()   
                image_src = image.find('img').get('src')
                img = requests.get(base+image_src)
                if name not in existing_images:        
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #print(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
                
                data = image.find_all("div")[-1].get_text()
                if 'AVAILABLE IN' in data:
                    sizes = data.split('AVAILABLE IN')[-1].split('.')[0]
                    first, second = sizes.split('AND')
                    first_sizes = [i.strip() for i in first.split(',')[:-1]]
                    second_sizes = [second.strip().split(' ')[0]]
                    sizes = first_sizes + second_sizes
                    
                if 'OUR BASIN IN' in data:
                    colors = data.split('OUR BASIN IN')[-1].split('SOLID SURFACE')[0]
                    colo1, colo2 = colors.split('OR A')  
                    colo1 = [i.strip() for i in colo1.split(',')]
                    colo2 = [colo2.strip()] 
                    colors = colo1 + colo2
                else:
                    colors = [' ']
                for size in sizes:
                    for color in colors:

                        duals = 'DUAL SINKS.' if size == '1415' else ' '  
                        depth = '465 MM'
                        info = duals +f'Depth {depth}. PRICE INCLUDED IN H2-CABINETS. 35 MM MIXER COMPAITIBILITY'
                        price = ' '
                        db_dict['name'].append(name)
                        db_dict['type'].append('Lavuaari')
                        db_dict['color'].append(color)
                        db_dict['size'].append(size + ' MM')
                        db_dict['price'].append(price)
                        db_dict['number'].append(' ')
                        db_dict['url'].append(H2)
                        db_dict['company'].append('Haven')
                        db_dict['info'].append(info)


        # H2_MC

        try:
            response  = requests.get(H2_MC)
        except:
            print(f'Haven: Yhteys katkaistu {H2_MC}. Datanhaku ei onnistu.\n') 
            return  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            panels = soup.find_all(class_ = 'Shems Col4 clearfix')

            images = []
            for panel in panels:
                for img in panel.find_all(class_ = 'Shema'):
                    images.append(img)
            

            if len(images) != 8:
                print(f'Odotetun 8:n sijasta löytyi {len(images)} tuotetta sivulla {H2_MC}.\n')

            colors = ['DARK WOOD', 'LIGHT ASH WOOD', 'WHITE WOOD', 'OAK WOOD', 'WALNUT WOOD']
            for image in images:

                for color in colors:

                    name = image.find("strong").get_text().split('—')[0]  

                    #if '/' in name:
                    #    name = name.replace('/','⁄')   
                    #image_src = image.find('img').get('src')

                    data = image.find_all("div")[-1].get_text().split('\n')
                    data = [i.strip('\r') for i in data]
                    
                    info = 'H2-SERIES WITH MIRROR CABINET. '+data[0]
                    price = data[1].split('EUR')[-1].strip()
                    price = price.split(' ')[-1]

                    db_dict['name'].append(f'{name} + CABINET')
                    db_dict['type'].append('H2-Kaappi')
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H2_MC)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)  


        else:
            print(f'Sivulle {H2_MC} ei päästy. Response status code {response.status_code}.\n')
        
        #H2_M

        try:
            response  = requests.get(H2_M)
        except:
            print(f'Haven: Yhteys katkaistu {H2_M}. Datanhaku ei onnistu.\n') 
            return  
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            panels = soup.find_all(class_ = 'Shems Col4 clearfix')

            images = []
            for panel in panels:
                for img in panel.find_all(class_ = 'Shema'):
                    images.append(img)
            

            if len(images) != 8:
                print(f'Odotetun 8:n sijasta löytyi {len(images)} tuotetta sivulla {H2_M}.\n')

            colors = ['DARK WOOD', 'LIGHT ASH WOOD', 'WHITE WOOD', 'OAK WOOD', 'WALNUT WOOD']
            for image in images:

                for color in colors:

                    name = image.find("strong").get_text().split('—')[0]   
                    #if '/' in name:
                    #    name = name.replace('/','⁄')   
                    #image_src = image.find('img').get('src')

                    data = image.find_all("div")[-1].get_text().split('\n')
                    data = [i.strip('\r') for i in data]
                    
                    info = 'H2-SERIES WITH MIRROR. ' + data[0]
                    price = data[1].split('EUR')[-1].strip()
                    price = price.split(' ')[-1]

                    db_dict['name'].append(f'{name} + MIRROR')
                    db_dict['type'].append('H2-Kaappi')
                    db_dict['color'].append(color)
                    db_dict['size'].append(' ')
                    db_dict['price'].append(price)
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H2_M)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)  

            frame_panel = soup.find(class_ = 'BigImages Col3 clearfix')
            images = [img for img in frame_panel.find_all(class_ = 'BigImage')]

            if len(images) != 3:
                print(f'Odotetun 3:n sijasta löytyi {len(images)} tuotetta sivulla {H2_M}.\n')

            for i, image in enumerate(images):

                name = image.find(class_ = 'Text OtstupTextTop AlignCenter')
                name = name.find('strong').get_text().split('—')[0]   

                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]

                if i in [0,2]:
                    sizes = data[1].split('OF')[-1].split('AND')
                elif i == 1:
                    sizes = data[1].split('OF')[-1]
                    sizes1, sizes2 = sizes.split('AND')
                    sizes1= sizes1.strip().split(' ')
                    sizes1 = [siz.strip(',') for siz in sizes1]
                    sizes = sizes1+[sizes2]    
                sizes = [size.strip() for size in sizes]

                sizs = []
                for size in sizes:
                    if 'MM' in size:
                        sizs.append(size)
                    else:
                        sizs.append(size+' MM')    

                size2 = data[-1].strip('HEIGHT ')
                info = data[0]+'. '+data[-1]+'.'

                for size in sizs:

                    db_dict['name'].append(name)
                    db_dict['type'].append('Peili')
                    db_dict['color'].append(' ')
                    db_dict['size'].append(f'{size} x {size2}')
                    db_dict['price'].append(' ')
                    db_dict['number'].append(' ')
                    db_dict['url'].append(H2_M)
                    db_dict['company'].append('Haven')
                    db_dict['info'].append(info)
        else:
            print(f'Sivulle {H2_M} ei päästy. Response status code {response.status_code}.\n') 

        return pd.DataFrame(db_dict)

if __name__ == '__main__':
    Haven_scraper = HavenScraper()
    Haven_scraper.run()