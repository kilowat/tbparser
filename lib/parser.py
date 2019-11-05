import json
import re
import random
import string
import requests
from lxml import html
from .word_entity import WordEntity


class Parser:
    def __init__(self, word, file_path="./tmp/"):
        self.word = word
        self.ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
        self.en_text_query = 'div//div[@class="sentence "]//div[@class="text"]'
        self.audio_query = 'div//div[@class="sentence "]/md-button'
        self.file_path = file_path
        self.page = 1

    def __get_url(self):
        return "https://tatoeba.org/eng/sentences/search?query=" + self.word + "&from=eng&to=rus&orphans=no&unapproved=no&user=&tags=&list=&has_audio=yes&trans_filter=limit&trans_to=rus&trans_link=&trans_user=&trans_orphan=&trans_unapproved=&trans_has_audio=&sort=relevance&page=" + str(
            self.page)

    def parse(self):
        result = []
        r = requests.get(self.__get_url())
        doc = html.fromstring(r.text)

        items = doc.cssselect('.sentence-and-translations')

        for item in items:
            entity = WordEntity("run")
            entity.en_text   = self.__get_en_text(item)

            entity.ru_text   = self.__get_ru_text(item)
            entity.file_url  = self.__get_file_url(item)
            entity.file_name = self.__get_file(entity)

            result.append(entity)

        return result

    def __get_file(self, entity):
        r = requests.get(entity.file_url)
        name = ""

        header = r.headers

        content_length = header.get('content-length', 0)

        if content_length:
            name = self.__random_string() + ".mp3"

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

        for ru_item in nodes:
            text = self.__clear_string(ru_item.text_content())
            ru_text_list.append(text)

        return json.dumps(ru_text_list)

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

    def __random_string(self, stringLength=30):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase

        return ''.join(random.choice(letters) for i in range(stringLength))

    def __clear_string(self, str):
        text_tmp = re.sub('[^A-Za-z0-9-А-Яа-я  !,?]+', '', str)
        text_tmp = re.sub(' +', ' ', text_tmp)
        text_tmp = text_tmp.strip()

        return text_tmp

    def __error_log(self, text):
        pass

