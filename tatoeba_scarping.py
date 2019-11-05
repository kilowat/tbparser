from lib.parser import Parser

word = "run"

p = Parser(word)

items_res = p.parse()

for i in items_res:
    print(i.en_text)
    print(i.ru_text)
    print(i.file_url)