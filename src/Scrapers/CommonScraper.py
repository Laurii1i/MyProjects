import os
import pandas as pd
import re
import requests 
from selenium.webdriver.common.by import By

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)
PATH = os.path.join(PATH, '..')

class CommonScraper:

    def __init__(self):

        self.company_name = '' 
        self.website_url = ''
        self.database_PATH = os.path.join(PATH, 'Databases')
        self.scraped_dataframe = None
        self.existing_dataframe = None


    def remove_non_numbers(self, string: str) -> str:

        return re.sub(r'\D', '', string)
    
    def product_figure_exists(self, name):

        return os.path.isfile(os.path.join(PATH, 'Figures', self.company_name, f'{name}.png'))
    
    def download_image(self, save_name = str, img_src = None, img_path = None):

        if img_path:
            try:
                save_path = os.path.join(PATH, 'Figures', self.company_name, f'{save_name}.png')
                figure = self.driver.find_element(By.XPATH, img_path)
                img_src = figure.get_attribute("src")

                response = requests.get(img_src)

                if response.status_code == 200:
                    with open(save_path, 'wb') as file:
                        file.write(response.content)
            except:
                print(f'Figure download for {save_name} failed.')   

        if img_src: 
            try:
                response = requests.get(img_src)
                if response.status_code == 200:
                    with open(save_path, 'wb') as file:
                        file.write(response.content)
            except:
                print(f'Figure download for {save_name} failed.')                                       

    def append_to_dataframe(self):

        if self.scraped_dataframe is None:
            print('A dataframe has not been scraped into the memory.')
            return
        
        else:
            pass


    def overwrite_dataframe(self):

        if self.scraped_dataframe is None:
            print('A dataframe has not been loaded into the memory.')
            return
        
        assert self.company_name != '', "Company name cannot be empty"
        db_path = os.path.join(PATH, 'Databases', f'{self.company_name}.db')
        self.scraped_dataframe.to_csv(db_path, index = False)
        print(f'Dataframe written to {db_path}')

    def look_for_differences(self, scraped_dataframe, existing_dataframe) -> bool:

        scraped_names = set(scraped_dataframe['name'])
        existing_names = set(existing_dataframe['name'])

        only_in_scraped = list(scraped_names - existing_names)
        only_in_existing = list(existing_names - scraped_names) 

        new_products = scraped_dataframe[self.scraped_dataframe['name'].isin(only_in_scraped)]
        notfound_products = existing_dataframe[self.existing_dataframe['name'].isin(only_in_existing)]

        if len(new_products) != 0:
            print('New product(s) found!\n\n')
            for product in new_products.iterrows():
                print(f'{product}\n')
            print('\n')

        if len(notfound_products) != 0:
            print('Some products have gone extinct!\n\n')
            for product in notfound_products.iterrows():
                print(f'{product}\n')
            print('\n')
            
        common_names = scraped_names.intersection(existing_names)
        common_scraped = scraped_dataframe[scraped_dataframe['name'].isin(common_names)]
        common_existing = existing_dataframe[existing_dataframe['name'].isin(common_names)]

        for name in common_names:
            scraped_row = common_scraped[common_scraped['name'] == name].reset_index(drop=True)
            existing_row = common_existing[common_existing['name'] == name].reset_index(drop=True)

            if scraped_row.equals(existing_row):
                continue

            else:
                print('\nData changes detected:\n')
                print(f'Old data: {existing_row}\n')
                print(f'New data: {scraped_row}\n')



    def remove_duplicates_from_scraped_dataframe(self):

        if self.scraped_dataframe is None:
            print('Scraped dataframe not loaded to memory.')
        else:
            self.scraped_dataframe = self.scraped_dataframe.drop_duplicates(subset = ['name', 'type', 'color', 'size', 'price', 'info'])

    def load_dataframe(self):
        assert self.company_name != '', "Company name cannot be empty"
        return pd.read_csv(os.path.join(self.database_PATH, f'{self.company_name}.db'), dtype = str)

    def run(self):

        self.scraped_dataframe = self.scrape()
        self.remove_duplicates_from_scraped_dataframe()
        self.existing_dataframe = self.load_dataframe()
        self.look_for_differences(self.scraped_dataframe, self.existing_dataframe)
        
        a = input('Do you want to overwrite the existing dataframe?')
        if a in ['yes', 'y', 'Yes']:
            self.overwrite_dataframe()
        else:
            print('ei sitte')

