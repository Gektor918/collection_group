import json

class ApiExampleCollectionGroup:

    create_group = (
        "JSON string containing collection group data.\n\n"
        "**Example:**\n"
        "```json\n"
        + json.dumps(
            {
                "company_id": 1,
                "lang": {
                    "en": {
                        "name": "Promo",
                        "description": "Promotional collections",
                    },
                    "ru": {
                        "name": "Промо",
                        "description": "Промо-коллекции",
                    },
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n```"
    )

    update_order = (
        "JSON string containing collection group order mapping.\n\n"
        "**Example:**\n"
        "```json\n"
        + json.dumps(
            {
                "company_id": 1,
                "orders": {
                    1: 10,
                    2: 20,
                    3: 30
                }
            },
            ensure_ascii=False,
            indent=2
        )
        + "\n```"
    )

    update_group = (
        "JSON string containing updated collection group data.\n\n"
        "**Example:**\n"
        "```json\n"
        "{\n"
        '  "company_id": 1,\n'
        '  "id": 12,\n'
        '  "disable": false,\n'
        '  "lang": {\n'
        '    "en": {"name": "Promo Updated", "description": "Promotional collections"},\n'
        '    "ru": {"name": "Промо обновлено", "description": "Новое описание"}\n'
        "  }\n"
        "}\n"
        "```"
    )

    update_group_list = (
        "JSON string containing collection group list update data.\n\n"
        "**Example:**\n"
        "```json\n"
        "{\n"
        '  "company_id": 1,\n'
        '  "id": 12,\n'
        '  "new_collections": [1, 2, 3],\n'
        '  "delete_collections": [4, 5]\n'
        "}\n"
        "```"
    )
