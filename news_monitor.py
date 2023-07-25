
from rss_feed_parser import RSSFeedParser
from sentiment_nlp import SentimentNLP
from telegram_helpers import TelegramLogHandler, TelegramMessenger
from db_wrapper import DBWrapper
from utils import *
import logging
from datetime import datetime, timedelta
import sqlite3



class NewsMonitor():
    def __init__(self, config) -> None:
        self.config = config
        self.db_wrapper = DBWrapper(config['database_path'])
        self.telegram_log_handler = TelegramLogHandler(config['telegram']['bot_token'], \
                                                       config['telegram']['chat_id'])
        self.nlp_pipe = SentimentNLP(config['nlp_model'], TelegramMessenger(config['telegram']['bot_token'], \
                                                                            config['telegram']['chat_id']))
        self.rss_parser = RSSFeedParser(config['rss_feeds'], config['keywords'], self.nlp_pipe, self.db_wrapper)

        logging.basicConfig(
        filename='log/news_monitor.log',
        encoding='utf-8', 
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        if config['telegram']['enabled'] == True:
            telegram_handler = TelegramLogHandler(config['telegram']['bot_token'], config['telegram']['chat_id'])
            self.logger.addHandler(telegram_handler)
        

    def monitor_news(self, save_to_db=True):
        self.logger.info(f'Initializing news monitor on {datetime.now()}')
        
        while True:
            try:
                datetime_filter = datetime.now() - timedelta(days = 1)

                rss_feeds = self.rss_parser.parse_and_analyze_rss_feeds(datetime_filter, save_to_db=save_to_db)

                time.sleep(5)
            except Exception as e:
                self.logger.error(e)


if __name__ == "__main__":
    config = read_json('config.json')
    news_monitor = NewsMonitor(config)
 
    news_monitor.monitor_news()