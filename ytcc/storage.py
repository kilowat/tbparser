# -*- coding: UTF-8 -*-
import glob
import re
import os


class Storage():

    def __init__(self, video_id: str, language: str = 'en') -> None:
        self.video_id = video_id
        self.language = language

    def get_file_path(self, s_format='vtt') -> str:
        if re.search(r'[^\w-]', self.video_id):
            raise ValueError(
                'Invalid video id attempting to write to filesystem')

        return './tmp/subtitle_{0}.{1}.{2}'.format(
            re.sub(r'[^\w-]', '', self.video_id), self.language, s_format)

    def remove_file(self, s_format='vtt') -> None:
        os.remove(self.get_file_path(s_format))

    @staticmethod
    def remove_all_tmp_files():
        files = glob.glob('./tmp/*')
        for f in files:
            os.remove(f)
