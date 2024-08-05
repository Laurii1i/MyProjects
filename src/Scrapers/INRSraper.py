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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
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
        self.db_path = os.path.join(PATH, 'Databases', f'{self.company_name}.db')
        self.chromedriver = os.path.join(PATH, 'Scrapers', 'chromedriver.exe')

        s = Service(self.chromedriver)

        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")  # Disable pop-up blocking
        chrome_options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(service = s, options=chrome_options)            
        self.wait = WebDriverWait(self.driver, 5) # 10 sec timeout
        self.actions = ActionChains(self.driver)


    def test(self):

        try:
            self.driver.find_element(By.XPATH, '/html/body/div')
            print('dfdg')

        except:
            print('vittu')    
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
            for i, href in enumerate(products_hrefs):

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

                if i == 0:
                    extras = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[3]/span[1]')))
                    extras.click()
                    panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div[2]/div')))
                    items = panel.find_elements(By.CLASS_NAME, 'grid_item ')

                    items = [item for item in items if 'ILMAN' not in item.text]
                    og_price = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]/div'))).text
                    og_price = self.remove_non_numbers(og_price)

                    for item in items:
                        name = item.text
                        item.click()
                        time.sleep(0.5)
                        new_price = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]/div').text
                        new_price = self.remove_non_numbers(new_price)

                        price = int(new_price) - int(og_price)

                        colors_panel = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[3]/div[2]/div')
                        colors = colors_panel.find_elements(By.CLASS_NAME, 'grid_item ')
                        colors = [color.text for color in colors]

                        for color in colors:

                            db_dict['name'].append(name)
                            db_dict['type'].append('Kahva')
                            db_dict['color'].append(color)
                            db_dict['webpage'].append('INR')
                            db_dict['url'].append(' ')
                            db_dict['size'].append(' ')
                            db_dict['info'].append(' ')
                            db_dict['price'].append(str(price))

                    self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[1]/span[1]').click() 

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

        db_dict['name'].append('PLUS POWER')
        db_dict['color'].append(' ')
        db_dict['price'].append('110')
        db_dict['size'].append(' ')
        db_dict['type'].append('Lisävaruste')
        db_dict['url'].append(' ')
        db_dict['webpage'].append('INR')
        db_dict['info'].append('Pistorasia (230V). Pistorasiaa ei ole esiasennettu. Valitse itse sijoitus.')         
        return pd.DataFrame(db_dict)

    def fetch_size_info_from_description(self, desc):

        if 'cm' in desc:
            block = desc.split('cm')[0]

            numbers = re.findall(r'\d+', block)

            sizes = [number + '0 mm' for number in numbers]

            return sizes

        elif 'mm ' in desc or 'mm.' in desc:
            block = desc.split('mm')[0]

            numbers = re.findall(r'\d+', block)

            sizes = [number + ' mm' for number in numbers]

            return sizes
            

    def close_pop_up(self):

        try:
            # Wait for the shadow host to be present
            shadow_host = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#wisepops-instance-503489"))
            )

            
            # Use JavaScript to access the shadow root and find the SVG
            close_button = self.driver.execute_script("""
                var shadowRoot = arguments[0].shadowRoot;
                var svg = shadowRoot.querySelector('svg.PopupCloseButton__PopupCloseIcon-sc-srj7me-1.cDxkkR');
                return svg ? svg.closest('button') || svg.closest('a') || svg : null;
            """, shadow_host)

            # Check if the close button was found
            if close_button is None:
                raise NoSuchElementException("Close button not found in shadow DOM")

            # Try to click the element directly
            try:
                close_button.click()
            except Exception:
                # If direct click fails, try to trigger a click event using JavaScript
                self.driver.execute_script("""
                    var evt = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    arguments[0].dispatchEvent(evt);
                """, close_button)

        except TimeoutException:
            print("Timed out waiting for shadow host to appear")
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
        except JavascriptException as e:
            print(f"JavaScript error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        

    def switch_iframe(self):

        try:
            self.driver.switch_to.frame('fullscreen-iframe')
        except:
            time.sleep(0.1)
            self.switch_iframe()   

    def get_size(self, size):


        if size == '':
            return ['']

        if 'L:' in size and 'S:' in size:

            if not '/' in size:

                sizes = size.split('mm')
                sizes = [self.remove_non_numbers(size) for size in sizes]
                try:
                    sizes.remove('')
                except:
                    pass   
                
                final_sizes_formatted = [' x '.join(sizes)+' mm']

            else:

                sizes = size.split(' ')
                
                sizes = self.remove_no_number_containing_elements(sizes)

                final_sizes = []
                for size in sizes:

                    if '/' not in size:
                        final_sizes.append(size)
                    else:
                        final_sizes.append(size.split('/'))   
                        elements = len(size.split('/'))

                final_sizes_2 = []

                for size in final_sizes:

                    if type(size) == str:
                        final_sizes_2.append([size]*elements)

                    else:
                        final_sizes_2.append(size)

                final_sizes_formatted = []
                for i in range(elements):

                    a,b = final_sizes_2[0][i], final_sizes_2[1][i]

                    if len(final_sizes_2) == 3:
                        c = final_sizes_2[2][i]

                    else:
                        c = ''
                    final_sizes_formatted.append(f'{a} x {b} x {c} mm')

        elif 'Ø' in size:

            description = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/div[1]/p').text
            final_sizes_formatted = self.fetch_size_info_from_description(description)

        return final_sizes_formatted
    
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

                    img_src = self.website_url + product.find('img').get('src')

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

                time.sleep(1)
                try:
                    hyvaksy = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div/div/div[2]/div[2]/div/div[1]/button')
                    hyvaksy.click()
                except:
                    pass 

                info = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/p').text

                size_xpaths = ['//*[@id="model-section1"]/div/div[1]/span', '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/span']

                size_found = False
                for size_xpath in size_xpaths:
                    try:
                        size = self.driver.find_element(By.XPATH, size_xpath).text
                        size_found = True
                        break
                    except:
                        pass  
                
                if not size_found:
                    size = ''

                price_label = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/div[2]/span')
                self.actions.move_to_element(price_label).perform()
                price = self.remove_non_numbers(price_label.text)
                final_sizes_formatted = self.get_size(size)
                
                    
                for size in final_sizes_formatted:

                    db_dict['name'].append(name)
                    db_dict['size'].append(size)
                    db_dict['info'].append(info)
                    db_dict['url'].append(href)
                    db_dict['color'].append('')
                    db_dict['webpage'].append('INR')
                    db_dict['price'].append(price)
                    db_dict['type'].append('Peili')

            for i, cabinet in enumerate(mirror_cabinets):


                name, category, href = cabinet

                self.driver.get(href)

                if i == 0:
                    time.sleep(12)
                    self.close_pop_up()
                
                try:
                    info = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/p')))
                    info = info.text
                except:
                    info = ''    


                size_xpaths = ['//*[@id="model-section1"]/div/div[1]/span', '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/span']

                size_found = False
                for size_xpath in size_xpaths:
                    try:
                        size = self.driver.find_element(By.XPATH, size_xpath).text
                        size_found = True
                        break
                    except:
                        pass  
                
                if not size_found:
                    size = ''

                final_sizes_formatted = self.get_size(size)

                muokkaa_xpaths = ['/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[4]/div/a', '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[5]/div/a', '/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div[5]/div/a', '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[3]/div/a', '/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/div/a']
                
                for xpath in muokkaa_xpaths:

                    try:
                        muokkaa = self.driver.find_element(By.XPATH, xpath)
                        break
                    except:
                        pass    
                  

                try:
                    muokkaa.click()

                except:

                    self.actions.move_to_element(muokkaa).perform() 
                    muokkaa.click()
                
                self.switch_iframe()
                

                options = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[1]/div/div/div/div[2]/div[2]')))
                options.click()

                if i == 0:
                    extras = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[3]/span[1]')))
                    extras.click()
                    panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div')))
                    items = panel.find_elements(By.CLASS_NAME, 'grid_item ')

                    items = [item for item in items if 'ILMAN' not in item.text]
                    og_price = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]/div').text
                    og_price = self.remove_non_numbers(og_price)

                    for item in items:
                        name = item.text
                        item.click()
                        time.sleep(0.5)
                        new_price = self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]/div').text
                        new_price = self.remove_non_numbers(new_price)

                        price = int(new_price) - int(og_price)

                        db_dict['name'].append(name)
                        db_dict['type'].append('Lisävaruste')
                        db_dict['color'].append(' ')
                        db_dict['webpage'].append('INR')
                        db_dict['url'].append(' ')
                        db_dict['size'].append(' ')
                        db_dict['info'].append(' ')
                        db_dict['price'].append(str(price))
                    self.driver.find_element(By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[1]/span[1]').click()    

                color_options = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]/span[1]')))
                color_options.click()
                    
                main_color_panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]/div')))
                time.sleep(0.1)
                
                main_cols = main_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')

                main_cols_text = [main_col.text for main_col in main_cols]
            
                if 'ACCENT / NCS' in main_cols_text:
                    accent_but = main_cols.pop()

                    main_cols_text = [main_col.text for main_col in main_cols]
                    self.wait.until(EC.element_to_be_clickable(accent_but))
                    
                    try:
                        accent_but.click()
                    except:
                        self.close_pop_up()
                        accent_but.click()   
                         
                    accent_color_panel = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div[2]/div')))
                    accent_cols = accent_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')
                else:
                    accent_but = None
                    accent_cols = []

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
                    
                    for size_info in final_sizes_formatted:
                        db_dict['color'].append(color)
                        db_dict['price'].append(price)
                        db_dict['size'].append(size_info)
                        db_dict['name'].append(name)
                        db_dict['type'].append('Peilikaappi')
                        db_dict['url'].append(f'{self.website_url}{href}')
                        db_dict['webpage'].append('INR')
                        db_dict['info'].append(info)

        return pd.DataFrame(db_dict)
    
    def scrape_faucets(self):

        webpage = 'https://www.inr.fi/tuotteet/allaskaapit/'

        db_structure = ('name','type','color', 'size', 'price','url','webpage', 'info')
        db_dict = {item: [] for item in db_structure}

        response  = requests.get(webpage)

        if response.status_code == 200:

            #self.driver.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')

            main = soup.find(class_ = 'container-fluid product-filter-result')
            main_panel = main.find(class_ = "row")
            products = main_panel.find_all(class_ = "col-sm-6 col-md-4 col-lg-4 col-xl-3 col-xxl-2")

            for product in products:

                name = product.find('h3').get_text(strip = True)
                if len(name) > 25:
                    continue

                category = product.find(class_ = "category-heading").get_text(strip = True)
                href = product.find('a').get('href')

                img_src = self.website_url + product.find('img').get('src')

                if not self.product_figure_exists(name = name):
                    self.download_image(save_name = name, img_src = img_src)

                self.driver.get(href)

                size_string = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/span')))

                size_list = size_string.split('mm.')

                for size_item in size_list:
                    if 'Allaskaluste' in size_item:
                        size_string_a = size_item
                    elif 'Posliinipesuallas' in size_item:
                        size_string_p = size_item
                    elif 'Pöytätaso' in size_item:
                        size_string_t = size_item    

                try:
                    size_list_a = self.extract_numbers_from_string(size_string_a)
                    size_a = ' x '.join(size_list_a)+' mm'
                except:
                    size_list_a = ' '    

                try:
                    size_list_p = self.extract_numbers_from_string(size_string_p)
                    size_p = ' x '.join(size_list_p)+' mm'
                except:
                    size_list_p = ' '   

                try:
                    size_list_t = self.extatct_numbers_from_string(size_string_t)
                    size_t = ' x '.join(size_list_t)+' mm'
                except:
                    size_list_t = ' '   
                

                info = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/p').text

                muokkaa = self.wait.until(EC.presence_of_element_located((By.ID, 'aboutproduct-configurator-open')))

                self.actions.move_to_element(muokkaa).perform()

                muokkaa.click()

                self.switch_iframe()

                option_but = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[1]/div/div/div/div[2]/div[1]')))
                

if __name__ == '__main__':
    scraper = INRScraper()
    scraper.scraped_dataframe = scraper.scrape_cabinets()  
    scraper.append_to_database(scraper.scraped_dataframe)

    scraper.scraped_dataframe = scraper.scrape_mirrors()
    scraper.append_to_database(scraper.scraped_dataframe)
    #scraper.overwrite_dataframe()      