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

    def add(self, entity_list):
        self.__insert_only_new(entity_list)

    def __insert_only_new(self, entity):
        if not self.__is_inserted(entity):
            self.__insert(entity)

    def __is_inserted(self, entity):
        count = False

        if not entity.file_name:
            return False

        cur = self.connect.cursor()
        query = f"SELECT count(*) FROM {self.__table_phrases_name} WHERE file_name='{entity.file_name}'"
        cur.execute(query)
        res = cur.fetchone()

        if len(res) > 0:
            count = res[0] > 0

        cur.close()

        return count

    def __insert(self, entity):
        cur = self.connect.cursor()

        query = f"INSERT INTO `{self.__conf['DB_DATABASE']}`.`{self.__table_phrases_name}` (`word`, `file_name`, `en_text`, `ru_text`) VALUES ('{entity.word}', '{entity.file_name}', '{entity.en_text}', '{entity.ru_text}');"
        cur.execute(query)
        cur.close()

    def close_connect(self):
        self.connect.close()


    def select_words(self):
        cur = self.connect.cursor()
        query = ('SELECT words.name FROM words '
                'LEFT JOIN phrases ON phrases.word=words.name '
                'WHERE phrases.word IS NULL AND length(words.name) > 2'
                ' ORDER BY words.name DESC')

        cur.execute(query)

        res = []

        for row in cur:
            res.append(row[0])

        return res