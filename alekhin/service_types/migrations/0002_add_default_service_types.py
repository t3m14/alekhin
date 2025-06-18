from django.db import migrations

def create_default_service_types(apps, schema_editor):
    ServiceType = apps.get_model('service_types', 'ServiceType')
    
    types = [
        "Флебология",
        "Лазерная облитерация изолированных вариксов",
        "Лечение сосудистых звездочек",
        "Лечение \"глубоких вен\" лазером",
        "Приём флеболога",
        "Лимфология",
        "Мануальное дренирование",
        "Бандажирование",
        "Комплексное лечение",
        "Гинекология",
        "БОС терапия",
        "Урогинекология",
        "Гинекологический профиль",
        "Сексология",
        "ЛФК",
        "Косметология",
        "Аппаратная коррекция фигуры",
        "Аппаратная косметология для рук",
        "Аппаратная чистка лица",
        "Лазерная эпиляция",
        "Эпиляция зоны бикини",
        "Эпиляция зоны тела",
        "Эпиляция зоны ног",
        "Эпиляция зоны рук",
        "Эпиляция зоны лица и шеи",
    ]
    
    # Удаляем дубликаты, сохраняя порядок
    unique_types = []
    for service_type in types:
        if service_type not in unique_types:
            unique_types.append(service_type)
    
    # Создаем записи только если их еще нет
    for type_name in unique_types:
        ServiceType.objects.get_or_create(
            name=type_name
        )

def reverse_create_default_service_types(apps, schema_editor):
    ServiceType = apps.get_model('service_types', 'ServiceType')
    
    types = [
        "Флебология",
        "Лазерная облитерация изолированных вариксов",
        "Лечение сосудистых звездочек",
        "Лечение \"глубоких вен\" лазером",
        "Приём флеболога",
        "Лимфология",
        "Мануальное дренирование",
        "Бандажирование",
        "Комплексное лечение",
        "Гинекология",
        "БОС терапия",
        "Урогинекология",
        "Гинекологический профиль",
        "Сексология",
        "ЛФК",
        "Косметология",
        "Аппаратная коррекция фигуры",
        "Аппаратная косметология для рук",
        "Аппаратная чистка лица",
        "Лазерная эпиляция",
        "Эпиляция зоны бикини",
        "Эпиляция зоны тела",
        "Эпиляция зоны ног",
        "Эпиляция зоны рук",
        "Эпиляция зоны лица и шеи",
    ]
    
    # Удаляем только те записи, которые мы создали
    ServiceType.objects.filter(name__in=types).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('service_types', '0001_initial'),  # Замените на последнюю миграцию
    ]

    operations = [
        migrations.RunPython(
            create_default_service_types,
            reverse_create_default_service_types
        ),
    ]