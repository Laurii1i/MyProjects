import os
import pandas as pd

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)
PATH = os.path.join(PATH, '..')

class CommonScraper:

    def __init__(self):

        self.website_name = ''
        self.website_url = ''
        self.database_PATH = os.path.join(PATH, 'Databases')

    def save_to_database(self):

        if not hasattr(self, 'scraped_database'):
            print('A database has not been scraped into the memory.')
            return
        
        pass


    def overwrite_database(self):

        if not hasattr(self, 'scraped_database'):
            print('A database has not been loaded into the memory.')
            return
        
        db_path = os.path.join(PATH, 'Databases', f'{self.website_name}.db')
        self.scraped_database.to_csv(db_path, index = False)
        print(f'Database written to {db_path}')

    def look_for_differences(self) -> bool:

        if not hasattr(self, 'scraped_database') and not hasattr(self, 'existing_database'):
            print('You need to have Scraped and Existing databases loaded into memory to compare them.')
            return
        
        scraped_names = set(self.scraped_database['name'])
        existing_names = set(self.existing_database['name'])

        only_in_scraped = list(scraped_names - existing_names)
        only_in_existing = list(existing_names - scraped_names)

        self.new_products = self.scraped_database[self.scraped_database['name'].isin(only_in_scraped)]
        self.notfound_products = self.existing_database[self.existing_database['name'].isin(only_in_existing)]

        common_names = scraped_names.intersection(existing_names)
        common_scraped = self.scraped_database[self.scraped_database['name'].isin(common_names)]
        common_existing = self.existing_database[self.existing_database['name'].isin(common_names)]

        for name in common_names:

            common_scraped[common_scraped['name'] == name]
            common_existing[common_existing['name'] == name]

            if common_scraped.equals(common_existing):
                continue

            else:
                print('\nData changes detected:\n')
                print(f'Old data: {common_existing}\n')
                print(f'New data: {common_scraped}\n')




    def load_database(self):
        
        self.existing_database = pd.read_csv(os.path.join(self.database_PATH, f'{self.website_name}.db'), dtype = str)

    def run(self):
        print('Toteuta tämä alaluokissa')
    
