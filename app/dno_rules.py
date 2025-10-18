DNO_RULES = [
    {"check": "unique", "field": "pole_id"},
    {"check": "range", "field": "height", "min": 10, "max": 25},
    {"check": "required", "field": "material"},
    {"check": "required", "field": "location"}
]