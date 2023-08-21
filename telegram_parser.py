import telethon
from utils import *

class TelegramParser():
    def __init__(self, config) -> None:
        self.client = telethon.TelegramClient(
            "telegram_listener", 
            config['telegram']['api_id'],
            config['telegram']['api_hash']
        )
        self.channels = config['telegram']['telegram_channels']
        self.keywords = config['keywords']

    def bot_join_chats():
        pass

    def start(self):
        self.client.start()
        for channel in self.channels:
            self.client.get_messages(channel, limit=100)

    def listen(self):
        for message in self.client.iter_dialogs():
            for keyword in self.keywords:
                if keyword in message.text:
                    print(f"Found keyword '{keyword}' in message '{message.text}'")

    def run(self):
        self.start()
        self.listen()


if __name__ == "__main__":
    config = read_json('config.json')
    parser = TelegramParser(config)
    parser.run()