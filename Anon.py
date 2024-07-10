import random
import string
import tkinter as tk
from datetime import datetime
from faker import Faker
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    FloodWaitError,
    PhoneNumberInvalidError,
    PhoneNumberOccupiedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest

# Функция для запроса API ID и API Hash
def request_api_credentials():
    api_id = input("Введите API ID: ")
    api_hash = input("Введите API Hash: ")
    return api_id, api_hash

# Функция для аутентификации в Telegram
def authenticate(api_id, api_hash):
    client = TelegramClient('session_name', api_id, api_hash)

    try:
        client.connect()

        if not client.is_user_authorized():
            phone_number = input("Введите ваш номер телефона в формате +71234567890: ")
            client.send_code_request(phone_number)
            code = input("Введите код, полученный от Telegram: ")

            client.sign_in(phone_number, code)

            # Сохранение данных сессии
            with open('session.txt', 'w') as f:
                f.write(client.session.save())

            # Если авторизация прошла успешно, закрываем командную строку
            client.disconnect()
            print("Сессия завершена")
            exit()

    except PhoneNumberInvalidError as e:
        log_error(f"Ошибка: Неверный номер телефона: {str(e)}")
        restart_program()
    except PhoneNumberOccupiedError as e:
        log_error(f"Ошибка: Номер телефона уже занят: {str(e)}")
        restart_program()
    except SessionPasswordNeededError as e:
        log_error(f"Ошибка: Двухфакторная аутентификация не поддерживается: {str(e)}")
        restart_program()
    except Exception as e:
        log_error(f"Ошибка: {str(e)}")
        restart_program()

    return client

# Ваши API ключи здесь
api_id, api_hash = request_api_credentials()  # Запрашиваем у пользователя API ID и API Hash

# Инициализация faker для генерации русских имен и фамилий
faker = Faker('ru_RU')

# Инициализация клиента Telegram
client = authenticate(api_id, api_hash)

# Функция генерации случайного имени пользователя
def generate_random_username(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Функция обновления профиля
def update_profile():
    global new_first_name, new_last_name, new_username

    try:
        new_first_name = faker.first_name()
        new_last_name = faker.last_name()
        new_username = generate_random_username()

        profile_result = client(UpdateProfileRequest(first_name=new_first_name, last_name=new_last_name))
        username_result = client(UpdateUsernameRequest(username=new_username))

        # Обновление меток в интерфейсе
        first_name_label.config(text=f"Имя: {new_first_name}")
        last_name_label.config(text=f"Фамилия: {new_last_name}")
        username_label.config(text=f"Имя пользователя: @{new_username}")

        # Запись лога
        log_entry = f"{datetime.now()} - Профиль обновлен: {new_first_name} {new_last_name}, @{new_username}\n"
        log_text.insert(tk.END, log_entry)
        log_text.see(tk.END)  # Прокручиваем текст вниз, чтобы видеть последние записи

        print(f"Имя обновлено на: {new_first_name} {new_last_name}")
        print(f"Имя пользователя обновлено на: @{new_username}")
        print(f"Ответ от сервера (профиль): {profile_result}")
        print(f"Ответ от сервера (имя пользователя): {username_result}")

        # Обновление информации об аккаунте
        update_account_info()

        # Запуск таймера обратного отсчета
        countdown(3600)  # Устанавливаем таймер на 60 минут

    except PhoneNumberInvalidError as e:
        log_error(f"Ошибка: Неверный номер телефона: {str(e)}")
        restart_program()
    except PhoneNumberOccupiedError as e:
        log_error(f"Ошибка: Номер телефона уже занят: {str(e)}")
        restart_program()
    except FloodWaitError as e:
        log_error(f"Ошибка: Превышено ограничение: {str(e)}")
        restart_program()
    except Exception as e:
        log_error(f"Ошибка: Проблема в смене имени: {str(e)}")
        restart_program()

# Функция для обновления информации об аккаунте
def update_account_info():
    global me
    me = client.get_me()
    account_number_label.config(text=f"Номер: {me.phone}")
    account_first_name_label.config(text=f"Имя: {me.first_name}")
    account_last_name_label.config(text=f"Фамилия: {me.last_name}")
    account_username_label.config(text=f"Имя пользователя: @{me.username}")

# Функция таймера обратного отсчета
def countdown(remaining=None):
    if remaining is not None:
        global time_remaining
        time_remaining = remaining

    if time_remaining <= 0:
        time_label.config(text="Время до следующего обновления: 00:00")
        update_profile()
    else:
        mins, secs = divmod(time_remaining, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        time_label.config(text=f"Время до следующего обновления: {timer}")
        time_remaining -= 1
        root.after(1000, countdown)

# Функция для записи ошибок в лог
def log_error(message):
    log_text.insert(tk.END, f"{datetime.now()} - {message}\n")
    log_text.see(tk.END)  # Прокручиваем текст вниз, чтобы видеть последние записи

# Создание основного окна
root = tk.Tk()
root.title("Telegram Profile Updater")

# Получение информации об аккаунте
me = client.get_me()

# Метки для отображения текущего имени, фамилии и имени пользователя
first_name_label = tk.Label(root, text=f"Имя: {me.first_name}")
first_name_label.pack(anchor="w")

last_name_label = tk.Label(root, text=f"Фамилия: {me.last_name}")
last_name_label.pack(anchor="w")

username_label = tk.Label(root, text=f"Имя пользователя: @{me.username}")
username_label.pack(anchor="w")

# Блок информации об аккаунте справа
account_frame = tk.Frame(root, padx=10, pady=10)
account_frame.pack(side="right", fill="y")

account_info_label = tk.Label(account_frame, text="Информация об аккаунте", font=("Arial", 12, "bold"))
account_info_label.pack(anchor="w")

account_number_label = tk.Label(account_frame, text=f"Номер: {me.phone}")
account_number_label.pack(anchor="w")

account_first_name_label = tk.Label(account_frame, text=f"Имя: {me.first_name}")
account_first_name_label.pack(anchor="w")

account_last_name_label = tk.Label(account_frame, text=f"Фамилия: {me.last_name}")
account_last_name_label.pack(anchor="w")

account_username_label = tk.Label(account_frame, text=f"Имя пользователя: @{me.username}")
account_username_label.pack(anchor="w")

# Метка для отображения таймера
time_label = tk.Label(root, text="Время до следующего обновления: 60:00")
time_label.pack(anchor="w", pady=(20, 0))

# Кнопка для немедленного обновления профиля
update_button = tk.Button(root, text="Обновить данные", command=update_profile)
update_button.pack(anchor="w", padx=10, pady=10)

# Лог обновлений профиля
log_frame = tk.Frame(root)
log_frame.pack(anchor="w", padx=10, pady=(20, 10), fill="both", expand=True)

log_label = tk.Label(log_frame, text="Лог обновлений профиля", font=("Arial", 12, "bold"))
log_label.pack(anchor="w")

log_text = tk.Text(log_frame, height=10, width=50)
log_text.pack(anchor="w", fill="both", expand=True)

# Окно для отображения ошибок
error_label = tk.Label(root, text="", fg="red")
error_label.pack(anchor="w", padx=10, pady=10)

# Запуск таймера на 60 минут
time_remaining = 3600
countdown()

# Запуск основного цикла Tkinter
root.mainloop()

# Завершение сессии клиента Telegram при закрытии окна
client.disconnect()
print("Сессия завершена")
