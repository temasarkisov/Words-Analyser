import json
import os.path

import bs4
import re

from analyser import WordAnalyser


class GenerateSyn:
    def __init__(self):
        self.word_analyser = WordAnalyser()
        # with open('tags/data.json', 'r') as f:
        #    self.tag_data = json.load(f)

        # self.td = {}
        # i = 0
        # for tag in self.tag_data:
        #    self.td[tag['slug']] = i
        #    i += 1

        self.words_ru = self.word_analyser.model_ru.index_to_key
        self.words_en = self.word_analyser.model_en.index_to_key
        # open('results/tag_info.json', 'w').write(json.dumps(self.td, ensure_ascii=False).encode('utf8').decode())

    def activation_function(self, x):
        return pow(x, 4)

    @staticmethod
    def get_html(tag_name):
        import requests

        print(f'Get HTML for word - {tag_name}')
        if os.path.isfile('data_from_sinonim/' + tag_name + '.txt'):
            return open('data_from_sinonim/' + tag_name + '.txt').read()

        try:
            print(f'Download HTML for word - {tag_name}')
            url = "https://sinonim.org/as/" + tag_name

            payload = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Referer': 'https://sinonim.org/as/%D1%84',
                'Connection': 'keep-alive',
                'Cookie': 'num_hits=49; _ym_uid=16382092771028836659; _ym_d=1638209277; _ga=GA1.2.1756214272.1638209277; _gid=GA1.2.99813716.1638816244; _gat=1; _ym_isad=1; num_hits=50',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'TE': 'trailers'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            html = response.content.decode('utf-8')
            open('data_from_sinonim/' + tag_name + '.txt', 'w').write(html)
        except:
            return ''
        return html

    def parse_html(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        table = soup.find('ul', {'class': 'assocPodryad'})
        if not table:
            return {}
        li = table.find_all('li')
        result = {}
        for assoc in li:
            try:
                a = assoc.find('a')
                result[assoc.text] = float(re.search(r'\d+\.\d+', a.get('style')).group())
            except (AttributeError, TypeError):
                pass
        return result

    def find_close_to_word(self, word, border, lang):
        result = {}
        if lang == 'ru':
            words = self.words_ru
        else:
            words = self.words_en

        try:
            if lang == 'ru':
                arr = self.word_analyser.model_ru.most_similar(positive=word, topn=None)
            else:
                arr = self.word_analyser.model_en.most_similar(positive=word + '_NOUN', topn=None)
        except KeyError:
            return result

        for idx, el in enumerate(arr):
            if el > border:
                if lang == 'ru':
                    result[words[idx]] = el
                else:
                    result[words[idx].split('_')[0]] = el
        return result

    def calculate_border(self, value):
        return 1 + (3 - value) * 0.5

    def get_data_for_word(self, word, lang):
        print(f'Get tags for word - {word}, lang - {lang}')
        MIN_BORDER = 0.5

        html = self.get_html(word)
        associations = self.parse_html(html)
        main_res = self.find_close_to_word(word, MIN_BORDER, lang)

        for key, value in associations.items():
            new_border = MIN_BORDER * self.calculate_border(value)
            if new_border > 0.8:
                main_res = self.union_dicts(main_res, {key: MIN_BORDER + 0.25 / self.calculate_border(value)})
                continue
            dict_res = self.find_close_to_word(key, new_border, lang)

            for k, v in dict_res.items():
                dict_res[k] = v / 2 + 0.25 / self.calculate_border(v)
            self.union_dicts(main_res, dict_res)
        main_res = {k: v for k, v in sorted(main_res.items(), key=lambda item: -item[1])}
        for k, v in main_res.items():
            main_res[k] = round(self.activation_function(v), 4)
        return main_res

    def reverse_dict(self, data):
        result = {}
        for tag, tag_data in data.items():
            for word, value in tag_data.items():
                if word in result:
                    result[word].append({'t': tag, 'd': value})
                else:
                    result[word] = [{'t': tag, 'd': value}]
        return result

    def find_syn(self, lang):
        data_for_all_tags = {}
        print('Start searching syn', lang)
        for tag in self.tag_data:
            if not tag['active']:
                continue
            print(tag['name_' + lang], lang)
            data_for_all_tags[tag['slug']] = self.get_data_for_word(tag['name_' + lang], lang)
        print('Reverse dict', lang)
        result = self.reverse_dict(data_for_all_tags)
        json_result = json.dumps(result, ensure_ascii=False).encode('utf8').decode()
        print('Save file', lang)
        open('results/result_' + lang + '.json', 'w').write(json_result.replace(' ', ''))
        return result

    def union_dicts(self, main_res, dict_res):
        for k, v in dict_res.items():
            if k not in main_res:
                main_res[k] = v
                continue
            if v > main_res[k]:
                main_res[k] = v
        return main_res


def generate_new_syn():
    generator = GenerateSyn()

    with open('tags/tag_info.json', 'r') as f:
        tag_names = json.load(f)

    for tag_data in tag_names:
        if tag_data['lang'] == 'en':
            a = generator.get_data_for_word(tag_data['tag'].replace(' ', '::'), tag_data['lang'])
        else:
            a = generator.get_data_for_word(tag_data['tag'], tag_data['lang'])
        open('results/' + tag_data['tag'] + '.json', 'w') \
            .write(json.dumps(a, ensure_ascii=False).encode('utf8').decode())


if __name__ == '__main__':
    generate_new_syn()
