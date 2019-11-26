import time

import pymysql

from lib.word_entity import WordEntity


class Db:
    def __init__(self, conf):
        self.__conf = self.__get_env(conf)
        self.connect = pymysql.connect(
            host=self.__conf['DB_HOST'],
            port=int(self.__conf['DB_PORT']),
            user=self.__conf['DB_USERNAME'],
            passwd=self.__conf['DB_PASSWORD'],
            db=self.__conf['DB_DATABASE'])
        self.__table_phrases_name = "phrases"

    def __get_env(self, env_config_file_path):
        env_config = {}
        f = open(env_config_file_path)
        read_file = f.read()
        read_file = read_file.splitlines()

        for i in read_file:
            sp = i.split("=")
            if len(sp) > 1:
                env_config[sp[0]] = sp[1]
        return env_config

    def add_phrase(self, entity, phrase_table, word_phrase_table):
        try:
            cur = self.connect.cursor()
            query_phrase_table = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`{phrase_table}` (`file_name`, `en_text`, `ipa_text`,`ru_text`) VALUES (%s, %s, %s, %s);"

            cur.execute(query_phrase_table, (entity.file_name, entity.en_text, entity.ipa_text, entity.ru_text))
            self.connect.commit()
        except Exception as err:
            pass
        finally:
            self.add_phrase_word(entity, word_phrase_table)

