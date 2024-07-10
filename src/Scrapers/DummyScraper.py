import CommonScraper

class DummyScraper(CommonScraper):

    def __init__(self):

        self.website_name = 'Dummy'
        self.website_url = 'www.dummysitetobescraped.fi'

    def run(self):
        print('tässä pitäisi toteuttaa toinen scraperi')