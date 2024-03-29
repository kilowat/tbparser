import datetime

from lib.db import Db
from lib.wordparser import WordParser
import time
import threading
import conf
import logging


from lib.word_entity import WordEntity

thread_count = conf.main['thread_count']
env_config_file_path = conf.main['env_config_file_path']
file_path = conf.word_conf['file_path']
yandex_key = conf.main['yandex_key']

db = Db(env_config_file_path)

# to do get from db
word_entities = db.select_words_to_translate(limit=conf.word_conf['limit'])

db.close_connect()

start_time = time.time()


def run():
    db = Db(env_config_file_path)

    while len(word_entities) > 0:
        time.sleep(conf.main['sleep'])
        p = WordParser(file_path=file_path, yandex_key=yandex_key)
        entity = word_entities.pop()
        res = p.parse(entity)
        print(f"word:{res.word.encode('ascii', 'ignore').decode('ascii')} finded")
        print("time: %s seconds ---" % int((time.time() - start_time)))

        db.update_word_table(res)

    print("--- %s seconds ---" % (time.time() - start_time))


# -------------- Main process ----------------


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()

now = datetime.datetime.now()
logging.basicConfig(filename=conf.main['log_dir'] + 'word_parse_info.log', level=logging.INFO)
logging.info("time end work:" + str(now)[:19])