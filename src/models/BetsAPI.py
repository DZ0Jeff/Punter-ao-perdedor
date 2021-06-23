from utils.time import generate_random_time
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page, remove_popup_odds
from utils.parser_handler import init_parser, remove_duplicates_on_array
from secrets import user, password

from selenium.common.exceptions import NoSuchElementException


class BetsApiCrawler:
    base_url = "https://pt.betsapi.com"

    def __init__(self) -> None:
        print('> Iniciando Robô...')
        self.driver = setSelenium(False)
        self.login()
        self.driver.get("https://pt.betsapi.com")
        generate_random_time()

    def login(self):
        '''
        Login to BetsAPI in facebook

        params: None
        '''
        driver = self.driver

        driver.get('https://pt.betsapi.com/login')
        generate_random_time()
        driver.find_element_by_class_name('btn.btn-block.btn-facebook').click()

        print('> Logando...')
        login_url = driver.current_url
        driver.find_element_by_name('email').send_keys(user)
        try:
            driver.find_element_by_name('password').send_keys(password)
        except NoSuchElementException:
            driver.find_element_by_name('pass').send_keys(password)

        try:
            driver.find_element_by_id('loginbutton').click()
        except NoSuchElementException:
            driver.find_element_by_name('login').click()

        generate_random_time()
        if driver.current_url == login_url:
            print('> Erro ao logar, informações inválidas ou algum erro aconteceu...')
            exit()
            
        print('> Logado!')

    def select_last_match(self):
        driver = self.driver
        driver.get(self.base_url + "/c/table-tennis")
        
        soap = self.parse_results()
        table = soap.find('table', class_="table table-sm")
        
        for games in table.find_all("tr"): 
            links = games.find_all('a', text="View")

            result = [ self.base_url + link['href'] for link in links ]

        result = remove_duplicates_on_array(result)
        return result

    def get_odds(self):
        driver = self.driver

        print('> Pegando odd da partida ...')
        generate_random_time()
        remove_popup_odds(driver)

        driver.find_element_by_link_text('Odds').click()
        generate_random_time()
        remove_popup_odds(driver)
        driver.find_element_by_link_text('Odds').click()

        soap = self.parse_results()
        table = soap.find('table')
        odd = table.select_one('tbody tr:nth-of-type(2) td:nth-of-type(2)').text
        # print('Odd: ', odd)
        return odd

    def view_player_history(self, url):
        '''
        Interact woth user profile history and gets wins and loses

        params: url => url of player
        '''
        print('> Procurando histórico de jogadores...')
        driver = self.driver
        driver.get(url)
        generate_random_time()

        soap = self.parse_results()

        player_details = dict()

        title = soap.find('h1').get_text(separator="")
        player = str(title).strip()
        win = 0
        lose = 0
        odds = []

        # print('Jogador: ', player)
        player_details["Nome"] = player

        for table in soap.find_all('table', class_="table table-sm"):
            
            # find wins in player historic
            for i in table.find_all('td', class_="badge_W"):
                win += 1
            
            # find wins in player historic
            for i in table.find_all('td', class_="badge_L"):
                lose += 1

        # print('Vitórias: ', win)
        # print('Derrotas: ', lose)
        player_details['Vitórias'] = win
        player_details['Derrotas'] = lose

        #  just procced if player has more wins than loses
        if win > lose:
            for table in soap.find_all('table', class_="table table-sm"):
                # get matches
                future_matches = table.find_all('a', href=True, text="View")
                for i in future_matches:
                    match = self.base_url + i['href']
                    # print(match)
                    odd = self.get_odds(match)
                    odds.append(odd)
            
        # print('Odds: ', ' '.join(odds))
        player_details['Média de odds'] = odds
        print(player_details)

    def get_match(self, url):
        driver = self.driver
        driver.get(url)
        generate_random_time()

        print('> pegando dados da partida...')
        win, lose = self.get_match_history()

        if win > lose:
            print('> Pegando as odds das partidas...')
            odd = self.get_odds()
            print('Odd: ', odd)
            
            if float(odd) <= 1.4:
                print('Odd baixa!')
                # proxima ver resultado das partidas, sets
                self.get_current_match()

    def get_match_history(self):
        driver = self.driver

        driver.find_element_by_link_text('História').click()
        remove_popup_odds(driver)
        driver.find_element_by_link_text('História').click()

        soap = self.parse_results()

        title = soap.find('h1').get_text(separator='')

        win = 0
        lose = 0

        print(title)

        table = soap.find_all('table', class_="table table-sm")
        for item in table:
            for column in item.find_all('tr'):
                for i in column.find_all('td', class_="badge_W"):
                    win += 1
                
                # find wins in player historic
                for i in column.find_all('td', class_="badge_L"):
                    lose += 1

        print('Vitórias: ',win)
        print('Derrotas: ', lose)

        return win, lose

    def get_current_match(self):
        driver = self.driver
        
        driver.find_element_by_link_text('Matches').click()
        remove_popup_odds(driver)
        driver.find_element_by_link_text('Matches').click()

        match_link = driver.current_url

        while True:
            generate_random_time()
            soap = self.parse_results()

            current_result = ''
            try:
                current_result = soap.select_one('h1 a.text-danger').text
            
            except Exception as error:
                print(error)
                print('Resultado não disponivel!')
                continue

            if current_result == "0-2":
                print('Enviar a alarme para o usuário!')
                print('link', match_link)

            if soap.find('table').find('th', text="5"):
                print('Condição de quebra achada!')
                break

    def parse_results(self):
        src = dynamic_page(self.driver)
        return init_parser(src)

    def finish(self):
        self.driver.quit()

