from utils.telegram import TelegramBot
from utils.time import generate_random_time
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page, remove_popup_odds
from utils.parser_handler import init_parser, remove_duplicates_on_array
from src.secrets import user, password
from selenium.common.exceptions import NoSuchElementException


class BetsApiCrawler:
    base_url = "https://pt.betsapi.com"

    def __init__(self) -> None:
        print('> Iniciando Robô...')
        self.driver = setSelenium(False)
        self.telegram = TelegramBot()
        self.telegram.send_message('Iniciando Bot...')
        self.login()
        self.driver.get("https://pt.betsapi.com")
        generate_random_time()

    def login(self):
        """
        Login to BetsAPI in facebook

        params: None
        """
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
        """
        scrappe the lasts upcoming games

        :return: array: results of last macthes
        """
        driver = self.driver
        driver.get(self.base_url + "/c/table-tennis")
        
        soap = self.parse_results()
        table = soap.find('table', class_="table table-sm")

        result = []
        for games in table.find_all("tr"): 
            links = games.find_all('a', text="View")

            result += [self.base_url + link['href'] for link in links]

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

    def get_match(self, url):
        '''

        handler of upcoming matches

        :param url: url of match
        :return: void
        '''
        driver = self.driver
        driver.get(url)
        generate_random_time()

        print('> Pegando dados da partida...')
        win, lose, title = self.get_match_history()

        if win > lose:
            print('> Pegando as odds das partidas...')
            odd = self.get_odds()
            print('Odd: ', odd)
            # self.telegram.send_message(f'Odd: {odd}')
            
            if float(odd) <= 1.4:
                print('Odd baixa!')
                # proxima ver resultado das partidas, sets
                self.get_current_match(odd, title)

            else:
                print('> [INVÁLIDO] Odd alta! saindo...')

        else:
            print('> [INVÁLIDO] Derrotas maior que vitórias ou iguais, saíndo...')

    def get_match_history(self):
        driver = self.driver

        driver.find_element_by_link_text('História').click()
        remove_popup_odds(driver)
        driver.find_element_by_link_text('História').click()

        soap = self.parse_results()

        raw_title = soap.find('h1').get_text(separator='')
        title = " ".join(raw_title.split())

        win = 0
        lose = 0

        print(title)

        table = soap.find_all('table', class_="table table-sm")
        for item in table:
            for column in item.find_all('tr'):
                for _ in column.find_all('td', class_="badge_W"):
                    win += 1
                
                # find wins in player historic
                for _ in column.find_all('td', class_="badge_L"):
                    lose += 1

        print('Vitórias: ', win)
        print('Derrotas: ', lose)

        return win, lose, title

    def get_current_match(self, odd, title):
        driver = self.driver

        driver.find_element_by_link_text('Matches').click()
        remove_popup_odds(driver)
        driver.find_element_by_link_text('Matches').click()

        match_link = driver.current_url

        while True:
            generate_random_time(30, 60)
            driver.refresh()
            soap = self.parse_results()

            print('> Checando...')
            print(match_link)
            current_result = ''
            try:
                current_result = soap.select_one('h1 span.text-danger').text
            
            except Exception as error:
                print(error)
                print('Resultado ainda não disponivel! checando novamente...')
                continue

            print(f'Resultado: {str(current_result).strip()}')

            if current_result == "0-2" or current_result == "2-0":
                print('Enviar a alarme para o usuário!')
                print('link', match_link)
                self.telegram.send_message(f'link: {match_link}, odd: {odd}, partida: {title}')
                break

            # break_search = soap.find('table').find('tr', class_="text-center").find_all('td')[-1].text
            # print(break_search)

            # if break_search != 0:
            #     # print('Condição não achada...')
            #     continue
            #
            # else:
            #     print('Condição de quebra achada!')
            #     break
            # send_telegram_message(current_result)
            results_numbers = current_result.split('-')
            if int(results_numbers[0]) > 2 or int(results_numbers[1]) > 2:
                print('Condição de quebra achada!')
                break

    def parse_results(self):
        src = dynamic_page(self.driver)
        return init_parser(src)

    def finish(self):
        self.driver.quit()
