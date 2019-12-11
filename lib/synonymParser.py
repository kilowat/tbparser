import datetime
import json
import re
import requests
import logging
import lib.eng_to_ipa as ipa
from lxml import html
from .word_entity import WordEntity
from yandex.Translater import Translater


class SynonymParser:

    def __init__(self, log_file_name="log/forvo_synonym_parser.log"):
        self.word = ""
        self.ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
        self.en_text_query = 'a'
        self.__log_file_name = log_file_name
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'}

    def __get_url(self):
            return "https://www.merriam-webster.com/dictionary/"+self.word
            #return "https://forvo.com/word/"+self.word+"/#en"

    def parse(self, word):
        self.word = word

        result = []

        r = requests.get(self.__get_url(), headers=self.__headers)
        self.doc = html.fromstring(r.text)

        if r.status_code == 403:
            self.__error_log('synonym parser error ' + str(r.status_code))
            raise Exception('synonym parser error ' + str(r.status_code))

        self.doc = html.fromstring(r.text)

        items = self.doc.cssselect('.synonyms_list li')

        for item in items:
            entity = WordEntity(word)
            entity.en_text = self.__get_en_text(item)

            result.append(entity)

        return result

    def __get_en_text(self, item):
        query_node = item.find(self.en_text_query)

        if query_node is not None:
            text = query_node.text_content()
            return self.__clear_string(text)
        else:
            self.__error_log(self.en_text_query)


    def __clear_string(self, str):
        text_tmp = re.sub('[^A-Za-z0-9-А-Яа-я  !,?.ё\'"]+', '', str)
        text_tmp = re.sub(' +', ' ', text_tmp)
        text_tmp = text_tmp.strip()

        return text_tmp

    def __error_log(self, text):
        pass
        now = datetime.datetime.now()
        logging.basicConfig(filename=self.__log_file_name, level=logging.INFO)
        msg = str(now)[:19] + " word:" + self.word + " Element not find query:" + text
        logging.info(msg)

