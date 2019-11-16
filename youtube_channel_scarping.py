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
        for video_item in video_list:
            data = video_item
            data['ent_text'] = ""
            data['ru_text'] = ""
            data['ipa_text'] = ""
            data['picture'] = ""
            data['title'] = ""
            data['description'] = ""
            data['status'] = 0
            db.update_or_insert_youtube_table(data)

        channel_item['status'] = 1
        db.update_youtube_channel_table(channel_item)
    db.connect.close()


run()

