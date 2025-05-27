import json
import pandas as pd

# Загрузка JSON
with open("user_stats.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Получение данных пользователей
user_stats = data["user_stats"]

# Создание списка для хранения данных
rows = []

# Заполнение данными
for user_id, stats in user_stats.items():
    row = {
        "user_id": user_id,
        "errors": stats.get("errors", ""),
        "success": stats.get("success", ""),
        "error_type": stats.get("error_type", ""),
        "retry_timeout": stats.get("retry_timeout", ""),
        "lightning_ids_count": len(stats.get("lightning_ids", [])),
        "lightning_ids": ", ".join(map(str, stats.get("lightning_ids", []))),
    }
    rows.append(row)

# Создание DataFrame
df = pd.DataFrame(rows)

# Сортировка данных по user_id
df = df.sort_values("user_id")

# Сохранение в Excel
df.to_excel("user_stats.xlsx", index=False)

print("Файл user_stats.xlsx успешно создан.")
