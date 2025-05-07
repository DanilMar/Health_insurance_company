import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess  # Импортируем subprocess

# Путь к файлу подачи заявки
APPLY_FOR_INSURANCE_FILENAME = "apply_for_insurance.py"
ADMINISTRATION_MODULE_FILENAME = "administration_module.py"  # Добавляем путь к файлу админ-модуля

# Создание базы данных (если не существует)
def create_db():
    global conn
    conn = sqlite3.connect('medicine.db')
    global cursor
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            full_name TEXT,
            birth_date TEXT,
            passport_series TEXT,
            passport_number TEXT,
            contract_number TEXT,
            date TEXT,
            insurance_number INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Регистрация нового пользователя
def register(username, password, email, phone):
    if not username or not password or not email or not phone or "Логин" in entry_username.get() or "Пароль" in entry_password.get() or "Повторить пароль" in entry_confirm_password.get() or "Email" in entry_email.get() or "Номер телефона" in entry_phone.get():
        messagebox.showerror("Ошибка", "Все поля обязательны для заполнения.")
        return

    if password != entry_confirm_password.get():
        messagebox.showerror("Ошибка", "Пароли не совпадают.")
        return

    conn = sqlite3.connect('medicine.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)',
                       (username, password, email, phone))
        conn.commit()
        messagebox.showinfo("Успех", "Пользователь зарегистрирован!")
        clear_login_form()  # Очищаем форму авторизации
        show_login_form()    # Показать форму авторизации снова
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    finally:
        conn.close()

def open_apply_for_insurance(username, password):
    # Запускаем файл apply_for_insurance.py как модуль
    subprocess.Popen(["python", APPLY_FOR_INSURANCE_FILENAME, username, password])

def open_administration_module(username, password):
    """Открывает модуль администрирования."""
    subprocess.Popen(["python", ADMINISTRATION_MODULE_FILENAME, username, password])
    root.destroy()

# Авторизация пользователя
def login():
    username = entry_user.get()
    password = entry_pass.get()

    conn = sqlite3.connect('medicine.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()

    if row and row[0] == password:
        if username == "admin":
            messagebox.showinfo("Успех", "Вы вошли в систему как администратор!")
            open_administration_module(username, password)  # Открываем модуль администрирования
        else:
            messagebox.showinfo("Успех", "Вы вошли в систему!")
            open_apply_for_insurance(username, password)  # Передаем имя пользователя и пароль
            root.destroy()  # Закрываем окно авторизации
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль.")

    conn.close()

# Очистка формы авторизации
def clear_login_form():
    for widget in root.winfo_children():
        # Убедитесь, что вы не удаляете panel
        if isinstance(widget, (tk.Button, tk.Entry, tk.Label)):
            widget.destroy()

# Функция для создания поля ввода с подсказкой
def entry_with_placeholder(parent, placeholder, width):
    entry = tk.Entry(parent, fg='#504e4e', bg='#d7d3d3', bd=2, highlightbackground='#810000', highlightcolor='#810000', highlightthickness=2, width=width, font=('Arial', 16))  # Устанавливаем цвет текста, фон и 2D-обводку
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", lambda e: clear_placeholder(e, placeholder))
    entry.bind("<FocusOut>", lambda e: set_placeholder(e, placeholder))
    return entry

def clear_placeholder(event, placeholder):
    if event.widget.get() == placeholder:
        event.widget.delete(0, tk.END)
        event.widget.config(fg='black')  # Меняем цвет текста на черный

# Устанавливаем подсказку, если поле пустое
def set_placeholder(event, placeholder):
    if event.widget.get() == "":
        event.widget.insert(0, placeholder)
        event.widget.config(fg='#504e4e')  # Меняем цвет текста на серый

# Отображение формы регистрации
def show_registration_form():
    clear_login_form()

    global entry_username
    entry_username = entry_with_placeholder(root, "Логин", 40)
    entry_username.place(x=400, y=250)

    global entry_password
    entry_password = entry_with_placeholder(root, "Пароль", 40)
    entry_password.place(x=400, y=310)

    global entry_confirm_password
    entry_confirm_password = entry_with_placeholder(root, "Повторите пароль", 40)
    entry_confirm_password.place(x=400, y=370)

    global entry_email
    entry_email = entry_with_placeholder(root, "Email", 40)
    entry_email.place(x=400, y=430)

    global entry_phone
    entry_phone = entry_with_placeholder(root, "Номер телефона", 40)
    entry_phone.place(x=400, y=490)

    tk.Button(root, text="РЕГИСТРАЦИЯ", command=lambda: register(entry_username.get(), entry_password.get(), entry_email.get(), entry_phone.get()), bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightthickness=2, width=20, height=1, font=('Russo One', 14)).place(x=515, y=550)

# Отображение формы авторизации
def show_login_form():
    clear_login_form()

    global entry_user
    entry_user = entry_with_placeholder(root, "Логин", 40)
    entry_user.place(x=400, y=320)

    global entry_pass
    entry_pass = entry_with_placeholder(root, "Пароль", 40)
    entry_pass.place(x=400, y=375)

    tk.Button(root, text="ВХОД", command=login, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightcolor='#810000', highlightthickness=2, width=7, height=1, font=('Russo One', 14)).place(x=590, y=425)
    tk.Button(root, text="Регистрация", command=show_registration_form, bg='white', fg='black', relief='solid', highlightthickness=0,  borderwidth=0, width=10, height=1, font=('Arial', 10, 'italic')).place(x=410, y=435)

# Создание графического интерфейса
root = tk.Tk()
root.title("МЕДСТРАХ")
root.iconbitmap("med.ico")
root.config(bg='white')
root.state('zoomed')
root.geometry(f"{1920}x{1080}")

# Шапка
red_frame = tk.Frame(root, bg="#810000", height=110)
red_frame.pack(fill=tk.X)

# Заголовок "МедСтрах"
title_label = tk.Label(red_frame, text="МЕДСТРАХ", font=("mr_ApexMk3MediumG", 48, "bold"), fg="white", bg="#810000")
title_label.pack(pady=20) # Добавили pady для отступа сверху и снизу
title_label.place(relx=0.5, rely=0.5, anchor="center")

create_db()  # Создание базы данных
show_login_form()  # Отобразить форму авторизации

root.mainloop()