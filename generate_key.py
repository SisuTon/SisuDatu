import secrets
import string

# Генерируем случайную строку из 64 символов
# Используем буквы (верхний и нижний регистр), цифры и специальные символы
chars = string.ascii_letters + string.digits + string.punctuation
jwt_key = ''.join(secrets.choice(chars) for _ in range(64))

print("\nВаш новый JWT секретный ключ:")
print("-" * 50)
print(jwt_key)
print("-" * 50)
print("\nСкопируйте этот ключ и вставьте его в файл .env вместо 'ваш_секретный_ключ_jwt_здесь'") 