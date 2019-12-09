import re

import lib.eng_to_ipa as ipa




f = open('C:\\work_dir\\programm\\tech_dict\\ipa.txt', 'w', encoding="utf-8")
with open('C:\\work_dir\\programm\\tech_dict\\words.txt') as my_file:
    for line in my_file:
        s = re.sub('[^A-Za-z0-9-А-Яа-я  !,?.ё\'"]+', '', line)
        w = ipa.convert(s)

        if '*' in w:
            w = ""

        f.write("%s\n" % w)
