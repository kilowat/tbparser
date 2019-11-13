class WordEntity:

    def __init__(self, word):
        self.word = word
        self.en_text = ""
        self.ru_text = ""
        self.file_url = ""
        self.file_name = ""
        self.ipa_text = ""

    def __str__(self):
        return f' word: {self.word} \n en_text: {self.en_text} \n ip_text: {self.ipa_text} \n ru_text: {self.ru_text} \n file_url: {self.file_url} \n file_name: {self.file_name} '



