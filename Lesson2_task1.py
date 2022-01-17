"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import re

os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
main_data = []




def get_data():
    re_prod = re.compile(r"Изготовитель системы:\s*\S*")
    re_name = re.compile(r"Название ОС:\s*\S*")
    re_code = re.compile(r"Код продукта:\s*\S*")
    re_type = re.compile(r"Тип системы:\s*\S*")
    for i in range(1, 4):
        with open(f'info_{i}.txt', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if re_prod.search(str(row)):
                    os_prod_list.append(re_prod.search(str(row)).group().split()[2].replace("'", '').replace("]", ''))
                if re_name.search(str(row)):
                    os_name_list.append(re_name.search(str(row)).group().split()[2].replace("'", '').replace("]", ''))
                if re_code.search(str(row)):
                    os_code_list.append(re_code.search(str(row)).group().split()[2].replace("'", '').replace("]", ''))
                if re_type.search(str(row)):
                    os_type_list.append(re_type.search(str(row)).group().split()[2].replace("'", '').replace("]", ''))
    main_data.append(['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы'])
    for ind in range(len(os_prod_list)):
        main_data.append([os_prod_list[ind]])
        main_data[ind + 1].append(os_name_list[ind])
        main_data[ind + 1].append(os_code_list[ind])
        main_data[ind + 1].append(os_type_list[ind])
    return main_data

def write_to_csv(file):
    rows = get_data()
    print(rows)
    with open(file, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(rows)


write_to_csv('data_report.csv')