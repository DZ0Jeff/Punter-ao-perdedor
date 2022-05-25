import os
from src.models.BetsAPI import BetsApiCrawler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    bot = BetsApiCrawler(ROOT_DIR, display_browser=True)
    try:
        while True:
            players = bot.select_last_match()
            for match in players:
                bot.get_match(match)
            print('> Terminado!')

    except Exception as erro:
        bot.finish()
        raise
        # print(erro)

    except KeyboardInterrupt:
        print('> Saindo..., volte sempre!')
        bot.finish()

    finally:
        print('> Saindo...')
        bot.finish()


if __name__ == "__main__":
    main()
