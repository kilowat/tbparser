import datetime

from lib.db import Db
from lib.forvoparser import Forvoparser
import time
import threading
import conf
import logging


from lib.word_entity import WordEntity

limit = conf.forvo_conf['limit']  # max download file every word

thread_count = conf.main['thread_count']
env_config_file_path = conf.main['env_config_file_path']
file_path = conf.forvo_conf['file_path']
yandex_key = conf.main['yandex_key']

db = Db(env_config_file_path)

# to do get from db
words = db.select_words('sentence_word')

db.close_connect()

start_time = time.time()


def run():
    db = Db(env_config_file_path)

    while len(words) > 0:
        p = Forvoparser(limit, file_path=file_path)
        word = words.pop()
        res_list = p.parse(word)

        print(f"word:{word} find:{len(res_list)}")
        print("time: %s seconds ---" % int((time.time() - start_time)))

        if len(res_list) > 0:
            for res in res_list:
                db.add_phrase(res, 'sentence_forvo', 'sentence_word')
        else:
            entity = WordEntity(word)
            db.add_phrase_word(entity, 'sentence_word')

    print("--- %s seconds ---" % (time.time() - start_time))


# -------------- Main process ----------------


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()

now = datetime.datetime.now()
logging.basicConfig(filename=conf.main['log_dir']+'forvo_info.log', level=logging.INFO)
logging.info("time end work:" + str(now)[:19])