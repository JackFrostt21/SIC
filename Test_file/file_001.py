file_name = 'Probapera.txt'

list1 = []

for i in range(2):
    message = input('Vvedi suda:')
    list1.append(message + '\n')

with open(file_name, 'w') as file:
    for message in list1:
        file.write(message)

print('in file:')

with open(file_name, 'r') as file:
    for message in file:
        print(message, end='')