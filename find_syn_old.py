import json
from analyser import WordAnalyser


def activation_function(x):
    return pow(x, 4)


class GenerateSyn:
    def __init__(self):
        self.word_analyser = WordAnalyser()

        with open('tags/data.json', 'r') as f:
            self.tag_data = json.load(f)

        self.td = {}
        i = 0
        for tag in self.tag_data:
            self.td[tag['slug']] = i
            i += 1

        open('results/tag_info.json', 'w').write(json.dumps(self.td, ensure_ascii=False).encode('utf8').decode())

    def word2vec_distance(self, word1, word2, lang):
        if lang == 'ru':
            return self.word_analyser.get_sim_of_two(word1, word2.split('_')[0].replace('ё', 'е'), lang)
        return self.word_analyser.get_sim_of_two(word1 + '_NOUN', word2, lang)

    def syn_for_word(self, word, lang):
        result = []

        cur_tags = []
        for tag in self.tag_data:
            for tag_word in tag['name_' + lang].split(' '):
                distance = self.word2vec_distance(tag_word, word, lang)
                if distance > 0.4:
                    cur_tags.append([tag['slug'], activation_function(distance)])

        for cr in cur_tags:
            result.append({'t': self.td[cr[0]], 'd': round(cr[1], 4)})

        return result

    def find_syn(self, lang):
        result = {}

        iteration = 0
        with open('stem/' + lang + '_stem.txt', 'r') as f:
            for word in f:
                iteration += 1

                if iteration % 1000 == 0:
                    print(iteration, lang)

                word = word.strip()
                syn = self.syn_for_word(word, lang)
                if len(syn) != 0:
                    result[word.split('_')[0]] = syn

        json_result = json.dumps(result, ensure_ascii=False).encode('utf8').decode()
        open('results/result_' + lang + '.json', 'w').write(json_result.replace(' ', ''))


def generate_new_syn():
    generator = GenerateSyn()
    generator.find_syn('ru')
    generator.find_syn('en')


if __name__ == '__main__':
    generate_new_syn()
