"""
Задание 6.

Создать  НЕ программно (вручную) текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».

Принудительно программно открыть файл в формате Unicode и вывести его содержимое.
Что это значит? Это значит, что при чтении файла вы должны явно указать кодировку utf-8
и файл должен открыться у ЛЮБОГО!!! человека при запуске вашего скрипта.

При сдаче задания в папке должен лежать текстовый файл!

Это значит вы должны предусмотреть случай, что вы по дефолту записали файл в cp1251,
а прочитать пытаетесь в utf-8.

Преподаватель будет запускать ваш скрипт и ошибок НЕ ДОЛЖНО появиться!

Подсказки:
--- обратите внимание, что заполнять файл вы можете в любой кодировке
но открыть нужно ИМЕННО!!! в формате Unicode (utf-8)
--- обратите внимание на чтение файла в режиме rb
для последующей переконвертации в нужную кодировку

НАРУШЕНИЕ обозначенных условий - задание не выполнено!!!
"""
import chardet


def read_utf_8(text_file):
    # check encoding
    with open(text_file, 'rb') as f:
        text_bytes = f.read()
        encoding = chardet.detect(text_bytes)['encoding']
    # decode and rewrite in utf-8
    if encoding != 'UTF-8':
        text = text_bytes.decode(encoding)
        with open(text_file, 'w', encoding='utf-8') as file:
            file.writelines(text.replace('\n', ''))
    # read in utf-8
    with open(text_file, 'r', encoding='utf-8') as f:
        text_utf_8 = f.read()
        print(text_utf_8)


lines = ['сетевое программирование', 'сокет', 'декоратор']

with open('test_file.txt','w', encoding='utf-16') as f:
    for line in lines:
        f.write(f'{line}\n')

read_utf_8('test_file.txt')



