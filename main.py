from src.models.BetsAPI import BetsApiCrawler
from time import sleep


def main():
    bot = BetsApiCrawler()
    try:
        players = bot.select_last_match()
        for match in players[-1:]:
            bot.get_match(match)
        print('> Terminado!')

    except Exception as erro:
        raise
        # print(erro)

    except KeyboardInterrupt:
        print('Saindo..., volte sempre!')
    
    finally:
        print('Saindo...')
        bot.finish()


if __name__ == "__main__":
    main()