import sqlite3

class DBWrapper():
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def save_to_db(self, df, table_name, if_exists='append', index=False):
        df.to_sql(name=table_name, con=self.conn, if_exists=if_exists, index=index)
        self.conn.commit()

    def get_article_ids_from_db(self):
        try:
            sql = "SELECT id FROM rss_feeds"
            self.cursor.execute(sql)
            ids = self.cursor.fetchall()
            ids = [id[0] for id in ids]
            return ids
        except:
            return []