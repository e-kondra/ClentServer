"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""
import yaml

dict_for_yaml = {
    'first_key': ['first', 'second', 'third', 'fourth'],
    'second_key': 12,
    'third_key':
        {
            '111': 'vienas šimtas vienolika €',
            '34': 'trisdešimt keturi €'
        }
}

with open('file.yaml','w', encoding='utf-8') as f:
    yaml.dump(dict_for_yaml, f, default_flow_style=False, allow_unicode=True)

with open('file.yaml','r', encoding='utf-8') as f1:
    content = yaml.load(f1, Loader=yaml.BaseLoader)
    print(type(content))
    print(content)

print(content == dict_for_yaml)






