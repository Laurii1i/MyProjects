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

        db_structure = ('name','type','color', 'size', 'price','url','webpage', 'info')
        self.db_dict = {item: [] for item in db_structure}

    def scrape_cabinets(self):

        kaappi = 'https://www.inr.fi/tuotteet/kylpyhuonesailytys/'

        existing_images = os.path.join(PATH, 'Figures', self.company_name)
        existing_images = [fig.strip('.png') for fig in existing_images]


        response  = requests.get(kaappi)

        if response.status_code == 200:

            chrome_options = Options()
            chrome_options.add_argument("--disable-search-engine-choice-screen")
            chrome_options.add_argument("--start-maximized")

            s = Service(self.chromedriver)
            driver = webdriver.Chrome(service = s, options=chrome_options)            
            wait = WebDriverWait(driver, 30) # 10 sec timeout
            actions = ActionChains(driver)

            soup = BeautifulSoup(response.text, 'html.parser')

            main = soup.find(class_ = 'container-fluid product-filter-result')
            main_panel = main.find(class_ = "row")
            products = main_panel.find_all(class_ = "col-sm-6 col-md-4 col-lg-4 col-xl-3 col-xxl-2")

            if len(products) != 25:
                print(f'{len(products)} products were found instead of expected 25.')


            products_hrefs = [product.find('a').get('href') for product in products]
            
            description_panel_xpath = '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]'
            for href in products_hrefs:

                driver.get(f'{self.website_url}{href}') 

                time.sleep(2)

                try:
                    accept_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
                    accept_cookies.click()
                except:
                    pass

                wait.until(EC.presence_of_element_located((By.XPATH, description_panel_xpath)))

                name = driver.find_element(By.XPATH, '//*[@id="ec-text-wrapper-inner-slideshow-h2"]').text
                typpe = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/h4').text
                info = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[5]/div/div[1]/p').text

                size_info = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/span')
                actions.move_to_element(size_info).perform()

                sizes = size_info.text.split('mm')
                sizes = [self.remove_non_numbers(size) for size in sizes]
                sizes.remove('')
                size_info = ' x '.join(sizes)+' mm'

                #iframes_before = len(driver.find_elements(By.TAG_NAME, 'iframe'))
                muokkaa = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/div/div[2]/div[4]/div/a')
                muokkaa.click()

                new_iframe = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/iframe[1]')))

                #iframes_after = len(driver.find_elements(By.TAG_NAME, 'iframe'))

                driver.switch_to.frame(new_iframe)
                
                options = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[1]/div/div/div/div[2]/div[3]')))
                options.click()

                color_options = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]')))
                color_options.click()

                #accent_but = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "ACCENT")]')))
                #accent_but.click()
                
                main_color_panel = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div')))
                
                main_cols = main_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')
                accent_but = main_cols.pop()

                wait.until(EC.element_to_be_clickable(accent_but))
                accent_but.click()
                accent_color_panel = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div[2]/div')))

                accent_cols = accent_color_panel.find_elements(By.CLASS_NAME, 'grid_item ')

                for col in accent_cols + main_cols:
                    
                    wait.until(EC.element_to_be_clickable(col))

                    try:
                        col.click()
                    except:
                        driver.execute_script("""
                        arguments[0].scrollIntoView({
                            behavior: 'smooth',
                            block: 'end'
                        });
                    """, col)
                        time.sleep(1)
                        col.click()

                    time.sleep(0.5)
                    price_label = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/main/section[3]/div[4]/div[1]/button/span[2]')))

                    price = self.remove_non_numbers(price_label.text)
                    color = col.text
                    
                    self.db_dict['color'].append(color)
                    self.db_dict['price'].append(price)
                    self.db_dict['size'].append(size_info)
                    self.db_dict['name'].append(name)
                    self.db_dict['type'].append(typpe)
                    self.db_dict['url'].append(f'{self.website_url}{href}')
                    self.db_dict['webpage'].append('INR')
                    self.db_dict['info'].append(info)
                print(self.db_dict)    






if __name__ == '__main__':
    scraper = INRScraper()
    scraper.scrape_cabinets()        