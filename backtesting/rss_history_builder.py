
from datetime import datetime, timedelta
import requests
import time
import os


import sys

current_directory = os.getcwd()
root_directory = os.path.dirname(current_directory)
sys.path.append(os.path.join(root_directory, 'news_monitor'))

from news_monitor import NewsMonitor
from rss_feed_parser import RSSFeedParser
from utils import *

from dateutil import parser as timeparser


def WSJ_rss_history_fetchers_from_wayback_machine(start, end):
    wayback_WSJ_template = "https://web.archive.org/web/<YYYYMMDDHHMM>/https://feeds.a.dj.com/rss/RSSMarketsMain.xml"

    def save_xml(url):
        response = requests.get(url)
        xml = response.content
        memento_datetime = response.headers['memento-datetime']
        next_memento = response.headers['link']
        next_memento_time = next_memento[next_memento.find('next memento')+25:].split("\"")[0]
        print(f"memento_datetime={memento_datetime}")
        print(f"next_memento_time={next_memento_time}")
        with open(f"./backtesting/history_rss_feeds/WSJ/{timeparser.parse(memento_datetime).strftime('%Y%m%d%H%M')}_{url.split('/')[-1]}", "wb") as f:
            f.write(xml)
        return timeparser.parse(next_memento_time)

    next_memento_time = start
    while next_memento_time.replace(tzinfo=None) < end:
        try:
            url = wayback_WSJ_template.replace('<YYYYMMDDHHMM>', next_memento_time.strftime('%Y%m%d%H%M'))
            print(f'processing {url}')
            next_memento_time = save_xml(url)
            time.sleep(1)
        except Exception as e:
            print(f'Failed on {url}.\nException:{e}')
            continue

class BuildHistoryNewsMonitor(NewsMonitor):
    def __init__(self, config, rss_history_folder) -> None:
        super().__init__(config)
        self.rss_history_files = self._build_history_rss_files_list(rss_history_folder)
        self.rss_parser = RSSFeedParser(self.rss_history_files, config['keywords'], self.nlp_pipe, self.db_wrapper)

    def _build_history_rss_files_list(self, rss_history_folder):
        files = os.listdir(rss_history_folder)
        xml_list = []
        for file in files:
                rss_feed = {}
                rss_feed['name'] = 'WSJ'
                rss_feed['url'] = f"{rss_history_folder}/{file}"
                rss_feed['weight'] = 10
                xml_list.append(rss_feed)

        return xml_list
    
    def save_history_to_db(self):
        self.rss_parser.parse_and_analyze_rss_feeds(save_to_db=True)


if __name__ == "__main__":
    config = read_json('config.json')

    rss_history_folder = './backtesting/history_rss_feeds/WSJ/'
    start = datetime(2022,1,1)
    end = datetime(2023,7,26)
    # fetch historical rss feeds from the wayback machine website
    # WSJ_rss_history_fetchers_from_wayback_machine(start, end)

    news_monitor = BuildHistoryNewsMonitor(config, rss_history_folder)
    # process historical rss feeds
    news_monitor.save_history_to_db()


