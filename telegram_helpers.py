import logging 
import requests
import getpass
from datetime import datetime

class TelegramLogHandler(logging.Handler):
    def __init__(self, bot_token, chat_id):
        """
        Initializes the TelegramLogHandler.

        Args:
            bot_token (str): The bot token for accessing the Telegram API.
            chat_id (str): The chat ID for sending messages.
        """
        super().__init__()
        self.username = getpass.getuser()
        self.telegram_messenger = TelegramMessenger(bot_token, chat_id)

    def emit(self, record):
        """
        Sends log records as Telegram messages.

        Args:
            record (logging.LogRecord): The log record to be sent.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {self.username} - {self.format(record)}"
        self.telegram_messenger.send_telegram_message(log_entry)

class TelegramMessenger():
    def __init__(self, bot_token, chat_id):
        """
        Initializes the TelegramMessenger.

        Args:
            bot_token (str): The bot token for accessing the Telegram API.
            chat_id (str): The chat ID for sending messages.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_telegram_message(self, message):
        """
        Sends a message using the Telegram API.

        Args:
            message (str): The message to be sent.
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Telegram message. Error code: {response.status_code}")
        except Exception as e:
            print(f"failed with exception {e}")
        