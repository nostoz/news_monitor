import feedparser
import pandas as pd
from dateutil import parser as timeparser
import json
import concurrent.futures

from utils import *
from sentiment_nlp import SentimentNLP
from db_wrapper import DBWrapper

class RSSFeedParser:

    def __init__(self, rss_feeds, keywords, nlp_pipe:SentimentNLP, db_wrapper:DBWrapper):
        self.rss_feeds = rss_feeds
        self.keywords = keywords
        self.df_feeds = None
        self.nlp_pipe = nlp_pipe
        self.db_wrapper = db_wrapper

    def get_df_feeds(self, datetime_filter=None):
        if datetime_filter:
            return self.df_feeds[self.df_feeds['timestamp'] >= datetime_filter.timestamp()]
        return self.df_feeds

    @timeit
    def _parse_and_analyze_single_rss_feed(self, rss_feed, dump_json=False, datetime_filter=None, known_articles_ids=[]):
        df_feed = pd.DataFrame(columns=["id", "timestamp", "datetime", "title", "summary",\
                                         "source", "rss_feed_weight", "keyword", "keyword_weight", \
                                            "sentiment_score", "sentiment_label", "custom_score"])
        feed = feedparser.parse(rss_feed['url'])
        if dump_json == True:
            with open(f"{rss_feed['name']}.json", 'w') as fp:
                json.dump(feed, fp)
        
        for item in feed.entries:
            datetime_published = timeparser.parse(item.published)

            # skip news olrder than datetime_filter
            if (datetime_filter and datetime_published < datetime_filter) or item.id in known_articles_ids:
                continue

            summary = item.summary if 'summary' in item.keys() else ''
            df_feed.loc[df_feed.shape[0]] = {
                "id": item.id,
                "timestamp": int(datetime_published.timestamp()),
                "datetime": item.published,
                "title": item.title,
                "summary": summary,
                "source": item.link,
                "rss_feed_weight": rss_feed['weight']
            }
        
        df_feed_with_sentiment = self.nlp_pipe.get_sentiment(self.keywords, df_feed.reset_index(drop=True))

        return df_feed_with_sentiment
    
    @timeit
    def parse_and_analyze_rss_feeds(self, dump_json=False, save_to_db=True, datetime_filter=None, exclude_known_articles=True):
        if exclude_known_articles:
            known_articles_ids = self.db_wrapper.get_article_ids_from_db()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._parse_and_analyze_single_rss_feed, rss_feed, dump_json, datetime_filter, known_articles_ids)\
                        for rss_feed in self.rss_feeds]
            concurrent.futures.wait(futures)
            self.df_feeds = pd.concat([future.result() for future in futures])

            if save_to_db :
                self.db_wrapper.save_to_db(self.df_feeds, table_name="rss_feeds", if_exists='append', index=False)

        return self.df_feeds

