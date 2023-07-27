import time
import json
import logging
from telegram_helpers import TelegramLogHandler

def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        # print('func:%r args:[%r, %r] took: %2.4f sec' %(f.__name__, args, kw, te-ts))
        print('func:%r took: %2.4f sec' %(f.__name__, te-ts))
        return result

    return timed

def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
    

def set_logger(log_file, log_level='ERROR'):
    log_levels = {'INFO':logging.INFO,
                  'WARNING':logging.WARNING,
                  'DEBUG':logging.DEBUG,
                  'ERROR':logging.ERROR,
                  'CRITICAL':logging.CRITICAL,
                  'FATAL':logging.FATAL}
    config = read_json('config.json')
    logging.basicConfig(
    filename=f'log/{log_file}',
    encoding='utf-8', 
    level=log_levels[log_level],
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(__name__)
    if config['telegram']['enabled'] == True:
        telegram_handler = TelegramLogHandler(config['telegram']['bot_token'], config['telegram']['chat_id'])
        logger.addHandler(telegram_handler)
    
    return logger
    