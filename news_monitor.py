
from rss_feed_parser import RSSFeedParser
from sentiment_nlp import SentimentNLP
from telegram_helpers import TelegramMessenger
from db_wrapper import DBWrapper
from utils import *
from datetime import datetime, timedelta

class NewsMonitor():
    def __init__(self, config) -> None:
        """
        Initializes the NewsMonitor.

        Args:
            config (dict): The configuration dictionary containing project settings.
        """
        self.logger = set_logger(name=__name__, log_file='news_monitor.log', log_level='INFO')
        self.config = config
        self.telegram_messenger = None
        if config['telegram']['enabled'] == True:
            self.telegram_messenger = TelegramMessenger(config['telegram']['bot_token'], \
                                                        config['telegram']['chat_id'])
        self.db_wrapper = DBWrapper(config['database_path'])
        self.nlp_pipe = SentimentNLP(config['nlp_model'], self.telegram_messenger)
        self.rss_parser = RSSFeedParser(config['rss_feeds'], config['keywords'], self.nlp_pipe, self.db_wrapper)

    def get_db_wrapper(self):
        """
        Returns the database wrapper instance.

        Returns:
            DBWrapper: The instance of DBWrapper used for database operations.
        """
        return self.db_wrapper

    def monitor_news(self, save_to_db=True):
        """
        Monitors news alerts from various sources and performs sentiment analysis.

        Args:
            save_to_db (bool, optional): Whether to save results to the database. Defaults to True.
        """
        self.logger.info(f'Initializing news monitor on {datetime.now()}')
        
        while True:
            try:
                datetime_filter = datetime.now() - timedelta(days = 3)
                rss_feeds_with_keyword = self.rss_parser.parse_and_analyze_rss_feeds(datetime_filter, save_to_db=save_to_db)
                
                time.sleep(5)
            except Exception as e:
                self.logger.error(e)


if __name__ == "__main__":
    config = read_json('config.json')
    news_monitor = NewsMonitor(config)
 
    news_monitor.monitor_news()