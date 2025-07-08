import secrets
import string

def generate_secure_password(length=16):
    """
    Генерирует криптографически безопасный случайный пароль
    
    Args:
        length (int): Длина пароля (по умолчанию 16 символов)
    
    Returns:
        str: Случайный пароль
    """
    # Определяем набор символов для пароля
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # Генерируем случайный пароль
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password

if __name__ == "__main__":
    # Генерируем несколько паролей для разных целей
    postgres_password = generate_secure_password(16)
    django_secret_key = generate_secure_password(50)
    
    print("🔐 Сгенерированные пароли:")
    print(f"PostgreSQL пароль: {postgres_password}")
    print(f"Django SECRET_KEY: {django_secret_key}")
    
    print("\n📝 Добавьте эти значения в ваш .env файл:")
    print(f"POSTGRES_PASSWORD={postgres_password}")
    print(f"DJANGO_SECRET_KEY={django_secret_key}")