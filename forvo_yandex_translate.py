from lib.db import Db
from yandex.Translater import Translater
import conf

env_config_file_path = conf.main['env_config_file_path']
yandex_key = conf.main['yandex_key']
db = Db(env_config_file_path)

phrases = db.select_forvo_phrases(conf.forvo_conf['translate_limit'])

for phrase in phrases:
     tr = Translater()
     tr.set_key(yandex_key)
     tr.set_from_lang("en")
     tr.set_to_lang("ru")
     tr.set_text(phrase['en_text'])
     ru_text = tr.translate()
     db.update_forvo_ru_text(phrase['file_name'], ru_text)
     print("translated "+phrase['file_name'])