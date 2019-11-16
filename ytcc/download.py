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
            'skip_download': True,
            'writeautomaticsub': True,
            'outtmpl': 'subtitle_%(id)s',
            'logger': FakeLogger()
        }
        self.opts.update(opts)

    def all_videos(self, channel_id):
        with youtube_dl.YoutubeDL() as ydl:
            try:
                result = []
                url = "https://www.youtube.com/channel/"+channel_id+"/videos"
                info = ydl.extract_info(url, download=False)

                for item in info["entries"]:
                    result.append(item["id"])
                return result
            except Exception as err:
                raise DownloadException(
                    "Unable to download image: {0}".format(str(err)))

    def update_opts(self, opts: dict) -> None:
        self.opts.update(opts)

    def get_captions(self, video_id: str, allow_empty_ru=False) -> str:
        result = {}
        en_text = self.__parse_caption(video_id, 'en')
        ru_text = self.__parse_caption(video_id, 'ru')

        if en_text == "" or (ru_text == "" and allow_empty_ru !=True):
            return False

        result['en_text'] = en_text
        result['ru_text'] = ru_text
        result['ipa_text'] = self.__convert_to_ipa(en_text)

        info_res = self.parse_info(video_id)

        result.update(info_res)

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

    def __parse_caption(self, video_id: str, langugae : str = 'en') -> str:
        result = self.get_result(video_id, langugae)

        if result != 0:
            return ""

        storage = Storage(video_id, langugae)
        file_path = storage.get_file_path()
        with open(file_path, encoding='UTF8') as f:
            output = self.get_captions_from_output(f.read(), langugae)
        storage.remove_file()

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
                raise DownloadException(
                    "Unable to download image: {0}".format(str(err)))

    def get_result(self, video_id: str, language: str = 'en') -> int:
        opts = self.opts
        if language:
            opts['subtitleslangs'] = [*opts.get('subtitleslangs', []), language]

        with youtube_dl.YoutubeDL(opts) as ydl:
            try:
                return ydl.download([self.get_url_from_video_id(video_id)])
            except youtube_dl.utils.DownloadError as err:
                raise DownloadException(
                    "Unable to download captions: {0}".format(str(err)))
            except youtube_dl.utils.ExtractorError as err:
                raise DownloadException(
                    "Unable to extract captions: {0}".format(str(err)))
            except Exception as err:
                raise DownloadException(
                    "Unknown exception downloading and extracting captions: {0}".format(
                        str(err)))

    def get_url_from_video_id(self, video_id: str) -> str:
        return '{0}?{1}'.format(self.base_url, urlencode({'v': video_id}))

    def get_captions_from_output(self, output: str, language: str = 'en') -> str:
        converter = CaptionConverter()
        converter.read(output, WebVTTReader())
        output = converter.write(SRTWriter())
        return output

    def __convert_to_ipa(self, en_text):
        list_line = en_text.split("\n")

        if len(list_line) > 5:
            result = []
            for key, item in enumerate(list_line[:3]):
                if key == 2:
                    result.append(ipa.convert(item))
                else:
                    result.append(item)

            for key, line in enumerate(list_line):
                if key > 5 and (key - 6) % 4 == 0:
                    result.append(ipa.convert(line))
                elif key > 3:
                    result.append(line)
        return "\n".join(result)


class DownloadException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
