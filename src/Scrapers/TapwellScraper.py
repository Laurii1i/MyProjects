import CommonScraper

class TapwellScraper(CommonScraper):

    def __init__(self):

        super().__init__()
        self.website_name = 'Tapwell'
        self.website_url = 'https://www.tapwell.fi'

    def run(self):
        
        db_structure = ('name','type','color','price','number','url','webpage')

        db_dict = {item: [] for item in db_structure}

        s = Service(os.path.join(PATH, 'Scrapers','chromedriver.exe'))

        try:
            driver = webdriver.Chrome(service = s)
        except:
            #q.put(('Chromedriver ei löytynyt,\nEi voida hakea dataa sivulta Tapwell\n', 'red'))  
            return None

        wait = WebDriverWait(driver, 10) # 10 sec timeout
        base = self.website_url
        driver.get(base)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="coiPage-1"]/div[2]/button[2]')))

        except TimeoutException:
            #q.put(('Hyväksy cookiet - nappia ei löytynyt\nOhitetaan etsintä\n', 'red'))
            return

        try:
            hyvaksy_kaikki = driver.find_element('xpath', '//*[@id="coiPage-1"]/div[2]/button[2]')
            hyvaksy_kaikki.click()

        except:
            pass    

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/section[2]/div')))
        except TimeoutException:
            #q.put(('Etusivun paneelia ei löytynyt,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
            driver.quit()
            return None

        main_panel = driver.find_element('xpath', '//*[@id="app"]/main/section[2]/div')
        main_buts = main_panel.find_elements(By.TAG_NAME, 'a')
        main_buts = [but for but in main_buts if but.is_displayed()]

        if main_buts == []:
            #q.put(('Etusivun nappeja ei löytynyt,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
            driver.quit()
            return None

        if len(main_buts) != 4:
            #q.put((f'Etusivun nappeja löytyi {len(main_buts)} odotetun 4:n sijasta,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
            driver.quit()
            return None

        main_hrefs = [but.get_attribute('href') for but in main_buts]

        if None in main_hrefs:
            #q.put(('href - referenssi ei löytynyt kaikista etusivun napeista,\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
            driver.quit()
            return None

        types = ('Suihku', 'Kylpyhuonehana', 'Keittiöhana', 'Pyyhekuivain')
        main_hrefs = zip(main_hrefs,types)
        products = []

        try:
            actions = ActionChains(driver)
        except:
            #q.put(('ActionChains(driver) ei onnistunut\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))    
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
                    #q.put(f'Etsitään tuotteita: {tyyppi}\n')
                    break
            
            try: # Wait until tuotesivun paneeli (joka sisältää kaikki tuotteet on latautunut)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/div[3]/div')))
            except TimeoutException:
                #q.put(('Tuotesivun tuotepaneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))  
                driver.quit()
                return None 

            try: # odota kunnes värivaihtoehtopaneeli on latautunut
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul')))
            except TimeoutException:
                #q.put(('Tuotesivun värivaihtoehdot-paneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red')) 
                driver.quit()
                return None

            color_but_panel = driver.find_element('xpath','//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul') # paneeli, josta löytyy värinapit
        

            product_buts = []
            i = 1
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # scrollaa sivun pohjalle, jotta kaikki tuotteet latautuu oikein
            except:
                #q.put(('Ei voitu siirtyä sivun pohjalle.\nDatahaku sivustolta Tapwell keskeytyy.\n', 'red')) 
                driver.quit()
                return None 

            time.sleep(2)
            while True:
                xpath = f'//*[@id="app"]/main/div/div/div[3]/div/div[{i}]/div/a'
                try:
                    product_buts.append((driver.find_element('xpath', xpath)))
                    i = i+1
                except: 
                    #q.put(f'{i-1} eri tuotenimeä löytyi.\n')
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
                    #q.put(('Värivaihtoehdot-paneelia ei löytynyt\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
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
                        wait.until(lambda driver: self.has_changed(driver, ini_text, prod_num_xpath))
                        # wait a litle bit more to ensure that every piece of data has changed
                        time.sleep(0.02)
                    except:
                        pass

                    try: # Data variable contains the panel, which contains prod number, color, price information
                        data = driver.find_element('xpath', '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/div[1]/div[1]')
                    except:
                        #q.put((f'Tuotteen tietoja ei löytynyt sivulta\n{driver.current_url}\nDatahaku keskeytyy sivustolta Tapwell\n', 'red')) 
                        driver.quit()
                        return None

                    datas = data.find_elements(By.TAG_NAME, 'p')
                    # datas = [product_number, , price]

                    try: # name and color are found from here
                        prod_and_col = driver.find_element('xpath', '//*[@id="app"]/main/div/div/div[1]/div[1]/div[1]/h1').text
                    except:
                        #q.put((f'Tuotenumeroa ja väriä ei löytynyt sivulta\n{driver.current_url}\nDatahaku keskeytyy sivustolta Tapwell\n', 'red'))
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
                    db_dict['webpage'].append(self.website_name)

                    figure = driver.find_element('xpath','//*[@id="app"]/main/div/div/div[1]/div[2]/img')
                    fig_src = figure.get_attribute('src')
                    figure = requests.get(fig_src)

                    with open(os.path.join(PATH, 'Figures', self.website_name, f'{product_number}.png'), 'wb') as f:
                        f.write(figure.content)

                    #with open(f'{PATH}/../Figures/{self.website_name}/{product_number}.png', 'wb') as f:
                    #    f.write(figure.content)


                    time.sleep(0.1)

            driver.get(base) # go back to frontpage  
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/section[2]/div')))

        new_data = pd.DataFrame(db_dict)
        #new_data.to_csv('C:/Users/lauri/Documents/tap_project2/database2', index = False)
        driver.quit()
        return new_data  

if __name__ == '__main__':
    tapwell_scraper = TapwellScraper()
    tapwell_scraper.run()