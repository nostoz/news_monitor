import sqlite3
from utils import set_logger
import os
import pandas as pd

class DBWrapper():
    def __init__(self, db_path) -> None:
        self.logger = set_logger(log_file='db_wrapper.log', log_level='INFO')

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_rss_feeds_table_if_not_existing()          

    def save_to_db(self, df, table_name, if_exists='append', index=False):
        
        df = self.keep_older_records_when_duplicate_ids(table_name, df)
        df.to_sql(name=table_name, con=self.conn, if_exists=if_exists, index=index)
        self.conn.commit()

    def get_article_ids_from_db(self):
        try:
            sql = "SELECT id FROM rss_feeds"
            self.cursor.execute(sql)
            ids = self.cursor.fetchall()
            ids = [id[0] for id in ids]
            return ids
        except Exception as e:
            self.logger.error(f'Failed to fetch ids with exception {e}')
            return []

    def _create_rss_feeds_table(self):
        create_table_query = "CREATE TABLE rss_feeds \
            (id TEXT PRIMARY KEY, timestamp INTEGER, datetime TEXT, title TEXT,\
             summary TEXT, source TEXT, rss_feed_weight INTEGER,\
             keyword TEXT, keyword_weight INTEGER, sentiment_score REAL,\
             sentiment_label TEXT, custom_score REAL)"

        self.cursor.execute(create_table_query)

    def _create_rss_feeds_table_if_not_existing(self):
        try:
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="rss_feeds"')
        except sqlite3.OperationalError:
            self._create_rss_feeds_table()

    def drop_records(self, table_name, ids):
        """
        Drop records from the specified table that match the given list of IDs.

        Args:
            table_name: The name of the table.
            ids: The list of IDs to drop.

        Returns:
            None.
        """
        sql = f'DELETE FROM {table_name} WHERE id IN ({",".join(map(str, ids))})'
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def keep_older_records_when_duplicate_ids(self, table_name, df):
        """
        Checks which records between the database and the DataFrame have the same IDs and get 
        the list of those IDs where the field timestamp is older in the DataFrame compared to the database.

        Args:
            table_name: The name of the table.
            df: The DataFrame.

        Returns:
            The list of IDs where the field timestamp is older in the DataFrame compared to the database.
        """
        df = df.sort_values(by='timestamp').drop_duplicates(subset='id', keep='first')
        df_ids = df['id'].tolist()
        sql = f'SELECT id, timestamp FROM {table_name} WHERE id IN ({",".join(map(repr, df_ids))})'
        self.cursor.execute(sql)
        db_ids = self.cursor.fetchall()

        ids_to_remove_db = []
        ids_to_remove_df = []
        for db_tuple in db_ids:
            df_row = df[df['id'] == db_tuple[0]]
            if db_tuple[1] > df_row['timestamp'].values:
                ids_to_remove_db.append(db_tuple[0])
            else:
                ids_to_remove_df.append(db_tuple[0])

        if len(ids_to_remove_db) > 0:
            self.drop_records(table_name, ids_to_remove_db)
        if len(ids_to_remove_df) > 0:
            df = df[~(df['id'] == ids_to_remove_df)]

        return df

    