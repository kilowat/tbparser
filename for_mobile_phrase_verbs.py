import datetime
import json

from lib.db import Db
import time
import threading
import conf
import logging


from lib.word_entity import WordEntity
from lib.wordhunparser import WordHunParser

from xlrd import open_workbook

wb = open_workbook('D:\\other\\pv.xlsx')
words = []
for s in wb.sheets():
    #print 'Sheet:',s.name
    for row in range(1, s.nrows):
        col_names = s.row(0)
        col_value = []
        for name, col in zip(col_names, range(s.ncols)):
            value  = (s.cell(row,col).value)
            try : value = str(int(value))
            except : pass
            col_value.append(value)
        words.append(col_value)
#print (words)

#words = [words[0]]
env_config_file_path = conf.main['env_config_file_path']

db = Db(env_config_file_path)

for word in words:
    p = WordHunParser()
    example = p.parse(word[0])
    json_example = json.dumps(example)
    if example:
        try:
            db.add_f_verb(en_text=word[0], ru_text=word[1], ip_text=word[2], json_example=json_example)
        except: pass
    print(example)



# thread_count = conf.main['thread_count']
# env_config_file_path = conf.main['env_config_file_path']
#
# db = Db(env_config_file_path)
#
# # to do get from db
# words = db.select_example_words(limit=conf.tb_conf['word_limit'])
#
# db.close_connect()
#
# start_time = time.time()
#
# def run():
#     db = Db(env_config_file_path)
#
#     while len(words) > 0:
#         p = WordHunParser()
#         word = words.pop()
#         res = p.parse(word['name'])
#         db.add_example(word=word['name'], json_text=json.dumps(res), word_id=word['id'])
#         print(f"word:{word} find:{len(res)}")
#         print("time: %s seconds ---" % int((time.time() - start_time)))
#
#
#     print("--- %s seconds ---" % (time.time() - start_time))
#
#
# # -------------- Main process ----------------
#
#
# threads = []
#
# for i in range(thread_count):
#     t = threading.Thread(target=run)
#     threads.append(t)
#     t.start()
#
# now = datetime.datetime.now()
# logging.basicConfig(filename=conf.main['log_dir'] + 'word_hunt_info.log', level=logging.INFO)
# logging.info("time end work:" + str(now)[:19])