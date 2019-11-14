from ytcc.download import Download

video_id = 'zD68reVP0Ek'
download = Download()
# Language is optional and default to "en"
# YouTube uses "en","fr" not "en-US", "fr-FR"
captions = download.get_captions(video_id, 'en')
print(captions)