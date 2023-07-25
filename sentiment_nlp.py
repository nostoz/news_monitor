
from transformers import pipeline
from utils import *

class SentimentNLP():
    def __init__(self, model, telegram_messenger=None) -> None:
        self.model = model
        self.pipe = pipeline("sentiment-analysis", model=model, device="cuda")
        self.telegram_messenger = telegram_messenger

    def _is_keyword_in_string(self, keyword, string_to_search):
        if isinstance(keyword, list):
            return all(k.casefold() in string_to_search.casefold() for k in keyword)
        else:
            return keyword.casefold() in string_to_search.casefold()

    @timeit
    def get_sentiment(self, keywords, df_feeds):
        new_sentiment_analyses = []
        for idx, row in df_feeds.iterrows():
            for keyword in keywords:
                if self._is_keyword_in_string(keyword, row['title']) or self._is_keyword_in_string(keyword, row['summary']): 
                    sentiment = self.pipe(f"{row['title']}\n{row['summary']}")
                    
                    df_feeds.loc[idx, 'keyword'] = str(keyword)
                    df_feeds.loc[idx, 'sentiment_score'] = sentiment[0]['score']
                    df_feeds.loc[idx, 'sentiment_label'] = sentiment[0]['label']
                    new_sentiment_analyses.append([row['datetime'], keyword, row['title'], row['source'], f"{sentiment[0]['label']} ({sentiment[0]['score']:0.2f})"])

        if self.telegram_messenger and len(new_sentiment_analyses) > 0:
            telegram_msgs = [""]
            count_msgs = 0
            for element in new_sentiment_analyses:
                if len(telegram_msgs[count_msgs] + str(element)) >= 4000:
                    count_msgs += 1
                    telegram_msgs.append("")
                telegram_msgs[count_msgs] += f"Published on: {element[0]}\n\
                                        Keyword: {element[1]}\n\
                                        Title: {element[2]}\n\
                                        Source: {element[3]}\n\
                                        Sentiment: {element[4]}\n\n"

            for msg in telegram_msgs:
                self.telegram_messenger.send_telegram_message(msg)
                
        return df_feeds[df_feeds['keyword'].isna() == False]