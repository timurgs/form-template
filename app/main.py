import re
import json
from typing import Dict, Any

from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client["forms_db"]
templates_collection = db["templates"]


async def load_templates():
    with open("app/templates/sample_templates.json", 'r') as f:
        templates = json.load(f)
        await templates_collection.insert_many(templates)


# Функция для валидации данных
def validate_field(field_name: str, value: str) -> str:
    if re.match(r"^\d{2}\.\d{2}\.\d{4}$", value) or re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return "date"
    elif re.match(r"^\+7 \d{3} \d{3} \d{2} \d{2}$", value):
        return "phone"
    elif re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
        return "email"
    else:
        return "text"


@app.post("/get_form")
async def get_form(request: Request) -> Dict[str, Any]:
    # Получаем данные, переданные пользователем в произвольной форме
    form_data = dict(await request.form())

    # загружаем базу MongoDB шаблонами
    await load_templates()

    # Получаем шаблоны форм из MongoDB
    templates = await templates_collection.find().to_list(length=None)

    # Проверяем соответствие с шаблонами
    for template in templates:
        template_fields = template["fields"]
        if all(field in form_data and validate_field(field, form_data[field]) == field_type
               for field, field_type in template_fields.items()):
            return {"template_name": template["name"]}

    # Если ни один шаблон не подходит, возвращаем ошибки валидации
    validation_errors = {}
    for field_name, value in form_data.items():
        validation_errors[field_name] = validate_field(field_name, value)

    return validation_errors
