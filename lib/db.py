import pymysql


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

            query_word_phrase_table = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`{word_phrase_table}` (`file_name`, `word`) VALUES (%s, %s);"
            cur.execute(query_word_phrase_table, (entity.file_name, entity.word))

            self.connect.commit()
        except:
            pass
        finally:
            cur.close()

    def add_phrase_word_checked(self, entity, word_phrase_table):
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

    def select_words(self, table):
        cur = self.connect.cursor()
        query = ('SELECT words.name FROM words '
                'LEFT JOIN '+ table +' ON '+table+'.word=words.name '
                'WHERE '+ table +'.word IS NULL AND length(words.name) > 2'
                ' ORDER BY words.name DESC')

        cur.execute(query)

        res = []

        for row in cur:
            res.append(row[0])

        return res