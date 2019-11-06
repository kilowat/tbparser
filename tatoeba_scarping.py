from lib.db import Db
from lib.parser import Parser
import time
import threading

from lib.word_entity import WordEntity

limit = 200  # max download file every word

thread_count = 4  # numbers how match start the threads
env_config_file_path = "C:\\work_dir\\webserver_5_5\\OSPanel\domains\\true-english.ru\\.env"
file_path = "C:\\work_dir\\webserver_5_5\\OSPanel\\domains\\true-english.ru\\storage\\app\public\\phrases\\"
db = Db(env_config_file_path)

# to do get from db
words = db.select_words()
db.close_connect()

start_time = time.time()


def run():
    db = Db(env_config_file_path)
    while len(words) > 0:
        p = Parser(limit, file_path=file_path)
        word = words.pop()
        res_list = p.parse(word)

        print(f"word:{word} find:{len(res_list)}")
        print("time: %s seconds ---" % int((time.time() - start_time)))

        if len(res_list) > 0:
            for res in res_list:
                db.add(res)
        else:
            entity = WordEntity(word)
            db.add(entity)

    print("--- %s seconds ---" % (time.time() - start_time))

# -------------- Main process ----------------


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()
