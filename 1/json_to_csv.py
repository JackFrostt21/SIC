import json
import csv

# Загрузка JSON
with open("user_stats.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Получение данных пользователей
user_stats = data["user_stats"]

# Создание CSV файла
with open("user_stats.csv", "w", newline="", encoding="utf-8") as csvfile:
    # Определение заголовков
    fieldnames = [
        "user_id",
        "errors",
        "success",
        "error_type",
        "retry_timeout",
        "lightning_ids_count",
        "lightning_ids",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

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
        writer.writerow(row)

print("Файл user_stats.csv успешно создан.")
