from os import replace
from time import sleep
from utils.telegram import TelegramBot
from utils.time import generate_random_time
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page, remove_popup_odds
from utils.parser_handler import init_parser, remove_duplicates_on_array, remove_whitespaces
from utils.file_handler import save_error
from src.secrets import user, password
from selenium.common.exceptions import NoSuchElementException


class BetsApiCrawler:
    base_url = "https://pt.betsapi.com"
    requests = 0

    def __init__(self, root_path) -> None:
        print('> Iniciando Robô...')
        self.ROOT_PATH = root_path
        self.driver = setSelenium(self.ROOT_PATH, False)
        self.telegram = TelegramBot(root_path)
        self.telegram.send_message('Iniciando Punter ao perdedor...')
        self.login()
        self.driver.get("https://pt.betsapi.com")
        self.requests += 1
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
        print("> Selecionado partidas...")
        driver = self.driver
        driver.get(self.base_url + "/c/table-tennis")
        self.requests += 1
        self.restart(self.base_url + "/c/table-tennis")
        
        soap = self.parse_results()
        table = soap.find('table', class_="table table-sm")

        result = []
        for games in table.find_all("tr"): 
            links = games.find_all('a', text="View")

            result += [self.base_url + link['href'] for link in links]

        # result = remove_duplicates_on_array(result)
        print('> Partidas selecionadas...')
        return result

    def get_odds(self):
        driver = self.driver

        print('> Pegando odd da partida ...')
        generate_random_time()
        remove_popup_odds(driver)

        try:
            driver.find_element_by_link_text('Odds').click()
            generate_random_time()
            remove_popup_odds(driver)
            driver.find_element_by_link_text('Odds').click()
        
        except Exception as error:
            print(f"> Um erro aconteceu... {error}")
            return

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
        self.requests += 1
        self.restart(url)
        generate_random_time()

        print('> Pegando dados da partida...')
        try:
            win, lose, title, guest = self.get_match_history()

        except Exception as error:
            save_error(error)
            print('> Erro ao localizar resultados...')
            return

        if win > lose:
            print('> Pegando as odds das partidas...')
            odd = self.get_odds()
            print('Odd: ', odd)
            # self.telegram.send_message(f'Odd: {odd}')
            
            if float(odd) <= 1.4:
                print('Odd baixa!')
                # proxima ver resultado das partidas, sets
                self.get_current_match(odd, title, guest)

            else:
                print('> [INVÁLIDO] Odd alta! saindo...')

        else:
            print('> [INVÁLIDO] Derrotas maior e/ou iguais que vitórias, saíndo...')

    def get_match_history(self):
        driver = self.driver

        try:
            driver.find_element_by_link_text('História').click()
            # print(driver.current_url)
            remove_popup_odds(driver)
            # print(driver.current_url)
            driver.find_element_by_link_text('História').click()

        except Exception as error:
            save_error(error)
            print(f"> Um erro aconteceu... {error}")
            return

        soap = self.parse_results()

        raw_title = soap.select('h1 a')
        # print(raw_title)

        temp_title = [ title.get_text(separator='') for title in raw_title ]

        title = ' '.join(temp_title)
        guest = raw_title[0].get_text(separator='')
        full_title = remove_whitespaces(soap.find('h1').get_text(separator=''))

        win = 0
        lose = 0

        print('Titulo: ', full_title)

        table = soap.find_all('table', class_="table table-sm")
        for item in table:
            for column in item.find_all('tr'):
                for _ in column.find_all('td', class_="badge_W"):
                    win += 1
                
                # find wins in player historic
                for _ in column.find_all('td', class_="badge_L"):
                    lose += 1

        print('> Vitórias: ', win)
        print('> Derrotas: ', lose)

        return win, lose, title, guest

    def get_current_match(self, odd, title, guest):
        driver = self.driver

        try:
            driver.find_element_by_link_text('Matches').click()
            remove_popup_odds(driver)
            driver.find_element_by_link_text('Matches').click()
        
        except Exception as error:
            print(f'> Um erro aconteceu...{error}')
            return

        # match_link = driver.current_url

        match_link = title.replace(" ", "%20")

        bet365_link = f"https://www.bet365.com/#/AX/K^{match_link}"

        guest_lost = False
        while True:
            driver.refresh()
            soap = self.parse_results()

            try:
                # Se achar a partida iniciou!
                current_result = soap.select_one('h1 span.text-danger').text
                results = soap.select_one("div.container div.row div.col-md-4 div.card")
                list_results = results.find('ul', class_="list-group")

            except AttributeError:
                print('> Resultados ainda não disponíveis, aguarde...')
                # print(error)
                generate_random_time(60, 60)
                continue

            else:
                # Sair se a partida cancelada
                if current_result == "Cancelled":
                    print('Partida cancelada!')
                    break

                # seleciona o quadro de resultados
                match_list = []
                for result in list_results.find_all('li'):
                    # extrai as vitórias e as salvam para futuras manipulações
                    if "won" in result.text:
                        print(result.text)
                        match_list.append(result.text)

                win = 0
                lose = 0

                for wins in match_list:
                    if f"{guest}" in wins:
                        win += 1

                    if not f"{guest}" in wins:
                        lose += 1
                
                placar = f"{win} - {lose}"

                print(f"Placar: {placar}")

                # enviar mensagem ao usuário se o placar estiver em 2-0
                if placar == "2 - 0":
                    print('Enviar a alarme para o usuário!')
                    print('link', bet365_link)
                    self.telegram.send_message(f'Favorito {guest} ganhando!\nplacar {placar}\nlink: {bet365_link}\nodd: {odd}')
                    break

                if placar == "0 - 1" and not guest_lost:
                    self.telegram.send_message(f"Favorito {guest} perdendo de {placar} \nPartida: {bet365_link}\nodd: {odd}")
                    guest_lost = True

                if placar == "0 - 2" and not guest_lost:
                    self.telegram.send_message(f"Favorito {guest} perdendo de {placar} seguidas \nPartida: {bet365_link}\nodd: {odd}")
                    guest_lost = True

                # se for realizada 3 partidas, o jogo se encerra
                if len(match_list) >= 3:
                    break

                generate_random_time(30, 60)

    def parse_results(self):
        src = dynamic_page(self.driver)
        return init_parser(src)

    def finish(self):
        self.driver.quit()

    def restart(self, url):
        if self.requests % 250 == 0:
            self.finish()
            self.driver = setSelenium(self.ROOT_PATH, False)
            self.driver.get(url)
