from utils.proxy import init_proxy
from utils.parser_handler import init_crawler, init_parser
from time import sleep
import requests
from fake_useragent import UserAgent
from utils.paths.chromedriver_path import path


BASE_LINK = "https://pt.betsapi.com"


def login_facebook(url="https://pt.betsapi.com/login", proxy=False):
    print('> Pegando link do login...')
    
    ua = UserAgent()
    user_agent = ua.random
    
    payload = {
        "user": "bedot54940@greenkic.com",
        "password": "green@215"
    }

    headers = { 'User-Agent' : user_agent }

    page = init_crawler(url)

    facebook_link = page.find('a', class_="btn btn-block btn-facebook")['href']
    print(facebook_link)
    
    print('> iniciando login...')
    with requests.Session() as session:
        login_link = "https://www.facebook.com/login/device-based/regular/login/?login_attempt=1&next=https%3A%2F%2Fwww.facebook.com%2Fdialog%2Foauth%3Fresponse_type%3Dcode%26client_id%3D177684156000502%26redirect_uri%3Dhttps%253A%252F%252Fpt.betsapi.com%252Fauth%252F%26scope%3Demail%26state%3DHA-1DZTYGXJK3WP4CEA92RI5LMNSUFH6O0B78QV%26ret%3Dlogin%26fbapp_pres%3D0%26logger_id%3D28da6016-21e2-4828-a3d0-a807b11518ba%26tp%3Dunspecified%26cbt%3D1623605689978&lwv=101"
        if proxy:
            proxy_ip = init_proxy(path)
            proxyList = { "http": "http://" + proxy_ip}
            active_session = session.post(login_link, data=payload, headers=headers, proxies=proxyList)

        else:
            active_session = session.post(login_link, data=payload, headers=headers)

        print(active_session)

        return session


def main():
    '''
    Insert your code here
    '''
    base_url = "https://pt.betsapi.com/ci/table-tennis"

    session = login_facebook(proxy=True)

    print('Ininciando Bot...')
    # soap = init_crawler(base_url)
    data = session.get(base_url)
    print(data.content)
    soap = init_parser(data.content)
    table = soap.find('table', id="tbl_inplay")
    firstGame = table.find("tr")
    # links = firstGame.find_all('a')
    
    print(table.get_text())

    # result = [ base_url + link['href'] for link in links ]

    # print('Pegando links ultimo jogo...')
    # print(" ".join(result))
   


if __name__ == "__main__":
    main()