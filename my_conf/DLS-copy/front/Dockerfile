# Берем легкий образ Node.js
FROM node:20-alpine

# Создаем папку для приложения
WORKDIR /app

# Копируем ТОЛЬКО файлы зависимостей
COPY package*.json ./

# Ставим зависимости
RUN npm ci

# Копируем весь остальной код
COPY . .

# Собираем приложение
RUN npm run build

# Открываем порт
EXPOSE 3000

# Запускаем сервер
CMD ["npm", "run", "start"]