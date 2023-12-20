import re
import csv
from datetime import datetime


# функция для чтения, разделение конф файла на блоки и формированию словаря
def read_config(config_file):
    with open(config_file, "r") as file:
        content = file.read()  # определяю переменную которая читает весь файл конф
    blocks = re.split(
        r"\n(?=\[[\w\d]+\])", content
    )  # каждый раз, когда встречается строка с [что-то], начинается новый блок
    config_dictionary = {}
    for block in blocks:
        id_asterisk_match = re.search(
            r"\[([\w\d]+)\]", block
        )  # В каждом блоке ищется строка, заключенная в квадратные скобки. Если такая строка найдена, она извлекается.
        if id_asterisk_match:  # проверка, был ли найден заголовок блока - [что то]
            id_asterisk = id_asterisk_match.group(1)  # извлекаем из [] ключ
            config_dictionary[id_asterisk] = block.split(
                "\n"
            )  # значение ключа (список строк)
    return config_dictionary


# функция для чтения и формирования словаря по csv файлу
def read_csv(csv_file):
    csv_dictionary = {}
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(
            reader
        )  # пропускает первую строчку (оглавление), если ее нет, закомментить
        for row in reader:
            if len(row) >= 4:  # проверка чтобы не поломать алгоритм
                (
                    id_asterisk,
                    _,
                    guid_1c,
                    _,
                ) = row  # присваиваем параметрам (id_asterisk и guid_1c) значения элементов списка, остальное игнорируем
                csv_dictionary[id_asterisk] = guid_1c or None
    return csv_dictionary


# обновление словаря conf гуидом из словаря csv
def add_guid_to_conf(config, csv_data):
    for (
        id_asterisk,
        block,
    ) in (
        config.items()
    ):  # id_asterisk — ключ, а block — соответствующее ему значение (список строк)
        guid = csv_data.get(id_asterisk)  # получаем значение ключа
        block = [
            line for line in block if line.strip() != ""
        ]  # убираем разрыв основного блока в конф файле и новой гуид строки
        if guid:
            guid_line = f"guid={guid}"  # создаем строку в которой лежит гуид
            stroka_guid_yes = any(
                line.startswith("guid=") for line in block
            )  # проверяем есть ли в блоке строка guid=
            if stroka_guid_yes:
                block = [
                    line if not line.startswith("guid=") else guid_line
                    for line in block
                ]  # заменяем новой строкой (чтобы не получить дубли)
            else:
                block.append(guid_line)  # добавляем строку
        else:
            block = [
                line for line in block if not line.startswith("guid=")
            ]  # если гуида в csv нет, то удалеям в конф
        config[id_asterisk] = block  # присваиваем новый блок в словарь
    return config


# новый conf файл с текущей датой и временем в наименовании
def write_new_config(config, base_filename):
    new_conf_file = f'{base_filename}_{datetime.now().strftime("%y-%m-%d-%H-%M")}.conf'  # формируем наименование
    with open(new_conf_file, "w") as file:
        for block in config.values():
            block_content = "\n".join(block)  # собирает строки в блок с разделением \n
            file.write(
                block_content.strip() + "\n\n"
            )  # берем набор блоков, очищаем от лишних пробелов и делаем 2 переноса чтобы разорвать визуально блоки
    return new_conf_file


# путь к файлу
config_file = "config.conf"
csv_file = "data.csv"

# вызовы
config_dict = read_config(config_file)
csv_dict = read_csv(csv_file)
updated_config_dict = add_guid_to_conf(config_dict, csv_dict)

# основа для наименования нового конф файла
base_config_filename = "config"

# запись обновленного конф в новый файл
new_config_file = write_new_config(updated_config_dict, base_config_filename)
