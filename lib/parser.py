import datetime
import json
import re
import requests
import logging
import lib.eng_to_ipa as ipa
from lxml import html
from .word_entity import WordEntity


class Parser:
    """
    parser tatoeba.org
    :param limit: limit download elements
    :type limit: int
    :param file_path: path to save downloaded files
    """

    def __init__(self, limit=100, file_path="./tmp/", log_file_name="log/tb_parser.log"):
        self.word = ""
        self.ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
        self.en_text_query = 'div//div[@class="sentence "]//div[@class="text"]'
        self.audio_query = 'div//div[@class="sentence "]/md-button'
        self.next_page_query = '.paging'
        self.file_path = file_path
        self.doc = ''
        self.page = 1
        self.limit = limit
        self.__downloaded = 0
        self.__log_file_name = log_file_name

    def __get_url(self):
        return "https://tatoeba.org/eng/sentences/search?query=" + self.word + "&from=eng&to=rus&orphans=no&unapproved=no&user=&tags=&list=&has_audio=yes&trans_filter=limit&trans_to=rus&trans_link=&trans_user=&trans_orphan=&trans_unapproved=&trans_has_audio=&sort=relevance&page=" + str(
            self.page)

    def parse(self, word):
        self.word = word

        result = []

        self.__run_chunk(word, result)

        return result

    def __run_chunk(self, word, result):
        r = requests.get(self.__get_url())
        self.doc = html.fromstring(r.text)

        items = self.doc.cssselect('.sentence-and-translations')

        for item in items:
            entity = WordEntity(word)
            entity.en_text = self.__get_en_text(item)
            entity.ipa_text = ipa.convert(entity.en_text)
            entity.ru_text = self.__get_ru_text(item)
            entity.file_url = self.__get_file_url(item)
            entity.file_name = self.__get_file(entity)

            if self.__downloaded > self.limit:
                break

            result.append(entity)

            self.__downloaded += 1

        next_page = self.__get_next_page()

        # recurse
        if next_page > 0 and self.__downloaded < self.limit:
            self.page = next_page
            self.__run_chunk(word, result)

        self.__downloaded = 0

    def __get_file(self, entity):
        r = requests.get(entity.file_url)
        name = ""
        header = r.headers
        content_length = header.get('content-length', 0)

        if content_length:
            name = self.__make_file_name(entity.file_url)
            open(self.file_path + name, 'wb').write(r.content)

        return name

    def __get_en_text(self, item):
        query_node = item.find(self.en_text_query)

        if query_node is not None:
            text = query_node.text_content()

            return self.__clear_string(text)
        else:
            self.__error_log(self.en_text_query)

    def __get_ru_text(self, item):
        ru_text_list = []
        nodes = item.findall(self.ru_text_query)

        if len(nodes) == 0:
            self.__error_log(self.ru_text_query)
            return ""

        for ru_item in nodes:
            text = self.__clear_string(ru_item.text_content())
            ru_text_list.append(text)

        return "|".join(ru_text_list)

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

    def __get_next_page(self):
        nodes = self.doc.cssselect(self.next_page_query)
        next = -1

        if len(nodes) > 0:
            next_a = nodes[0].find('li[@class="active"]').getnext().find('a')
            if next_a is not None and next_a.text_content().isdigit():
                next = int(next_a.text_content())

        return next

    def __error_log(self, text):
        pass
        #now = datetime.datetime.now()
        #logging.basicConfig(filename=self.__log_file_name, level=logging.INFO)
        #msg = str(now)[:19] +" word:" + self.word + " Element not find query:" + text
        #logging.info(msg)

    def __make_file_name(self, file_url):
        res = file_url.replace('https://', '')
        res = res.replace("/", "_")
        return res
