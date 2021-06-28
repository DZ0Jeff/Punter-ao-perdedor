import os

import telegram
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    """
    Telegram message handler

    - to get chat: access @getidsbot and type start to get id
    - to access token, create bot in @botFather and paste the token
    """
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    CHAT_ID = [1593930824]
    mybots = {}

    def __init__(self):
        self.bot = telegram.Bot(token=self.TOKEN)

    def send_message(self, msg):
        try:
            print('Enviando mensagem...')
            for chat in self.CHAT_ID:
                self.bot.sendMessage(chat_id=chat, text=msg)

        except Exception as error:
            print(f'> [ERRO] ao enviar mensagem! {error} ')

        else:
            print('Mensagem enviada com sucesso!')
