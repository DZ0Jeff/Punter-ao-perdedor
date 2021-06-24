from telethon import TelegramClient


def send_telegram_message(msg):
    api_id = 2106897
    api_hash = 'c02f382984864d67c0ced7b2d78a81a6'
    client = TelegramClient('betsapi_messages', api_id, api_hash)

    async def run_message():
        user = 'me'
        await client.send_message(user, msg)

    with client:
        client.loop.run_until_complete(run_message())
