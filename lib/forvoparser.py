import datetime
import json
import re
import requests
import logging
import lib.eng_to_ipa as ipa
from lxml import html
from .word_entity import WordEntity
from yandex.Translater import Translater


class Forvoparser:

    def __init__(self, limit=100, file_path="./tmp/", log_file_name="log/forvo_parser.log", yandex_key=""):
        self.word = ""
        self.ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
        self.en_text_query = 'a[@class="word"]'
        self.audio_query = 'span'
        self.next_page_query = '//nav[@class="pagination"]//ol//li'
        self.file_path = file_path
        self.page = 1
        self.limit = limit
        self.__downloaded = 0
        self.__log_file_name = log_file_name
        self.yandex_key = yandex_key
        self.__headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'}

    def __get_url(self):
        if self.page < 2:
            return "https://forvo.com/search/" + self.word + "/en/"
        else:
            return "https://forvo.com/search/" + self.word + "/en/page-" + str(self.page)

    def parse(self, word):
        self.word = word

        result = []

        self.__run_chunk(word, result)

        return result

    def __run_chunk(self, word, result):
        my_session = requests.session()
        for_cookies = my_session.get("https://forvo.com")
        cookies = for_cookies.cookies
        r = my_session.get(self.__get_url(), headers=self.__headers, cookies=cookies)
        self.doc = html.fromstring(r.text)

        if r.status_code != 200:
            self.__error_log('forvo parser error ' + str(r.status_code))
            raise Exception('forvo parser error ' + str(r.status_code))

        items = self.doc.cssselect('.list-phrases ul li')

        for item in items:
            entity = WordEntity(word)
            entity.en_text = self.__get_en_text(item)
            entity.ipa_text = ipa.convert(entity.en_text)
            entity.ru_text = self.__get_ru_text(entity)
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

    def __get_ru_text(self, entity):
        text = ""
        #tr = Translater()
        #tr.set_key(self.yandex_key)
        #tr.set_from_lang("en")
        #tr.set_to_lang("ru")
        #tr.set_text(entity.en_text)
        #text = tr.translate()

        return text

    def __get_file_url(self, item):
        url = 'https://forvo.com/player-phrasesMp3Handler.php?path='
        node = item.find(self.audio_query)
        url_text = ""
        if node is not None:
            attrs = node.attrib
            if attrs['onclick'] is not None:
                url_text = attrs['onclick']
                url_text = url_text.replace("PlayPhrase(", "")
                url_text = url_text.replace("')", "")
                url_text = url_text.replace("'", "")
                url_s = url_text.split(',')
                try:
                    id = url_s[1]
                    url_text = url + id
                except KeyError:
                    pass
        else:
            self.__error_log(self.audio_query)
        return url_text

    def __clear_string(self, str):
        text_tmp = re.sub('[^A-Za-z0-9-А-Яа-я  !,?.ё\'"]+', '', str)
        text_tmp = re.sub(' +', ' ', text_tmp)
        text_tmp = text_tmp.strip()

        return text_tmp

    def __get_next_page(self):
        next = -1
        nodes = self.doc.xpath(self.next_page_query)
        try:
            node = nodes[self.page]
            next_li = node.getnext()
            if next_li is not None and next_li.text_content().isdigit():
                next = int(next_li.text_content())
            return next
        except IndexError:
            return 0

    def __error_log(self, text):
        pass
        now = datetime.datetime.now()
        logging.basicConfig(filename=self.__log_file_name, level=logging.INFO)
        msg = str(now)[:19] + " word:" + self.word + " Element not find query:" + text
        logging.info(msg)

    def __make_file_name(self, file_url):
        res = file_url.replace("https://forvo.com/player-phrasesMp3Handler.php?path=", "")
        res = res + ".mp3"
        return res
