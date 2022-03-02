import gensim
import logging
import zipfile

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class WordAnalyser:
    def __init__(self) -> None:
        with zipfile.ZipFile('models/0.zip', 'r') as archive:
            stream = archive.open('model.bin')
            self.model_en = gensim.models.KeyedVectors.load_word2vec_format(stream, binary=True)

        self.model_ru = gensim.models.KeyedVectors.load('models/213/model.model')

    def get_sim_of_two(self, word1: str, word2: str, lang: str) -> float:
        try:
            if lang == 'ru':
                return self.model_ru.similarity(word1, word2)
            return self.model_en.similarity(word1, word2)
        except:
            return 0.0


if __name__ == '__main__':
    word_analyser = WordAnalyser()
    print(word_analyser.get_sim_of_two('cat', 'dog', 'en'))
