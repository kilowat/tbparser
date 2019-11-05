import json
import re
import random
import string
import requests
from lxml import html

from word_entity import WordEntity

ru_text_query = 'div[@class="direct translations"]//div[@class="text"]'
en_text_query = 'div//div[@class="sentence "]//div[@class="text"]'
audio_query = 'div//div[@class="sentence "]/md-button'

file_path = "./"


def parse(url):

    result = []

    r = requests.get(url)
    doc = html.fromstring(r.text)
    items = doc.cssselect('.sentence-and-translations')

    for item in items:
        entity = WordEntity("run")
        entity.en_text = get_en_text(item)
        entity.ru_text = get_ru_text(item)
        entity.file_url = get_file_url(item)
        entity.file_name = get_file(entity)
        result.append(entity)

    return result


def get_file(entity):
    r = requests.get(entity.file_url)
    print(r)

    header = r.headers

    content_length = header.get('content-length', 0)

    if content_length:
        name = entity.word + "_"+random_string() + ".mp3"
        print(name)
        open(file_path + name, 'wb').write(r.content)


def get_en_text(item):
    query_node = item.find(en_text_query)

    if query_node is not None:
        text = query_node.text_content()

        return clear_string(text)
    else:
        error_log(en_text_query + " node not find")


def get_ru_text(item):
    ru_text_list = []
    nodes = item.findall(ru_text_query)

    if len(nodes) == 0:
        error_log(ru_text_query)

    for ru_item in nodes:
        text = clear_string(ru_item.text_content())
        ru_text_list.append(text)

    return json.dumps(ru_text_list)


def get_file_url(item):
    node = item.find(audio_query)

    url_text = ""

    if node is not None:
        attrs = node.attrib
        if attrs['ng-click'] is not None:
            url_text = attrs['ng-click']
            url_text = url_text.replace("vm.playAudio('", "")
            url_text = url_text.replace("')", "")
    else:
        error_log(audio_query)

    return url_text


def random_string(stringLength=30):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for i in range(stringLength))


def clear_string(str):

    text_tmp = re.sub('[^A-Za-z0-9-А-Яа-я  !,?]+', '', str)
    text_tmp = re.sub(' +', ' ', text_tmp)
    text_tmp = text_tmp.strip()

    return text_tmp


def error_log(text):
    pass

url = "https://tatoeba.org/eng/sentences/search?query=run&from=eng&to=rus&orphans=no&unapproved=no&user=&tags=&list=&has_audio=yes&trans_filter=limit&trans_to=rus&trans_link=&trans_user=&trans_orphan=&trans_unapproved=&trans_has_audio=&sort=relevance"

items_res = parse(url)

for i in items_res:
    print(i.en_text)
    print(i.ru_text)
    print(i.file_url)
