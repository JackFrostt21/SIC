import json

# JSON данные из запроса пользователя - это только первая часть большого JSON
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
        "468573369": {"errors": 0, "success": 2, "lightning_ids": [45]},
        "474258228": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "482207300": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34, 33, 32],
        },
        "490372974": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "491944782": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "493231966": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "507000027": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 276,
        },
        "519532772": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 277,
        },
        "532034177": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "555475165": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "556438220": {"errors": 0, "success": 2, "lightning_ids": [46]},
        "574706358": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 38]},
        "576410805": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "583158983": {
            "errors": 0,
            "success": 2,
            "lightning_ids": [46, 45, 41, 38, 35, 34],
        },
        "591561346": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 272,
        },
        "597047120": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 273,
        },
        "597703708": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "608622908": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "628088356": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "633773477": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 274,
        },
        "635494523": {
            "errors": 1,
            "success": 0,
            "error_type": "retry_after",
            "lightning_ids": [],
            "retry_timeout": 275,
        },
        "637339123": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41]},
        "639780607": {"errors": 0, "success": 2, "lightning_ids": [46, 45]},
        "642808954": {"errors": 0, "success": 2, "lightning_ids": [46]},
        "646939381": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38]},
        "651508458": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
        "653198898": {"errors": 0, "success": 2, "lightning_ids": [46, 45, 41, 38, 35]},
    }
}

# Для демонстрации работы скрипта мы используем только первые записи
# Чтобы использовать полный JSON из запроса, его нужно сохранить целиком

print("Запустите скрипт json_to_csv.py для преобразования JSON в CSV файл")
print("Результат будет сохранен в user_stats.csv")

# Сохранение JSON в файл
with open("user_stats.json", "w", encoding="utf-8") as file:
    json.dump(json_data, file, indent=2, ensure_ascii=False)

print("Файл user_stats.json успешно создан.")
