import re

import conf
from lib.db import Db
from ytcc.download import Download

#video_id = 'zD68reVP0Ek'
download = Download()
#download.all_videos("UCcbbZI7w1d9MX5WuxTe3fYA")
# Language is optional and default to "en"
# YouTube uses "en","fr" not "en-US", "fr-FR"
#caption = download.get_captions(video_id, 'en')
#print(caption)

env_config_file_path = conf.main['env_config_file_path']


def run():
    db = Db(env_config_file_path)
    video_ids = db.select_youtube_video(conf.youtube_conf['limit'])
    for video_item in video_ids:
        caption = download.get_captions(video_item['video_id'])
        caption['status'] = 1
        caption['section_id'] = video_item['section_id']

        db.update_or_insert_youtube_table(caption)
    db.connect.close()


run()
