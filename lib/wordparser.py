import datetime
import json
import re
import requests
import logging
import lib.eng_to_ipa as ipa
from lxml import html
from .word_entity import WordEntity


class WordParser:
    """
    parser tatoeba.org
    :param limit: limit download elements
    :type limit: int
    :param file_path: path to save downloaded files
    """

    def __init__(self, file_path="./tmp/", log_file_name="log/word_parser.log"):
        self.word = ""
        self.ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
        self.file_path = file_path
        self.__log_file_name = log_file_name
        self.doc = ''

    def __get_url(self):
        return "https://tatoeba.org/eng/sentences/search?query=" + self.word + "&from=eng&to=rus&orphans=no&unapproved=no&user=&tags=&list=&has_audio=yes&trans_filter=limit&trans_to=rus&trans_link=&trans_user=&trans_orphan=&trans_unapproved=&trans_has_audio=&sort=relevance&page=" + str(
            self.page)

    def parse(self, word):
        self.word = word

        result = []

        return result

    def __get_file(self, entity):
        r = requests.get(entity.file_url)
        name = ""
        header = r.headers
        content_length = header.get('content-length', 0)

        if content_length:
            name = self.__make_file_name(entity.file_url)
            open(self.file_path + name, 'wb').write(r.content)

        return name

    def __get_ru_text(self, item):
        pass

    def __get_file_url(self, item):
        node = item.find(self.audio_query)
        url_text = ""

        if node is not None:
            attrs = node.attrib
            if attrs['ng-click'] is not None:
                url_text = attrs['ng-click']
                url_text = url_text.replace("vm.playAudio('", "")
                url_text = url_text.replace("')", "")
        else:
            self.__error_log(self.audio_query)

        return url_text

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

    def __make_file_name(self, file_url):
        res = file_url.replace('https://', '')
        res = res.replace("/", "_")
        return res
