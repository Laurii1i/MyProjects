import re
import time
import pandas as pd
import os
from bs4 import BeautifulSoup
from CommonScraper import CommonScraper
import requests 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time


PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)
PATH = os.path.join(PATH, '..')

class INRScraper(CommonScraper):

    def __init__(self):

        super().__init__()
        self.company_name = 'INR'
        self.website_url = 'https://www.inr.fi/'
        self.chromedriver = os.path.join(PATH, 'Scrapers', 'chromedriver.exe')

        s = Service(self.chromedriver)

        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(service = s, options=chrome_options)            
        self.wait = WebDriverWait(self.driver, 10) # 10 sec timeout
        self.actions = ActionChains(self.driver)

    def scrape_cabinets(self):

        db_structure = ('name','type','color', 'size', 'price','url','webpage', 'info')
        db_dict = {item: [] for item in db_structure}

        kaappi = 'https://www.inr.fi/tuotteet/kylpyhuonesailytys/'

        response  = requests.get(kaappi)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            main = soup.find(class_ = 'container-fluid product-filter-result')
            main_panel = main.find(class_ = "row")
            products = main_panel.find_all(class_ = "col-sm-6 col-md-4 col-lg-4 col-xl-3 col-xxl-2")

            if len(products) != 25:
                print(f'{len(products)} products were found instead of expected 25.')


            products_hrefs = [product.find('a').get('href') for product in products if 'tuotteet' in product.find('a').get('href')]

            
            description_panel_xpaths = ['/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]',
                                        '/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[1]']
            for href in products_hrefs:

                print(href)
                self.driver.get(f'{self.website_url}{href}') 

                time.sleep(2)

                try:
                    accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
                    accept_cookies.click()
                except:
                    pass

                for desc_xpath in description_panel_xpaths:
                    try:
                        self.wait.until(EC.presence_of_element_located((By.XPATH, desc_xpath)))
                    except:
                        pass    

                try:
                    name = self.driver.find_element(By.XPATH, '//*[@id="ec-text-wrapper-inner-slideshow-h2"]').text
                except:
                    name = ' '.join(href.split('/')[-1].split('-')[2:])

                try:
                    typpe = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/h4').text
                except:
                    typpe = 'Korkeakaappi'    

                try:    
                    info = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/p').text
                except:
                    info = ''    

                if not self.product_figure_exists(name = name):
                    print(f'Downloading image for {name}.')
                    self.download_image(xpath = '/html/body/div[2]/div[1]/div/div/div/div[1]/div[1]/picture/img', save_name = name)

                try:
                    size_info = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/span')
                    self.actions.move_to_element(size_info).perform()

                    sizes = size_info.text.split('mm')
                    sizes = [self.remove_non_numbers(size) for size in sizes]
                    try:
                        sizes.remove('')
                    except:
                        pass   
                    
                    size_info = ' x '.join(sizes)+' mm'

                except:
                    size_info = ''  

            
                #iframes_before = len(self.driver.find_elements(By.TAG_NAME, 'iframe'))

                muokkaa_xpaths = ['/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[4]/div/a', '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[5]/div/a', '/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div[5]/div/a']
                
                for xpath in muokkaa_xpaths:

                    try:
                        muokkaa = self.driver.find_element(By.XPATH, xpath)
                    except:
                        pass    
                  

                try:
                    muokkaa.click()

                except:
                    self.actions.move_to_element(muokkaa).perform() 
                    muokkaa.click() 

                new_iframe = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/iframe[1]')))

                #iframes_after = len(self.driver.find_elements(By.TAG_NAME, 'iframe'))

                self.driver.switch_to.frame(new_iframe)
                
                options = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[1]/div/div/div/div[2]/div[3]')))
                options.click()

                color_options = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]')))
                color_options.click()

                #accent_but = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "ACCENT")]')))
                #accent_but.click()
                
                main_color_panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div')))
                time.sleep(0.1)
                
                main_cols = main_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')

                main_cols_text = [main_col.text for main_col in main_cols]
            
                if 'ACCENT / NCS' in main_cols_text:
                    accent_but = main_cols.pop()

                    main_cols_text = [main_col.text for main_col in main_cols]
                    self.wait.until(EC.element_to_be_clickable(accent_but))
                    accent_but.click()
                    accent_color_panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div[2]/div')))
                    accent_cols = accent_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')
                else:
                    accent_but = None
                    accent_cols = []

                colors = [color.text for color in accent_cols + main_cols]

                for col in accent_cols + main_cols:
                    
                    self.wait.until(EC.element_to_be_clickable(col))

                    try:
                        col.click()
                    except:
                        self.driver.execute_script("""
                        arguments[0].scrollIntoView({
                            behavior: 'smooth',
                            block: 'end'
                        });
                    """, col)
                        time.sleep(1)
                        col.click()

                    time.sleep(0.5)
                    price_label = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]')))

                    price = self.remove_non_numbers(price_label.text)
                    color = col.text
                    
                    db_dict['color'].append(color)
                    db_dict['price'].append(price)
                    db_dict['size'].append(size_info)
                    db_dict['name'].append(name)
                    db_dict['type'].append(typpe)
                    db_dict['url'].append(f'{self.website_url}{href}')
                    db_dict['webpage'].append('INR')
                    db_dict['info'].append(info)
                #print(db_dict)  
                #  
        return pd.DataFrame(db_dict)


    def scrape_mirrors(self):

        page = 'https://www.inr.fi/tuotteet/peili-ja-peilikaapit/'

        db_structure = ('name','type','color', 'size', 'price','url','webpage', 'info')
        db_dict = {item: [] for item in db_structure}

        response  = requests.get(page)

        if response.status_code == 200:

            #self.driver.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')

            main = soup.find(class_ = 'container-fluid product-filter-result')
            main_panel = main.find(class_ = "row")
            products = main_panel.find_all(class_ = "col-sm-6 col-md-4 col-lg-4 col-xl-3 col-xxl-2")
            
            mirrors = []
            mirror_cabinets = []

            for product in products:

                try:

                    name = product.find('h3').get_text(strip = True)
                    if len(name) > 25:
                        continue

                    category = product.find(class_ = "category-heading").get_text(strip = True)
                    href = product.find('a').get('href')

                    img_src = product.find('img').get('src')

                    if not self.product_figure_exists(name = name):
                        self.download_image(save_name = name, img_src = img_src)

                    if 'Peilikaappi' in category:
                        mirror_cabinets.append((name, category, 'https://www.inr.fi' + href))
                    elif 'Peili' in category:

                        mirrors.append((name, category, 'https://www.inr.fi' + href))
                except:
                    pass
 
            for mirror in mirrors:

                name, category, href = mirror

                self.driver.get(href)

                info = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/').text

                size = self.driver.find_element(By.XPATH, '//*[@id="model-section1"]/div/div[1]/span').text

                if 'L:' in size and 'S:' in size:

                    if not '/' in size:

                        sizes = size.text.split('mm')
                        sizes = [self.remove_non_numbers(size) for size in sizes]
                        try:
                            sizes.remove('')
                        except:
                            pass   
                        
                        final_sizes_formatted = [' x '.join(sizes)+' mm']

                    else:
                        'L: 600 mm, K: 720 mm, S: 30/70 mm'

                        sizes = size.text.split(' ')
                        sizes.remove('L:')
                        sizes.remove('K:')
                        sizes.remove('S:')
                        sizes.remove('mm,')
                        sizes.remove('mm')
                        try:
                            sizes.remove('')
                        except:
                            pass

                        indices = []
                        numb = 0
                        for i, size in enumerate(sizes):

                            if '/' in size:
                                indices.append(i)

                            numb = len(size.split('/'))-1

                        final_sizes = []
                        for i in range(numb):

                            size_attempt = []

                            for size in sizes:
                                if '/' not in size:
                                    size_attempt.append(size)
                                else:
                                    size_attempt.append(size.split('/')[numb])

                            final_sizes.append(size_attempt)

                        final_sizes_formatted = []
                        for size in final_sizes:
                            a,b,c = size
                            final_sizes_formatted.append(f'{a} x {b} x {c} mm')

                elif 'Ø' in size:
                    print('Insert sizes manually, found in \n')
                    print(page)    
                    numb = input('Give number of size combinations')

                    final_sizes_formatted = []

                    for i in range(numb):
                        final_sizes_formatted.append(input(f'Write down {i+1}th size'))




if __name__ == '__main__':
    scraper = INRScraper()
    scraper.scraped_dataframe = scraper.scrape_mirrors()  
    #scraper.overwrite_dataframe()      