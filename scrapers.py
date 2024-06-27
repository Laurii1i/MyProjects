import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import re
import time
import pandas as pd
import os
from lxml import html

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH) # Root directory of the project


def has_changed(driver, ini_text, xpath): # this function is for waiting until p-tags refresh in selenium after a click

    current = driver.find_element(By.XPATH, xpath).text
    if current == ini_text:
        return False
    
    else: return True

def read_tapwell(q):

    db_structure = ('name','type','color','price','number','url','webpage')

    db_dict = {item: [] for item in db_structure}

    s = Service(os.path.join(PATH, 'chromedriver.exe'))

    try:
        driver = webdriver.Chrome(service = s)
    except:
        q.put(('Chromedriver ei löytynyt,\nEi voida hakea dataa sivulta Tapwell\n', 'red'))  
        return None

    wait = WebDriverWait(driver, 10) # 10 sec timeout
    base = 'https://www.tapwell.fi'
    driver.get(base)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="coiPage-1"]/div[2]/button[2]')))

    except TimeoutException:
        q.put(('Hyväksy cookiet - nappia ei löytynyt\nOhitetaan etsintä\n', 'red'))
        

    try:
        hyvaksy_kaikki = driver.find_element('xpath', '//*[@id="coiPage-1"]/div[2]/button[2]')
        hyvaksy_kaikki.click()

    except:
        pass    

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/section[2]/div')))
    except TimeoutException:
        q.put(('Etusivun paneelia ei löytynyt,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
        driver.quit()
        return None

    main_panel = driver.find_element('xpath', '//*[@id="app"]/main/section[2]/div')
    main_buts = main_panel.find_elements(By.TAG_NAME, 'a')
    main_buts = [but for but in main_buts if but.is_displayed()]

    if main_buts == []:
        q.put(('Etusivun nappeja ei löytynyt,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
        driver.quit()
        return None

    if len(main_buts) != 4:
        q.put((f'Etusivun nappeja löytyi {len(main_buts)} odotetun 4:n sijasta,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
        driver.quit()
        return None

    main_hrefs = [but.get_attribute('href') for but in main_buts]

    if None in main_hrefs:
        q.put(('href - referenssi ei löytynyt kaikista etusivun napeista,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
        driver.quit()
        return None

    types = ('Suihku', 'Kylpyhuonehana', 'Keittiöhana', 'Pyyhekuivain')
    main_hrefs = zip(main_hrefs,types)
    products = []

    try:
        actions = ActionChains(driver)
    except:
        q.put(('ActionChains(driver) ei onnistunut\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))    
        driver.quit()
        return None  

    for href, tyyppi in main_hrefs:

        main_panel = driver.find_element('xpath', '//*[@id="app"]/main/section[2]/div')
        main_buts = main_panel.find_elements(By.TAG_NAME, 'a')
        main_buts = [but for but in main_buts if but.is_displayed()]

        for but in main_buts:
            if href == but.get_attribute('href'):
                actions.move_to_element(but).perform()
                but.click()
                q.put(f'Etsitään tuotteita: {tyyppi}\n')
                break
        
        try: # Wait until tuotesivun paneeli (joka sisältää kaikki tuotteet on latautunut)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/div[3]/div')))
        except TimeoutException:
            q.put(('Tuotesivun tuotepaneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))  
            driver.quit()
            return None 

        try: # odota kunnes värivaihtoehtopaneeli on latautunut
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul')))
        except TimeoutException:
            q.put(('Tuotesivun värivaihtoehdot-paneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red')) 
            driver.quit()
            return None

        color_but_panel = driver.find_element('xpath','//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul') # paneeli, josta löytyy värinapit
    

        product_buts = []
        i = 1
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # scrollaa sivun pohjalle, jotta kaikki tuotteet latautuu oikein
        except:
            q.put(('Ei voitu siirtyä sivun pohjalle.\nDatahaku sivustolta Tapwell keskeytyy.\n', 'red')) 
            driver.quit()
            return None 

        time.sleep(2)
        while True:
            xpath = f'//*[@id="app"]/main/div/div/div[3]/div/div[{i}]/div/a'
            try:
                product_buts.append((driver.find_element('xpath', xpath)))
                i = i+1
            except: 
                q.put(f'{i-1} eri tuotenimeä löytyi.\n')
                break    

        for BUT in product_buts:

            actions.move_to_element(BUT).perform()
            try:
                BUT.click()
            except:
                time.sleep(0.5)
                BUT.click()   

            try:     
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul')))
            except TimeoutException:
                q.put(('Värivaihtoehdot-paneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
                driver.quit() 
                return None   

            color_buts = color_but_panel.find_elements(By.TAG_NAME, 'li')

            for but in color_buts:

                actions.move_to_element(but).perform()

                prod_num_xpath = '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/p[1]'
                ini_text = driver.find_element(By.XPATH, prod_num_xpath).text
                try:
                    but.click()
                    # wait until new data has loaded
                    wait.until(lambda driver: has_changed(driver, ini_text, prod_num_xpath))
                    # wait a litle bit more to ensure that every piece of data has changed
                    time.sleep(0.02)
                except:
                    pass

                try: # Data variable contains the panel, which contains prod number, color, price information
                    data = driver.find_element('xpath', '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]')
                except:
                    q.put((f'Tuotteen tietoja ei löytynyt sivulta\n{driver.current_url}\nDatahaku keskeytyy sivustolta Tapwell\n', 'red')) 
                    driver.quit()
                    return None

                datas = data.find_elements(By.TAG_NAME, 'p')
                # datas = [product_number, , price]

                try: # name and color are found from here
                    prod_and_col = driver.find_element('xpath', '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/h1').text
                except:
                    q.put((f'Tuotenumeroa ja väriä ei löytynyt sivulta\n{driver.current_url}\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
                    driver.quit()
                    return None   

                splitted = prod_and_col.split()
                product_name = splitted[0]
                color = ' '.join(splitted[1:])
                tuotenum, price = datas[0].text, datas[-1].text
                product_number = tuotenum.split()[-1]
                price = re.sub(r'[^\d.,]', '', price) # Remove everything else but numbers, dots and commas
                url = driver.current_url

                db_dict['name'].append(product_name)
                db_dict['type'].append(tyyppi)
                db_dict['color'].append(color)
                db_dict['price'].append(price)
                db_dict['number'].append(product_number)
                db_dict['url'].append(url)
                db_dict['webpage'].append('Tapwell')

                '''figure = driver.find_element('xpath','//*[@id="app"]/main/div/div/div[1]/div[2]/img')
                fig_src = figure.get_attribute('src')
                figure = requests.get(fig_src)

                with open(f'C:/Users/lauri/Documents/tap_project2/Figures/Tapwell/{product_number}.png', 'wb') as f:
                    f.write(figure.content)'''


                time.sleep(0.1)

        driver.get(base) # go back to frontpage  
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/section[2]/div')))

    new_data = pd.DataFrame(db_dict)
    #new_data.to_csv('C:/Users/lauri/Documents/tap_project2/database2', index = False)
    driver.quit()
    return new_data  

def read_haven(q):

    base = 'https://haven-system.com'

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

    db_structure = ('name','type','color', 'size', 'price','number','url','webpage', 'info')

    db_dict = {item: [] for item in db_structure}


    '''response  = requests.get(lighting)
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prodpanel1 = soup.find(class_ = "BigImages Col2 clearfix")
        prodpanel2 = soup.find(class_ = "BigImages Col3 clearfix")

        prodpanel3 = soup.find(class_ = "BigImages Col4 clearfix")
        if prodpanel3 is not None:
            q.put(f'Haven: Uusi tuotepaneeli löytynyt osoitteessa {lighting}. Tämän paneelin tuotteita ei lisätä tietokantaan.\n')

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
                db_dict['color'].append('')
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(lighting)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info+f'. Placement: {placement}')
    else:
        q.put(f'Sivulle {lighting} ei päästy. Response status code {response.status_code}.\n')


    #  KNOBS
    try:
        response  = requests.get(knobs)
    except:
        q.put(f'Haven: Yhteys katkaistu {knobs}. Datanhaku ei onnistu.\n') 
        return   
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prodpanel_up = soup.find(class_ = "BigImages Col4 clearfix")
        prodpanel_down = soup.find(class_ =  "BigImages Col2 clearfix")

        big_imgs1 = prodpanel_up.find_all(class_ = 'BigImage')
        big_imgs2 = prodpanel_down.find_all(class_= 'BigImage')
        if len(big_imgs1) != 4:
            q.put(f'Haven: Uusia tuotteita löytyi osoitteesta {knobs}. Datan parsiminen saattaa epäonnistua.')
        if len(big_imgs2) != 2:
            q.put(f'Haven: Uusia tuotteita löytyi osoitteesta {knobs}. Datan parsiminen saattaa epäonnistua.')
        
        big_imgs = big_imgs1 + big_imgs2
        for big_img in big_imgs:
            
            banner = big_img.find("strong").get_text()
            name = banner.split(' ')[-1]
            
            image_src = big_img.find('img').get('src')
            image = requests.get(base+image_src)
            if name not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img:
                    img.write(image.content)
                q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  

            data = big_img.find_all("div")[-1].get_text()
            size = data.split('PRICE')[0].strip('\n').strip('\r')
            colors = info.split('\n')[:2]
            colors = [col.strip('\r') for col in colors]
            colors = [col.split('/') for col in colors]
            final_colors = []
            for color in colors:
                col = color[0]
                try:
                    first, second = col.split('⁄')[:2]
                    final_colors.append(first)
                    final_colors.append(second)
                except:
                    final_colors.append(col)

            price = data.split('EUR')[-1].strip()
            size = info.split('\n')[2]
            
            for color in final_colors:   
                
                db_dict['name'].append(name)
                db_dict['type'].append('Kahva')
                db_dict['color'].append(color)
                db_dict['size'].append(size)
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(knobs)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append('')
    else:
        q.put(f'Sivulle {knobs} ei päästy. Response status code {response.status_code}.\n')
    print(pd.DataFrame(db_dict).iloc[-1])

    # faucets

    try:
        response  = requests.get(faucets)
    except:
        q.put(f'Haven: Yhteys katkaistu {faucets}. Datanhaku ei onnistu.\n') 
        return   
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all(class_ = "BigImage")

        if len(images) != 8:
            q.put(f'Haven: odotetun 8:n sijasta löytyi {len(images)} tuotetta osoitteesta {faucets}. Datan parsiminen saattaa epäonnistua.\n')
        
        pop_ups = [image for image in images if 'POP-UP' in image.get_text()]
        images = [image for image in images if 'POP-UP' not in image.get_text()]

        for image in images:
            
            name = image.find("strong").get_text()           
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if name not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
            
            data = image.find_all("div")[-1].get_text().split('\n')
            data = [i.strip('\r') for i in data]
            
            info = data[0]
            colors = data[1].split('⁄')

            for color in colors:
                if color in info[2]:
                    price = info[2].split('⁄')[0].split('EUR')[-1].strip()
                else:
                    price = info[3].split('⁄')[0].split('EUR')[-1].strip()    
                
                db_dict['name'].append(name)
                db_dict['type'].append('Hana')
                db_dict['color'].append(color)
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(faucets)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)
        
        colors = ['CHROME','BRASS','MATTE BLACK','COPPER']
        for i, pop_up in enumerate(pop_ups):

            name = pop_up.find(class_ = 'ForMob').get_text()           
            #image_src = pop_up.find('img').get('src')
            #img = requests.get(base+image_src)
            #if name not in existing_images:
            #    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{colors[i]}.png', 'wb') as img2:
            #        img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 

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
                db_dict['placement'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(faucets)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)

    else:
        q.put(f'Sivulle {knobs} ei päästy. Response status code {response.status_code}.\n')
    

    # Interiors

    try:
        response  = requests.get(interiors)
    except:
        q.put(f'Haven: Yhteys katkaistu {interiors}. Datanhaku ei onnistu.\n') 
        return  
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prodpanel1 = soup.find(class_ = "BigImages Col2 clearfix")
        prodpanel2 = soup.find(class_ = "BigImages Col3 clearfix")

        images1 = prodpanel1.find_all(class_ = 'BigImage')
        images2 = prodpanel2.find_all(class_ = 'BigImage')

        if len(images1+images2) != 5:
            q.put(f'Odotetun 5:n sijasta löytyi {len(images1+images2)} tuotetta sivulla {interiors}.\n')

        for image in images1+images2:
            
            name = image.find("strong").get_text() 
            if name == 'TOOLBOX':
                name = 'TOOLBOX A3.21'          
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if name not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
            
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
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(interiors)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append('')
    else:
        q.put(f'Sivulle {interiors} ei päästy. Response status code {response.status_code}.\n')     

     # wall cabinet
    try:
        response  = requests.get(wall_cabinet)
    except:
        q.put(f'Haven: Yhteys katkaistu {wall_cabinet}. Datanhaku ei onnistu.\n') 
        return  
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prodpanel1 = soup.find(class_ = "BigImages Col5 clearfix")
        prodpanel2 = soup.find(class_ = "BigImages Col2 clearfix")

        images1 = prodpanel1.find_all(class_ = 'BigImage')
        images2 = prodpanel2.find_all(class_ = 'BigImage')

        if len(images1+images2) != 7:
            q.put(f'Odotetun 7:n sijasta löytyi {len(images1+images2)} tuotetta sivulla {wall_cabinet}.\n')

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
            db_dict['number'].append('')
            db_dict['url'].append(wall_cabinet)
            db_dict['webpage'].append('Haven')
            db_dict['info'].append('')
            
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if f'{name}_{color}' not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}_{color}.png".\n')  
            
    else:
        q.put(f'Sivulle {wall_cabinet} ei päästy. Response status code {response.status_code}.\n')       

    # high cabinet

    try:
        response  = requests.get(high_cabinet)
    except:
        q.put(f'Haven: Yhteys katkaistu {high_cabinet}. Datanhaku ei onnistu.\n') 
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
            q.put(f'Odotetun 14:n sijasta löytyi {len(images)} tuotetta sivulla {high_cabinet}.\n')

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
            db_dict['number'].append('')
            db_dict['url'].append(high_cabinet)
            db_dict['webpage'].append('Haven')
            db_dict['info'].append('')
    
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if f'{name}_{color}' not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}_{color}.png', 'wb') as img2:
                    img2.write(img.content)
                q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')

    else:
        q.put(f'Sivulle {high_cabinet} ei päästy. Response status code {response.status_code}.\n')            

    try:
        response  = requests.get(mirror_cabinet)
    except:
        q.put(f'Haven: Yhteys katkaistu {mirror_cabinet}. Datanhaku ei onnistu.\n') 
        return  
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prodpanels = soup.find_all(class_ = "BigImages Col2 clearfix")
        images = []
        for prodpanel in prodpanels:
            for img in prodpanel.find_all(class_ = 'BigImage'):
                images.append(img)

        if len(images) != 4:
            q.put(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {mirror_cabinet}.\n')

        for image in images:
            
            name = image.find("strong").get_text()  

            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if f'{name}' not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')

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
                    db_dict['number'].append('')
                    db_dict['url'].append(mirror_cabinet)
                    db_dict['webpage'].append('Haven')
                    db_dict['info'].append(info)
    
    else:
        q.put(f'Sivulle {mirror_cabinet} ei päästy. Response status code {response.status_code}.\n')
    
    # Mirrors

    try:
        response  = requests.get(mirror)
    except:
        q.put(f'Haven: Yhteys katkaistu {mirror}. Datanhaku ei onnistu.\n') 
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
            q.put(f'Odotetun 17:n sijasta löytyi {len(images)} tuotetta sivulla {mirror}.\n')

        for image in images:
            
            name = image.find("strong").get_text()        
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if name not in existing_images:
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n')  
            
            data = image.find_all("div")[-1].get_text().split('\n')
            data = [i.strip('\r') for i in data]

            price = data[-1].split('EUR')[-1].strip()
            info = data[0]
            if 'MM,' in data[1]:
                size = data[1].split(',')[0]
                info = info + '. ' + data[1].split('MM,')[-1]
            else:
                size = data[1]   

                
            db_dict['name'].append(name)
            db_dict['type'].append('Peili')
            db_dict['color'].append('')
            db_dict['size'].append(size)
            db_dict['price'].append(price)
            db_dict['number'].append('')
            db_dict['url'].append(mirror)
            db_dict['webpage'].append('Haven')
            db_dict['info'].append(info)

    else:
            q.put(f'Sivulle {mirror} ei päästy. Response status code {response.status_code}.\n')
    
    # H3_1

    try:
        response  = requests.get(H3_1)
    except:
        q.put(f'Haven: Yhteys katkaistu {H3_1}. Datanhaku ei onnistu.\n') 
        return  
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        panel = soup.find(class_ = 'Shems Col4 clearfix')
        images = panel.find_all(class_ = 'Shema')
        
        if len(images) != 4:
            q.put(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {H3_1}.\n')

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
                    q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                info = ' '.join(data[:2])
                price = data[2].split('EUR')[-1].strip()

                db_dict['name'].append(name)
                db_dict['type'].append('H3-Kaappi')
                db_dict['color'].append(color)
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(H3_1)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)  

        panel = soup.find(class_ = 'BigImages Col2 clearfix')
        porcelains = panel.find_all(class_ = 'BigImage')
        if len(porcelains) != 2:
            q.put(f'Odotetun 2:n altaan sijasta löytyi {len(porcelains)} tuotetta sivulla {H3_1}.\n')

        for porce in porcelains:
            name = porce.find("strong").get_text()   
            data = porce.find_all("div")[-1].get_text()
            if '600, 800, 1000, AND 1400 MM' in data:
                sizes = ['600 MM', '800 MM', '1000 MM', '1400 MM']
            else:
                sizes = ['600 MM', '800 MM']   

            for size in sizes: 
                duals = 'DUAL SINKS.' if size == '1400 MM' else ''  
                depth = '465 MM' if name == 'PORCELAIN P2⁄60—140' else '405 MM'
                info = duals +f'Depth {depth}. THICKNESS 15 MM. PRICE INCLUDED IN H3-CABINETS. 35 MM MIXER COMPAITIBILITY'
                price = ''
                db_dict['name'].append(name)
                db_dict['type'].append('H3-Kaappi')
                db_dict['color'].append('')
                db_dict['size'].append(size)
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(H3_1)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info) 

                image_src = porce.find('img').get('src')
                img = requests.get(base+image_src)

                if f'{name}' not in existing_images:        
                    with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                        img2.write(img.content)
                    #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
    else:
        q.put(f'Sivulle {H3_1} ei päästy. Response status code {response.status_code}.\n')     

    # H3_2

    try:
        response  = requests.get(H3_2)
    except:
        q.put(f'Haven: Yhteys katkaistu {H3_2}. Datanhaku ei onnistu.\n') 
        return  
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        panel = soup.find(class_ = 'Shems Col4 clearfix')
        images = panel.find_all(class_ = 'Shema')
        
        if len(images) != 4:
            q.put(f'Odotetun 4:n sijasta löytyi {len(images)} tuotetta sivulla {H3_1}.\n')

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
                    q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                info = ' '.join(data[:2])
                price = data[2].split('EUR')[-1].strip()

                db_dict['name'].append(name)
                db_dict['type'].append('H3-Kaappi')
                db_dict['color'].append(color)
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(H3_2)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)  

         
    else:
        q.put(f'Sivulle {H3_2} ei päästy. Response status code {response.status_code}.\n') 

    

    # H2

    try:
        response  = requests.get(H2)
    except:
        q.put(f'Haven: Yhteys katkaistu {H2}. Datanhaku ei onnistu.\n') 
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
            q.put(f'Odotetun 10:n sijasta löytyi {len(images)} tuotetta sivulla {H2}.\n')

        for image in images:

            name = image.find("strong").get_text().strip()   
            image_src = image.find('img').get('src')
            img = requests.get(base+image_src)
            if name not in existing_images:        
                with open(f'C:/Users/lauri/Documents/tap_project3/Figures/Haven/{name}.png', 'wb') as img2:
                    img2.write(img.content)
                #q.put(f'Haven: Uusi kuva ladattiin "{name}.png".\n') 
            
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
                colors = ['']
            for size in sizes:
                for color in colors:

                    duals = 'DUAL SINKS.' if size == '1415' else ''  
                    depth = '465 MM'
                    info = duals +f'Depth {depth}. PRICE INCLUDED IN H2-CABINETS. 35 MM MIXER COMPAITIBILITY'
                    price = ''
                    db_dict['name'].append(name)
                    db_dict['type'].append('H2-Kaappi')
                    db_dict['color'].append(color)
                    db_dict['size'].append(size + ' MM')
                    db_dict['price'].append(price)
                    db_dict['number'].append('')
                    db_dict['url'].append(H2)
                    db_dict['webpage'].append('Haven')
                    db_dict['info'].append(info)


    # H2_MC

    try:
        response  = requests.get(H2_MC)
    except:
        q.put(f'Haven: Yhteys katkaistu {H2_MC}. Datanhaku ei onnistu.\n') 
        return  
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        panels = soup.find_all(class_ = 'Shems Col4 clearfix')

        images = []
        for panel in panels:
            for img in panel.find_all(class_ = 'Shema'):
                images.append(img)
        

        if len(images) != 8:
            q.put(f'Odotetun 8:n sijasta löytyi {len(images)} tuotetta sivulla {H2_MC}.\n')

        colors = ['DARK WOOD', 'LIGHT ASH WOOD', 'WHITE WOOD', 'OAK WOOD', 'WALNUT WOOD']
        for image in images:

            for color in colors:

                name = image.find("strong").get_text().split('—')[0]   
                #if '/' in name:
                #    name = name.replace('/','⁄')   
                #image_src = image.find('img').get('src')

                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                info = data[0]
                price = data[1].split('EUR')[-1].strip()
                price = price.split(' ')[-1]

                db_dict['name'].append(name)
                db_dict['type'].append('H3-Kaappi')
                db_dict['color'].append(color)
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(H2_MC)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)  


    else:
        q.put(f'Sivulle {H2_MC} ei päästy. Response status code {response.status_code}.\n') '''  
    
    #H2_M

    try:
        response  = requests.get(H2_M)
    except:
        q.put(f'Haven: Yhteys katkaistu {H2_M}. Datanhaku ei onnistu.\n') 
        return  
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        panels = soup.find_all(class_ = 'Shems Col4 clearfix')

        images = []
        for panel in panels:
            for img in panel.find_all(class_ = 'Shema'):
                images.append(img)
        

        if len(images) != 8:
            q.put(f'Odotetun 8:n sijasta löytyi {len(images)} tuotetta sivulla {H2_M}.\n')

        colors = ['DARK WOOD', 'LIGHT ASH WOOD', 'WHITE WOOD', 'OAK WOOD', 'WALNUT WOOD']
        for image in images:

            for color in colors:

                name = image.find("strong").get_text().split('—')[0]   
                #if '/' in name:
                #    name = name.replace('/','⁄')   
                #image_src = image.find('img').get('src')

                data = image.find_all("div")[-1].get_text().split('\n')
                data = [i.strip('\r') for i in data]
                
                info = data[0]
                price = data[1].split('EUR')[-1].strip()
                price = price.split(' ')[-1]

                db_dict['name'].append(name)
                db_dict['type'].append('H3-Kaappi')
                db_dict['color'].append(color)
                db_dict['size'].append('')
                db_dict['price'].append(price)
                db_dict['number'].append('')
                db_dict['url'].append(H2_M)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)  

        frame_panel = soup.find(class_ = 'BigImages Col3 clearfix')
        images = [img for img in frame_panel.find_all(class_ = 'BigImage')]

        if len(images) != 3:
            q.put(f'Odotetun 3:n sijasta löytyi {len(images)} tuotetta sivulla {H2_M}.\n')

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
                db_dict['color'].append('')
                db_dict['size'].append(f'{size} x {size2}')
                db_dict['price'].append('')
                db_dict['number'].append('')
                db_dict['url'].append(H2_M)
                db_dict['webpage'].append('Haven')
                db_dict['info'].append(info)
    else:
        q.put(f'Sivulle {H2_M} ei päästy. Response status code {response.status_code}.\n') 

    print(pd.DataFrame(db_dict).iloc[-2])
read_haven('q')

def check_updates(new_data, q):

    need_for_update = False
    db_loc = os.path.join(PATH, 'database.csv')
    old_data = pd.read_csv(db_loc, dtype = str)

    # first let's check if all of the new product numbers are found in the database

    pn_new = set(new_data['number'])
    pn_old = set(old_data['number'])
    new_ids = []
    for id in pn_new:
        if id not in pn_old:
            new_ids.append(id)
    new_products = new_data[new_data['number'].isin(new_ids)]
    if not new_products.empty:
        q.put(('Uusia tuotteita löytynyt:\n', 'green'))
        for _, row in new_products.iterrows():
            q.put(f"{row['name']} {row['color']}\n")
        need_for_update = True
    else:
        q.put(('Uusia tuotteita ei löytynyt.\n', 'green'))    

    # Next check If some old products have been removed.

    webpages = set(new_data['webpage'])

    for page in webpages:
        
        old_parsed = old_data[old_data['webpage'] == page]

        pn_old = set(old_parsed['number'])

        old_ids = []
        for id in pn_old:
            if id not in pn_new:
                old_ids.append(id)

        old_products = old_data[old_data['number'].isin(old_ids)]

        if not old_products.empty:
            q.put(('Vanhoja tuotteita poistunut sivustolta:\n', 'green'))
            for _, row in old_products.iterrows():
                q.put(f"{row['name']} {row['color']}\n")
            need_for_update = True
        else:
            q.put((f'Vanhoja tuotteita ei poistunut sivustolta Tapwell.\n', 'green')) 

    # Next search for possible price changes

    for _, row in new_data.iterrows():
        prod_num = row['number']
        try:
            old = old_data[old_data['number'] == prod_num]
            old_price, new_price = old['price'], row['price']
            if old_price != new_price:
                q.put((f'Tuotteen {prod_num} hinta on muuttunut {old_price} -> {new_price}', 'green'))
                need_for_update = True
        except:
            pass    
    else:
        q.put(('Tuotteiden hinnanmuutoksia ei löytynyt', 'green'))     
    return need_for_update

def overwrite_database(new_data):
    new_data.to_csv(os.path.join(PATH, 'database.csv'), index = False)

def update_database(new_data):

    db_loc = os.path.join(PATH, 'database.csv')
    old_data = pd.read_csv(db_loc)

    combined = pd.concat([new_data, old_data])

# Remove duplicates based on all columns
    combined = combined.drop_duplicates()

    combined.to_csv(os.path.join(PATH, 'database.csv'), index = False)

def update_everything(q):

    q.put(('Haetaan dataa sivustolta: Tapwell\n', 'blue'))

    dataframe_tapwell = read_tapwell(q)

    if dataframe_tapwell is None:
        q.put('Tapwellin tietokantaa ei pystytty päivittämään', 'red')
        return

    q.put(('Tuotteet haettu onnistuneesti sivustolta Tapwell\n', 'green'))
    check_updates(dataframe_tapwell, q)    
    overwrite_database(dataframe_tapwell)

def DL_haven_H2_imgs():

    s = Service('C:/Users/lauri/Documents/tap_project3/chromedriver.exe')
    driver = webdriver.Chrome(service = s)
    base1 = 'https://haven-system.com/catalogue/H2/oval/'
    base2 = 'https://haven-system.com/catalogue/H2/spegelskap/'
    driver.get(base1)
    actions = ActionChains(driver)


    first_panel = driver.find_element('xpath', '//*[@id="nc-block-75433bbd7e6067b816a33731d83f4624"]/div[2]')
    second_panel = driver.find_element('xpath' ,'//*[@id="nc-block-ce500dc82f11b6c876bb58f367c6efc2"]/div[2]')

    buts1paths = [f'//*[@id="nc-block-75433bbd7e6067b816a33731d83f4624"]/div[2]/span[4]/b[{i}]/span' for i in range(1,6)]
    buts2paths = [f'//*[@id="nc-block-ce500dc82f11b6c876bb58f367c6efc2"]/div[2]/span[4]/b[{i}]/span' for i in range(1,6)]

    # base2 xpaths
    # buts1paths = [f'//*[@id="nc-block-175bd2726c9da9deb4a4078e946f0990"]/div[2]/span[4]/b[{i}]/span' for i in range(1,6)]
    # buts2paths = [f'//*[@id="nc-block-01ae2e11799ffacd74ff4195ab431a93"]/div[2]/span[4]/b[{i}]/span' for i in range(1,6)]

    for xpath in buts1paths:
        but = driver.find_element('xpath', xpath)
        actions.move_to_element(but).perform()
        but.click()
        time.sleep(0.5)

        images1 = first_panel.find_elements(By.CLASS_NAME, 'Shema')
        names1 = [i.find_element(By.TAG_NAME, 'strong') for i in images1]
        images1 = [i.find_element(By.TAG_NAME, 'img') for i in images1]

        stuff1 = zip(names1, images1)
        
        for name, image in stuff1:

            nam, col = name.text.split('—')
            img_src = image.get_attribute('src')
            img = requests.get(img_src)

            with open(f'C:/Users/lauri/Documents/tap_project3/Figures/{nam}+MIRROR+STONE-TOP_{col}.png', 'wb') as f:
                f.write(img.content)

    for xpath in buts2paths:
        but = driver.find_element('xpath', xpath)
        actions.move_to_element(but).perform()
        but.click()
        time.sleep(0.5)

        images2 = second_panel.find_elements(By.CLASS_NAME, 'Shema')
        names2 = [i.find_element(By.TAG_NAME, 'strong') for i in images2]
        images2 = [i.find_element(By.TAG_NAME, 'img') for i in images2]

        stuff2 = zip(names2, images2)
        
        for name, image in stuff2:

            nam, col = name.text.split('—')
            img_src = image.get_attribute('src')
            img = requests.get(img_src)

            with open(f'C:/Users/lauri/Documents/tap_project3/Figures/{nam}+MIRROR+PORCELAIN_{col}.png', 'wb') as f:
                f.write(img.content)
    