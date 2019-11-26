import datetime
import re
import requests
import logging


import lib.eng_to_ipa as ipa
from lxml import html
from .word_entity import WordEntity


class WordHunParser:

    def __init__(self, file_path="./tmp/", log_file_name="log/word_parser.log", yandex_key=""):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        self.word = ""
        self.file_path = file_path
        self.__log_file_name = log_file_name
        self.__yandex_key = yandex_key

    def parse(self, word):

        url = "https://wooordhunt.ru/word/" + word

        r = requests.get(url)
        doc = html.fromstring(r.text)

        result = self.__fetch_examples(doc)

        return result

    def __fetch_examples(self, doc):
        result = []
        itemsNode = doc.xpath('//div[@id="wd_content"]//div[@class="block"][1]//p')
        ex = []

        for item in itemsNode:
            ex.append(self.__clear_string(item.text_content()))

        chunk_list = list(self.__chunks(ex, 2))

        for chunk in chunk_list:
            if len(chunk) > 1:
                result.append({
                    "en_text": chunk[0],
                    "ru_text": chunk[1],
                    "ipa_text": ipa.convert(chunk[0])
                })

        return result

    def __chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def __clear_string(self, str):
        text_tmp = re.sub('[^A-Za-z0-9-А-Яа-я  !,?.ё\'"]+', '', str)
        text_tmp = re.sub(' +', ' ', text_tmp)
        text_tmp = text_tmp.strip()

        return text_tmp

    def __error_log(self, text):
        pass
        now = datetime.datetime.now()
        logging.basicConfig(filename=self.__log_file_name, level=logging.INFO)
        msg = str(now)[:19] +" word:" + self.word + " Element not find query:" + text
        logging.info(msg)
