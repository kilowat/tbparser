import datetime

from lib.db import Db
from lib.synonymParser import SynonymParser
import time
import threading
import conf
import logging


from lib.word_entity import WordEntity


thread_count = conf.main['thread_count']
env_config_file_path = conf.main['env_config_file_path']
file_path = conf.forvo_conf['file_path']

db = Db(env_config_file_path)

# to do get from db
words = db.select_words("synonyms")
#words = ['run','traveling']

db.close_connect()

start_time = time.time()


def run():
    db = Db(env_config_file_path)

    while len(words) > 0:
        time.sleep(conf.main['sleep'])
        p = SynonymParser()
        word = words.pop()
        res_list = p.parse(word)

        for res in res_list:
            synonym = res.en_text

            db.add_synonyms(word, synonym)

            if synonym:
                db.add_word(synonym)

        print(f"word:{word.encode('ascii', 'ignore').decode('ascii')} find:{len(res_list)}")
        print("time: %s seconds ---" % int((time.time() - start_time)))

    print("--- %s seconds ---" % (time.time() - start_time))


# -------------- Main process ----------------


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()

now = datetime.datetime.now()
logging.basicConfig(filename=conf.main['log_dir']+'forvo_synonym_info.log', level=logging.INFO)
logging.info("time end work:" + str(now)[:19])