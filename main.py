from src.models.BetsAPI import BetsApiCrawler


def main():
    bot = BetsApiCrawler()
    try:
        while True:
            players = bot.select_last_match()
            for match in players:
                print(match)
            print('> Terminado!')


    except Exception as erro:
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
