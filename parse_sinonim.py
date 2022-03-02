import json
from find_syn import GenerateSyn


if __name__ == '__main__':
    data = json.loads(open('reserve_data/tags.json').read())
    for tag in data:
        html = GenerateSyn.get_html(tag['name_ru'])
        print(tag['name_ru'])
        open('data_from_sinonim/' + tag['name_ru'] + '.txt', 'w').write(html)
