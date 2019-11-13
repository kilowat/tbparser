import datetime
import json
import re
import requests
import logging

from yandex.Translater import Translater

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

    def __init__(self, file_path="./tmp/", log_file_name="log/word_parser.log", yandex_key=""):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        self.word = ""
        self.file_path = file_path
        self.__log_file_name = log_file_name
        self.__yandex_key = yandex_key

    def __word_hunt(self, entity):
        url = "https://wooordhunt.ru/word/" + entity.word
        r = requests.get(url)
        doc = html.fromstring(r.text)
        transcription = doc.xpath('//span[@class="transcription"]')

        if len(transcription) > 0:
            transcription_text = transcription[0].text_content()
            transcription_text = transcription_text.replace('|', '')
            entity.ipa_text = transcription_text

        translate = doc.xpath('//span[@class="t_inline_en"]')

        if len(translate) > 0:
            entity.ru_text = self.__clear_string(translate[0].text_content())

        audio = doc.xpath('//audio[@id="audio_us"]//source')
        if len(audio) > 0:
            entity.file_url = "https://wooordhunt.ru" + audio[0].attrib['src']

    def __reverso_translate(self, entity):
        url = "https://context.reverso.net/translation/english-russian/" + entity.word
        r = requests.get(url, headers=self.__headers)
        doc = html.fromstring(r.text)
        nodes = doc.xpath('//div[@id="translations-content"]//a')

        word_list = []

        for node in nodes:
            word_list.append(self.__clear_string(node.text_content()))

        if len(word_list) > 0:
            entity.ru_text = ", ".join(word_list)

    def parse(self, word):
        self.word = word

        entity = WordEntity(word)

        self.__reverso_translate(entity)

        self.__word_hunt(entity)

        if entity.ipa_text == "":
            entity.ipa_text = ipa.convert(entity.en_text)

        if entity.ru_text == "":
            self.__reverso_translate(entity)

        if entity.ru_text == "":
            entity.ru_text = self.__yandex_translate(entity)

        if entity.file_url == "":
            self.__dict_file_download(entity)

        if entity.file_url == "":
            self.__tureng_file_download(entity)

        if entity.file_url:
            self.__save_file(entity)

        return entity

    def __save_file(self, entity):
        r = requests.get(entity.file_url)
        header = r.headers
        content_length = header.get('content-length', 0)

        if content_length:
            name = entity.word.replace(" ", "_")
            name = name.replace("-", "_")
            entity.file_name = name
            open(self.file_path + name, 'wb').write(r.content)

    def __yandex_translate(self, entity):
        tr = Translater()
        tr.set_key(self.__yandex_key)
        tr.set_from_lang("en")
        tr.set_to_lang("ru")
        tr.set_text(entity.word)
        text = tr.translate()

        return text

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

    def __dict_file_download(self, entity):
        url = "https://www.dictionary.com/browse/" + entity.word

        r = requests.get(url, headers=self.__headers)
        doc = html.fromstring(r.text)

        nodeAudio = doc.xpath('//audio//source[2]')
        check_text = doc.xpath('//h1//text()')

        if len(check_text) > 0 and len(nodeAudio) > 0:
            check_text = check_text[0].replace(" ", "-")
            if check_text == entity.word:
                entity.file_url = nodeAudio[0].attrib['src']

    def __tureng_file_download(self, entity):
        url = "https://tureng.com/en/turkish-english/" + entity.word
        r = requests.get(url, headers=self.__headers)
        doc = html.fromstring(r.text)

        node = doc.xpath("//audio[@id='turengVoiceENTRENus']//source")
        if(len(node) > 0):
            file_path = "https:" + node[0].attrib['src']
            entity.file_url = file_path