# add to relations table file_name -> word
    def add_phrase_word(self, entity, word_phrase_table):
        if (self.__is_added_phrase_word(entity, word_phrase_table)) == 0:
            try:
                cur = self.connect.cursor()
                query_word_phrase_table = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`{word_phrase_table}` (`file_name`, `word`) VALUES (%s, %s);"
                cur.execute(query_word_phrase_table, (entity.file_name, entity.word))

                self.connect.commit()
            except Exception as err:
                print("error: {0}".format(err))
            finally:
                cur.close()

    def close_connect(self):
        self.connect.close()

    def __is_added_phrase_word(self, entity, word_phrase_table):
        res = 0
        try:
            cur = self.connect.cursor()
            query = f"SELECT COUNT(*) as COUNT FROM `{self.__conf['DB_DATABASE']}`.`{word_phrase_table}` WHERE `file_name`=%s AND `word`=%s"
            cur.execute(query, (entity.file_name, entity.word))

            for row in cur:
                res = row[0]
        except Exception as err:
            print("error: {0}".format(err))
        finally:
            cur.close()
            return res

    def select_words_to_translate(self, limit=1000):
        cur = self.connect.cursor()

        query = ('SELECT words.name, words.transcription, words.translate, audio.file_name FROM words '
            'LEFT JOIN audio ON audio.word_code=LOWER(words.name)' 
            'WHERE (translate="" OR transcription="" OR file_name=NULL) AND LENGTH(words.name) > 2 '
            ' ORDER BY RAND() LIMIT ' + str(limit))

        cur.execute(query)

        res = []
        for row in cur:
            entity = WordEntity(row[0])
            entity.en_text = row[0]
            entity.ipa_text = row[1]
            entity.ru_text = row[2]
            entity.file_name = row[3]
            res.append(entity)

        return res

    def select_words(self, table, limit=1000):
        cur = self.connect.cursor()
        query = ('SELECT words.name FROM words '
                'LEFT JOIN '+ table +' ON '+table+'.word=words.name '
                'WHERE '+ table +'.word IS NULL AND length(words.name) > 2'
                ' ORDER BY words.name DESC LIMIT ' + str(limit))

        cur.execute(query)

        res = []

        for row in cur:
            res.append(row[0])

        return res

    def select_example_words(self, table="examples", limit=1000):
        cur = self.connect.cursor()
        query = ('SELECT words.id, words.name FROM words '
                'LEFT JOIN '+ table +' ON '+table+'.word_id=words.id '
                'WHERE '+ table +'.word_id IS NULL AND length(words.name) > 2'
                ' ORDER BY words.name DESC LIMIT ' + str(limit))

        cur.execute(query)

        res = []

        for row in cur:
            res.append({
                'id': row[0],
                'name': row[1]
            })

        return res

    def update_word_table(self, entity):
        try:
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            cur = self.connect.cursor()
            query_word = f"UPDATE {self.__conf['DB_DATABASE']}.words SET transcription=%s, translate=%s, updated_at=%s WHERE `name`=%s"
            cur.execute(query_word, (entity.ipa_text, entity.ru_text, time_now, entity.word))

            self.connect.commit()
        except Exception as err:
            print("error: {0}".format(err))
        finally:
            if entity.file_name != "" or entity.file_name is not None:
             self.__update_audio_table(entity)
            cur.close()

    def __update_audio_table(self, entity):
        try:
            query_ = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`audio` (`word_code`, `file_name`, `mime`, `size`, `created_at`, `updated_at`) VALUES (%s, %s, %s, %s, %s, %s);"
            cur = self.connect.cursor()
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(query_, (entity.word, entity.file_name, 'audio/mpeg', entity.file_size, time_now, time_now))
            self.connect.commit()
        except Exception as err:
            print("update audio table:")
            print("error: {0}".format(err))

    def update_or_insert_youtube_table(self, data):
        if self.__is_added_youtube_table(data):
            return self.__update_youtube_table(data)
        else:
            return self.__insert_youtube_table(data)

    def __insert_youtube_table(self, data):
        result = True

        try:
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            cur = self.connect.cursor()
            query = (f"INSERT INTO "
                                       f"`{self.__conf['DB_DATABASE']}`.`youtube` "
                                       f"(`code`, "
                                       f"`en_text`, "
                                       f"`ru_text`, "
                                       f"`ipa_text`, `"
                                       f"picture`, "
                                       f"`title`, "
                                       f"`description`, "
                                       f"`section_id`, "
                                       f"`status`, "
                                       f"`created_at`, "
                                       f"`updated_at`) "
                                       f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
            cur.execute(query,(
                        data['code'],
                        data['en_text'],
                        data['ru_text'],
                        data['ipa_text'],
                        data['thumbnail'],
                        data['title'],
                        data['description'],
                        data['section_id'],
                        data['status'],
                        time_now,
                        time_now))
            self.connect.commit()
        except Exception as err:
            print("Error insert to youtube table: {0}".format(str(err)))
            result = False
        finally:
            cur.close()
            return result

    def __is_added_youtube_table(self, data):
        res = 0
        try:
            cur = self.connect.cursor()
            query = "SELECT COUNT(*) as count FROM `youtube` WHERE code=%s"
            cur.execute(query, data['code'])

            for row in cur:
                res = row[0]

        except Exception as err:
            print("Error select count from youtube table: {0}".format(str(err)))
        finally:
            cur.close()
            return res > 0

    def __update_youtube_table(self, data):
        result = True

        try:
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            cur = self.connect.cursor()
            query = (f"UPDATE `{self.__conf['DB_DATABASE']}`.`youtube` "
                     f"SET en_text=%s, "
                     f"ru_text=%s, "
                     f"ipa_text=%s, "
                     f"picture=%s, "
                     f"title=%s, "
                     f"description=%s, "
                     f"section_id=%s, "
                     f"status=%s, "
                     f"created_at=%s, "
                     f"updated_at=%s "
                     f"WHERE `code`=%s")

            cur.execute(query, (
                data['en_text'],
                data['ru_text'],
                data['ipa_text'],
                data['thumbnail'],
                data['title'],
                data['description'],
                data['section_id'],
                data['status'],
                time_now,
                time_now,
                data['code']))
            self.connect.commit()

        except Exception as err:
            result = False
            print("Error update to youtube table: {0}".format(str(err)))
        finally:
            cur.close()
            return result

    def select_youtube_video(self, limit):
        cur = self.connect.cursor()
        query = ('SELECT code, section_id FROM ' + self.__conf['DB_DATABASE']+'.`youtube` '
                'WHERE status=0 '
                'ORDER BY created_at ASC LIMIT ' + str(limit))

        cur.execute(query)

        res = []

        for row in cur:
            res.append({'video_id': row[0], 'section_id': row[1]})

        return res

    def select_youtube_channel(self, limit=1):
        cur = self.connect.cursor()
        query = ('SELECT code, section_id FROM ' + self.__conf['DB_DATABASE']+'.`youtube_channels` '
                'WHERE status=0 '
                'ORDER BY created_at ASC LIMIT ' + str(limit))

        cur.execute(query)

        res = []

        for row in cur:
            res.append({'code': row[0], 'section_id': row[1]})

        return res

    def update_youtube_channel_table(self, data):
        try:
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            cur = self.connect.cursor()
            query = (f"UPDATE `{self.__conf['DB_DATABASE']}`.`youtube_channels` "
                     f"SET status=%s, "
                     f"video_count=%s, "
                     f"updated_at=%s "
                     f"WHERE `code`=%s")

            cur.execute(query, (
                data['status'],
                data['video_count'],
                time_now,
                data['code']))
            self.connect.commit()
        except Exception as err:
            print("Error update to youtube table: {0}".format(str(err)))
        finally:
            cur.close()

    def select_forvo_phrases(self, limit = 1000):
        res = []

        try:
            cur = self.connect.cursor()
            query = f"SELECT file_name, en_text FROM `{self.__conf['DB_DATABASE']}`.`sentence_forvo` WHERE ru_text='' and file_name !=''  LIMIT " + str(limit)
            cur.execute(query)

            for row in cur:
                res.append({'file_name': row[0], 'en_text': row[1]})
        except Exception as err:
            print("Error select from forvo table: {0}".format(str(err)))
        finally:
            cur.close()
            return res

    def update_forvo_ru_text(self, file_name, ru_text):
        try:
            cur = self.connect.cursor()
            query = (f"UPDATE `{self.__conf['DB_DATABASE']}`.`sentence_forvo` "
                     f"SET ru_text=%s "
                     f"WHERE file_name=%s")
            cur.execute(query, (
                ru_text,
                file_name))
            self.connect.commit()
        except Exception as err:
            print("Error update sentecne_frovo table: {0}".format(str(err)))
        finally:
            cur.close()

    def add_example(self, word, json_text, word_id):
        try:
            cur = self.connect.cursor()
            query = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`examples` (`word`, `word_id`,`json_text`) VALUES (%s, %s, %s);"

            cur.execute(query, (word, word_id, json_text))

            self.connect.commit()
        except Exception as err:
            print("error: {0}".format(err))
        finally:
            cur.close()