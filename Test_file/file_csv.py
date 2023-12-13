import csv

file_name = 'users.csv'

users = [["Tom", 28], ["Alice", 23], ["Bob", 34]]

with open(file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)

with open(file_name, 'a', newline='') as file:
    user = ["Sam", 31]
    writer = csv.writer(file)
    writer.writerow(user)

with open(file_name, 'r', newline='') as file:
    reader = csv.reader(file)
    for i in reader:
        print(i[0], ' - ', i[1])


#Добавляем запись в начало файла

with open(file_name, 'r', newline='') as file:
    reader = csv.reader(file)
    users = list(reader)

new_user = ['Jerry', 22]
users.insert(0, new_user)

with open(file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(users)