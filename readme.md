# News Monitor 

The News Monitor project is designed to gather real-time news alerts from various channels based on given keywords. These alerts can be used as trading signals. The project utilizes RSS feeds and sentiment analysis to provide insights into the sentiment of the gathered news.

## Features

- Collects news alerts from multiple RSS feeds.
- Performs sentiment analysis on news articles using NLP models.
- Supports sending alerts and log messages to a Telegram chat.
- Stores news data in an SQLite database for later analysis.

## Project Structure

The project is organized into several modules and classes:

- `news_monitor.py`: The main entry point of the project, initializing and coordinating various components.
- `rss_feed_parser.py`: Handles parsing and analyzing RSS feeds for news alerts.
- `db_wrapper.py`: Provides a wrapper for database operations.
- `telegram_helpers.py`: Contains classes for sending messages to Telegram.
- `sentiment_nlp.py`: Handles sentiment analysis of news articles.
- `telegram_parser.py`: Work in progress for handling Telegram messages.
- `config.json`: Configuration file containing settings for the project.

## Getting Started

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Customize the `config.json` file with your preferred RSS feeds, keywords, and Telegram settings.
4. Run the `news_monitor.py` script to start gathering news alerts and performing sentiment analysis.

## Usage

1. Run the `news_monitor.py` script to start monitoring news alerts.
2. News alerts will be analyzed for sentiment and stored in the database.
3. Sentiment-related information may be sent to a specified Telegram chat if enabled.

## Future Improvements

- Implement complete functionality in `telegram_parser.py`.
- Enhance error handling and logging for robustness.
- Add unit tests to ensure the reliability of components.

## Contributions

Contributions are welcome! If you find any issues or have suggestions, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

*Note: This README provides a basic overview of the project. For detailed instructions and explanations, refer to the respective module files.*

