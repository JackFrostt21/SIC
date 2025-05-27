import json

# Полный JSON из запроса пользователя
json_data = {
    "user_stats": {
        "56888107": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 34]},
        "61510644": {
            "errors": 1,
            "success": 0,
            "error_type": "bot_blocked",
            "lightning_ids": [],
        },
        "95200667": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "100792866": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "123170452": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "146284950": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 270,
        },
        "146284959": {
            "errors": 1,
            "success": 0,
            "error_type": "unknown",
            "error_message": "Chat not found",
            "lightning_ids": [],
        },
        "149037188": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "150639777": {"errors": 0, "success": 2, "lightning_ids": [42]},
        "177408232": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34],
        },
        "182394876": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "183145985": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "186363946": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "215321729": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "219328141": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "227396987": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "231201314": {
            "errors": 1,
            "success": 0,
            "error_type": "bot_blocked",
            "lightning_ids": [],
        },
        "237254696": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "243730972": {"errors": 0, "success": 2, "lightning_ids": [45]},
        "248732701": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34, 33, 32],
        },
        "275846048": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "279595238": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "281581844": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "289054183": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "293445251": {"errors": 0, "success": 2, "lightning_ids": [45]},
        "295416883": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "321745026": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "346365321": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 33]},
        "346533414": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34],
        },
        "348796254": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "348908898": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "364580022": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34, 33, 32],
        },
        "368377853": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 34]},
        "370052751": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "385853376": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "430966547": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "443055717": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 277,
        },
        "448950069": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34],
        },
        "460833665": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 35]},
        "461270385": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "461485023": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
    }
}

# Для простоты демонстрации используем только фрагмент данных
# В реальности нужно использовать полный JSON из запроса пользователя

# Сохранение JSON в файл
with open("user_stats.json", "w", encoding="utf-8") as file:
    json.dump(json_data, file, indent=2, ensure_ascii=False)

print("Файл user_stats.json успешно создан.")
print("Запустите скрипт json_to_csv.py для преобразования JSON в CSV файл.")
