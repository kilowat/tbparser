# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
import youtube_dl
from pycaption import WebVTTReader, CaptionConverter, SRTWriter
import re
from urllib.parse import urlencode
from ytcc.storage import Storage
from ytcc.fake_logger import FakeLogger
import lib.eng_to_ipa as ipa


class Download():
    base_url = 'http://www.youtube.com/watch'

    def __init__(self, opts: dict = {}) -> None:
        self.opts = {
            # 'write-sub': True,
            'skip_download': True,
            # 'writeautomaticsub': True,
            'outtmpl': './tmp/subtitle_%(id)s',
            'logger': FakeLogger()
        }
        self.opts.update(opts)

    def all_videos(self, url):
        with youtube_dl.YoutubeDL({'ignoreerrors': True, 'abort-on-error': False, 'sleep-interval': 90}) as ydl:
            result = []
            try:
                result = []
                info = ydl.extract_info(url, download=False)

                for item in info["entries"]:
                    if item is not None:
                        result.append(item["id"])

            except Exception as err:
                print("Unable to download image: {0}".format(str(err)))
            finally:
                return result

    def update_opts(self, opts: dict) -> None:
        self.opts.update(opts)

    def get_captions(self, video_id: str, allow_empty_ru=False) -> str:
        result = {}
        en_text = self.__parse_caption(video_id, 'en')

        if not en_text:
            return False

        ru_text = self.__parse_caption(video_id, 'ru')

        if ru_text == "" and not allow_empty_ru:
            return False

        #result['en_text'] = self.__clear_sub(en_text)
        #ru_text = self.__clear_sub(ru_text)
        #result['ru_text'] = self.__clear_author(result["en_text"], ru_text)
        #result['ipa_text'] = self.__convert_to_ipa(result['en_text'])

        result['en_text'] = en_text
        result['ru_text'] = ru_text
        result['ipa_text'] = self.__convert_to_ipa(result['en_text'])

        info_res = self.parse_info(video_id)

        result.update(info_res)

        Storage.remove_all_tmp_files()

        return result

    def __clear_sub(self, text):
        if text == False or text == "" or text is None:
            return ""

        result_tmp = []

        tmp_text = text.split("\n\n")

        for item in tmp_text:
            if not re.search("[♪(]", item) \
                    and not re.search("playing]", item) \
                    and not re.search("music]", item) \
                    and not re.search("играет]", item) \
                    and not re.search("музыка]", item):
                result_tmp.append(item)

        result = []

        for line_index, item in enumerate(result_tmp):
            new_line = []
            for key, sub_item in enumerate(item.split("\n")):
                if key > 2:
                    sub_item.replace("\n", "")
                if key == 0:
                    new_line.append(str(line_index + 1))
                else:
                    new_line.append(sub_item)

            result.append("\n".join(new_line))

        return "\n\n".join(result)

    def __clear_author(self, en_text, ru_text):
        if ru_text == False or ru_text == "" or ru_text is None:
            return ""

        result = ""

        en_tmp = en_text.split("\n\n")
        ru_tmp = ru_text.split("\n\n")
        #Перевел или переведено
        if re.search("ерев", ru_tmp[0]):
            if len(en_tmp) < len(ru_tmp):
                ru_tmp = ru_tmp[1:]
                new_ru = []
                for line_index, item in enumerate(ru_tmp):
                    new_line = []
                    for key, sub_item in enumerate(item.split("\n")):
                        if (key == 0):
                            new_line.append(str(line_index + 1))
                        else:
                            new_line.append(sub_item)
                    new_ru.append("\n".join(new_line))

                result = "\n\n".join(new_ru)
            elif len(en_tmp) > len(ru_tmp):
                new_ru = []
                for line_index, item in enumerate(ru_tmp):
                    new_ru.append(item);

                result = "\n\n".join(new_ru)
            else:
                result = ru_text
        else:
            result = ru_text

        return result

    def __clear_description(self, text):
        tmp_str = text.split("\n")
        res = []
        for s in tmp_str:
            if re.search("htt", s) is None:
                s = s.replace('\n', '')
                res.append(s)
        result = "\n".join(res)
        return result

    def __parse_caption(self, video_id: str, langugae: str = 'en') -> str:
        result = self.get_result(video_id, langugae)

        if result != 0:
            return ""

        storage = Storage(video_id, langugae)
        file_path = storage.get_file_path()
        try:
            with open(file_path, encoding='UTF8') as f:
                output = self.get_captions_from_output(f.read(), langugae)
                f.close()
        except Exception as err:
            print("Error file write subtitle: {0}".format(str(err)))
            output = ""
        finally:
            return output

    def parse_info(self, video_id):
        opts = {}
        with youtube_dl.YoutubeDL(opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_id, download=False)

                result = {
                    "code": info_dict.get("id", None),
                    "title": info_dict.get('title', None),
                    "thumbnail": info_dict.get('thumbnail', None),
                    "description": self.__clear_description(info_dict.get('description', None))
                }
                return result

            except Exception as err:
                print("Unable to download image: {0}".format(str(err)))

    def get_result(self, video_id: str, language: str = 'en') -> int:
        opts = self.opts
        if language:
            opts['subtitleslangs'] = [*opts.get('subtitleslangs', []), language]
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = False
        with youtube_dl.YoutubeDL(opts) as ydl:
            try:
                return ydl.download([self.get_url_from_video_id(video_id)])
            except youtube_dl.utils.DownloadError as err:
                print("Unable to download captions: {0}".format(str(err)))
            except youtube_dl.utils.ExtractorError as err:
                print("Unable to extract captions: {0}".format(str(err)))
            except Exception as err:
                print("Unknown exception downloading and extracting captions: {0}".format(str(err)))

    def get_url_from_video_id(self, video_id: str) -> str:
        return '{0}?{1}'.format(self.base_url, urlencode({'v': video_id}))

    def get_captions_from_output(self, output: str, language: str = 'en') -> str:
        converter = CaptionConverter()
        converter.read(output, WebVTTReader())
        output = converter.write(SRTWriter())
        return output

    def __convert_to_ipa(self, en_text):
        list_line = en_text.split("\n\n")
        result = []

        for line in list_line:
            item_in_line = line.split("\n")
            srt_info = item_in_line[:2]
            text = item_in_line[2:]
            new_text_list = []

            for item_text in text:
                new_text_list.append(ipa.convert(item_text))

            new_line = srt_info + new_text_list

            result.append("\n".join(new_line))

        return "\n\n".join(result)


class DownloadException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
