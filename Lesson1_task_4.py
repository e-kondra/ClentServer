"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
my_list = ['разработка', 'администрирование', 'protocol', 'standard', 'susipažinimas']
for i in my_list:
    i_enc = i.encode('utf-8')
    print(i_enc,type(i_enc))
    i_dec = i_enc.decode('utf-8')
    print(i_dec, type(i_dec))

# Посмотрите на кодировку в литовском слове susipažinimas!
# Одна буква не из ASCII - в байтах выглядит как b'susipa\xc5\xbeinimas'
