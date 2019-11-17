import conf
from lib.db import Db
from ytcc.download import Download

download = Download()

env_config_file_path = conf.main['env_config_file_path']


def run():
    db = Db(env_config_file_path)
    channels_list = db.select_youtube_channel()

    for channel_item in channels_list:
        video_list = download.all_videos(channel_item['code'])

        count = 0

        for video_item in video_list:
            data = {'code': video_item, 'section_id': channel_item['section_id'], 'en_text': "", 'ru_text': "", 'ipa_text': "", 'thumbnail': "", 'title': "",
                    'description': "", 'status': 0}

            if db.update_or_insert_youtube_table(data):
                count += 1

        channel_item['status'] = 1
        channel_item['video_count'] = count
        db.update_youtube_channel_table(channel_item)

    db.connect.close()


run()

