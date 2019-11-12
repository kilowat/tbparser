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
file_path = conf.tb_conf['file_path']

db = Db(env_config_file_path)

# to do get from db
words = ["run"]

db.close_connect()

start_time = time.time()


def run():
    db = Db(env_config_file_path)

    while len(words) > 0:
        p = WordParser(file_path=file_path)
        word = words.pop()
        res = p.parse(word)
        print(f"word:{word} finded")
        print("time: %s seconds ---" % int((time.time() - start_time)))

        if res is not None:
            pass
            #db.add_phrase(res, 'phrases', 'phrases_word')
        else:
            entity = WordEntity(word)
            #db.add_phrase_word_checked(entity, 'phrases_word')

    print("--- %s seconds ---" % (time.time() - start_time))


# -------------- Main process ----------------


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()

now = datetime.datetime.now()
logging.basicConfig(filename='log/word_parse_info.log', level=logging.INFO)
logging.info("time end work:" + str(now)[:19])