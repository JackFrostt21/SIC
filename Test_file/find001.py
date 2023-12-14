import csv

# import os

# print(os.getcwd())

file_of = "input_csv_for_DB.csv"  # файл с ГУИДами
file_in = "DB_test.csv"  # файл куда положить ГУИДы

# Создаю два пустых списка
users_of = []
users_in = []

# читаю данные из файла file_of
with open(file_of, "r", encoding="utf-8") as file:
    reader_of = csv.reader(file)
    for row in reader_of:
        users_of.append(row)

# читаю данные из файла file_in
with open(file_in, "r", encoding="utf-8") as file:
    reader_in = csv.reader(file)
    for row in reader_in:
        users_in.append(row)

# выполняю сравнение, если нахожу совпадение, добавляю в список ГУИД
for row_of in users_of:
    for row_in in users_in:
        full_name = (
            row_in[0] + " " + row_in[1]
        )  # конкатенация, в файле file_in имя и фамилия в разных ячейках
        if row_of[0] == full_name:
            row_in[2] = row_of[1]

# перезаписываю в таблицу file_in из списка users_in
with open(file_in, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    for row in users_in:
        writer.writerow(row)
