import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys
import subprocess
import random
from tkinter import scrolledtext
from PIL import Image, ImageTk  # Используем Pillow для обработки изображений

class MainPage:
    def __init__(self, master, username, password):
        self.master = master
        self.master.title("Главная страница")
        self.master.iconbitmap("med.ico")
        self.master.config(bg='white')
        self.username = username
        self.password = password
        self.master.state('zoomed')
        self.master.geometry(f"{1920}x{1080}")
        self.user_data = self.load_user_data()
        self.contract_number = self.get_or_create_contract_number()
        self.menu_open = False
        self.arial_12 = ("Arial", 12)

        # Шапка
        self.red_frame = tk.Frame(self.master, bg="#810000", height=110)
        self.red_frame.pack(fill=tk.X)

        # Заголовок "Медстрах"
        self.title_label = tk.Label(self.red_frame, text="МЕДСТРАХ", font=("Impact", 48, "bold"), fg="white", bg="#810000")
        self.title_label.pack(pady=20)
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Создание элементов интерфейса
        self.create_widgets()

    def load_user_data(self):
        """Загружает данные пользователя из базы данных."""
        try:
            conn = sqlite3.connect('medicine.db')
            cursor = conn.cursor()
            cursor.execute('SELECT full_name, username, password, birth_date, passport_series, passport_number, email, phone FROM users WHERE username = ?', (self.username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'full_name': row[0],
                    'username': row[1],
                    'password': row[2],
                    'birth_date': row[3],
                    'passport_series': row[4],
                    'passport_number': row[5],
                    'email': row[6],
                    'phone': row[7]
                }
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные пользователя.")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {e}")
            return None

    def get_or_create_contract_number(self):
        """Получает существующий или создаёт новый номер договора."""
        try:
            conn = sqlite3.connect('medicine.db')
            cursor = conn.cursor()

            # Попытка получить существующий номер договора
            cursor.execute('SELECT contract_number FROM users WHERE username = ?', (self.username,))
            row = cursor.fetchone()

            if row and row[0] is not None:
                return row[0]  # Возвращает существующий номер договора
            else:
                # Создаёт новый номер договора, если он не существует
                new_contract_number = random.randint(100000, 999999)
                cursor.execute('UPDATE users SET contract_number = ? WHERE username = ?', (new_contract_number, self.username))
                conn.commit()
                conn.close()
                return new_contract_number  # Возвращает новый номер договора
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при работе с номером договора: {e}")
            return None

    def create_widgets(self):
        if self.user_data is None:
            return  # Прекращаем создание интерфейса, если данные не загружены

        # Преобразование иконок в объекты PhotoImage
        menu_icon = Image.open("menu.png")
        menu_photo = ImageTk.PhotoImage(menu_icon)
        support_icon = Image.open("support.png")
        support_photo = ImageTk.PhotoImage(support_icon)
        user_icon = Image.open("user.png")
        user_photo = ImageTk.PhotoImage(user_icon)

        # Кнопка Меню в левом верхнем углу (используя изображение)
        menu_button = tk.Button(self.master, image=menu_photo, command=self.toggle_menu, bg='#810000', activebackground='white', relief='flat')
        menu_button.image = menu_photo  # Сохраняем ссылку на объект изображения
        menu_button.place(x = 0, y = -6)

        # Кнопка Поддержка в правом верхнем углу (используя изображение)
        support_button = tk.Button(self.master, image=support_photo, command=self.open_support_chat, bg='#810000', activebackground='white', relief='flat')
        support_button.image = support_photo  # Сохраняем ссылку на объект изображения
        support_button.place(x = 1160, y = -6)

        # Кнопка профиля в правом верхнем углу (используя изображение)
        user_button = tk.Button(self.master, image=user_photo, command=self.open_main_page, bg='#810000', activebackground='white', relief='flat')
        user_button.image = user_photo  # Сохраняем ссылку на объект изображения
        user_button.place(x=1040, y=-6)

        tk.Label(self.master, text=self.user_data['full_name'].upper(), font=("Arial", 16, "bold"), bg="white").pack(pady=15)
        tk.Label(self.master, text=f"Логин: {self.user_data['username']}", font=("Arial", 12), bg="white").pack(pady=5)
        self.create_password_section()  # Создаем секцию пароля
        tk.Label(self.master, text=f"Дата рождения: {self.user_data['birth_date']}", font=("Arial", 12), bg="white").pack(pady=5)
        self.create_passport_section()  # Создаем секцию паспорта
        self.create_email_section()  # Создаем секцию email
        self.create_phone_section()  # Создаем секцию телефона

        if self.contract_number is not None:
            tk.Label(self.master, text=f"Номер текущего договора: {self.contract_number}", font=("Arial", 12), bg="white").pack(pady=5)
        else:
            tk.Label(self.master, text="Ошибка: Не удалось получить номер договора", font=("Arial", 12, "italic"), bg="white").pack(pady=5)

    def create_password_section(self):
        """Создает секцию для отображения и изменения пароля."""
        frame = tk.Frame(self.master, bg="white")
        frame.pack(pady=5)
        tk.Label(frame, text="Пароль: " + "*" * len(self.user_data['password']), font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Изменить", command=self.open_password_change_window, bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10)).pack(side=tk.LEFT, padx=5)

    def create_passport_section(self):
        """Создает секцию для отображения и изменения данных паспорта."""
        frame = tk.Frame(self.master, bg="white")
        frame.pack(pady=5)
        tk.Label(frame, text=f"Серия паспорта: {self.user_data['passport_series']}", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Изменить", command=lambda: self.open_change_window('passport_series', 'Серия паспорта'), bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10)).pack(side=tk.LEFT, padx=5)

        frame = tk.Frame(self.master, bg="white")
        frame.pack(pady=5)
        tk.Label(frame, text=f"Номер паспорта: {self.user_data['passport_number']}", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Изменить", command=lambda: self.open_change_window('passport_number', 'Номер паспорта'), bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10)).pack(side=tk.LEFT, padx=5)

    def create_email_section(self):
        """Создает секцию для отображения и изменения email."""
        frame = tk.Frame(self.master, bg="white")
        frame.pack(pady=5)
        tk.Label(frame, text=f"Email: {self.user_data['email']}", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Изменить", command=lambda: self.open_change_window('email', 'Email'), bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10)).pack(side=tk.LEFT, padx=5)

    def create_phone_section(self):
        """Создает секцию для отображения и изменения номера телефона."""
        frame = tk.Frame(self.master, bg="white")
        frame.pack(pady=5)
        tk.Label(frame, text=f"Номер телефона: {self.user_data['phone']}", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Изменить", command=lambda: self.open_change_window('phone', 'Номер телефона'), bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10)).pack(side=tk.LEFT, padx=5)

    def open_change_window(self, field, field_name):
        """Открывает окно для изменения данных."""
        change_window = tk.Toplevel(self.master)
        change_window.title(f"Изменить {field_name}")
        self.center_window(change_window, 380, 130)
        change_window.configure(bg="#f0f0f0")

        label_style = {"font": ("Arial", 12), "bg": "#f0f0f0"}
        entry_style = {"font": ("Arial", 12), "width": 30}

        tk.Label(change_window, text=f"Новый {field_name}:", **label_style).pack(pady=5)
        entry = tk.Entry(change_window, **entry_style)
        entry.pack(pady=5)

        def update_data():
            new_value = entry.get()
            if new_value:
                try:
                    conn = sqlite3.connect('medicine.db')
                    cursor = conn.cursor()
                    cursor.execute(f'UPDATE users SET {field} = ? WHERE username = ?', (new_value, self.username))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Успех", f"{field_name} успешно изменен.")
                    self.user_data[field] = new_value
                    change_window.destroy()
                    self.master.destroy()
                    subprocess.Popen(["python", "main_page.py", self.username, self.password])  # Запускаем с тем же логином и паролем.
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при обновлении {field_name}: {e}")
                    change_window.attributes('-topmost', True)  # Всегда сверху при ошибке
            else:
                messagebox.showerror("Ошибка", "Поле не может быть пустым.")
                change_window.attributes('-topmost', True)  # Всегда сверху при ошибке

        tk.Button(change_window, text="Сохранить", command=update_data, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightthickness=2, width=12, height=1, font=('Russo One', 14)).pack(pady=10)

    def open_password_change_window(self):
        """Открывает окно для изменения пароля."""
        password_window = tk.Toplevel(self.master)
        password_window.title("Изменить пароль")
        self.center_window(password_window, 380, 270)
        password_window.configure(bg="#f0f0f0")

        label_style = {"font": ("Arial", 12), "bg": "#f0f0f0"}
        entry_style = {"font": ("Arial", 12), "width": 30}

        tk.Label(password_window, text="Старый пароль:", **label_style).pack(pady=5)
        old_password_entry = tk.Entry(password_window, show="*", **entry_style)
        old_password_entry.pack(pady=5)

        tk.Label(password_window, text="Новый пароль:", **label_style).pack(pady=5)
        new_password_entry = tk.Entry(password_window, show="*", **entry_style)
        new_password_entry.pack(pady=5)

        tk.Label(password_window, text="Повторите новый пароль:", **label_style).pack(pady=5)
        confirm_password_entry = tk.Entry(password_window, show="*", **entry_style)
        confirm_password_entry.pack(pady=5)

        def update_password():
            old_password = old_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not all([old_password, new_password, confirm_password]):
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                password_window.attributes('-topmost', True)
                return

            if old_password != self.user_data['password']:
                messagebox.showerror("Ошибка", "Старый пароль введен неверно.")
                password_window.attributes('-topmost', True)
                return

            if new_password != confirm_password:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают.")
                password_window.attributes('-topmost', True)
                return

            try:
                conn = sqlite3.connect('medicine.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, self.username))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Пароль успешно изменен.")
                self.password = new_password
                self.user_data['password'] = new_password
                password_window.destroy()
                self.master.destroy()
                subprocess.Popen(["python", "main_page.py", self.username, self.password])  # Перезапускаем main_page с новым паролем
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении пароля: {e}")
                password_window.attributes('-topmost', True)

        tk.Button(password_window, text="Сохранить", command=update_password, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightthickness=2, width=12, height=1, font=('Russo One', 14)).pack(pady=10)

    def open_support_chat(self):
        """Открывает окно с чатом поддержки в правом верхнем углу и поверх всех окон."""
        support_window = tk.Toplevel(self.master)
        support_window.title("Чат с поддержкой")

        # Устанавливаем окно поверх всех
        support_window.transient(self.master)  # Окно привязано к основному
        support_window.grab_set()  # Захватываем фокус
        support_window.attributes('-topmost', True)

        # Получаем размеры главного окна
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()

        # Устанавливаем размер и положение окна поддержки
        support_width = 350
        support_height = 500  # Увеличиваем высоту окна
        x = main_width - support_width - 10  # Отступ от правого края
        y = 0 + 10  # Отступ от верхнего края
        support_window.geometry(f"{support_width}x{support_height}+{x}+{y}")

        support_window.transient(self.master)
        support_window.grab_set()
        support_window.attributes('-topmost', True)

        # Задаём фон окна поддержки
        support_window.configure(bg="#f0f0f0")

        # Текстовое поле для отображения сообщений (с возможностью прокрутки)
        self.chat_log = scrolledtext.ScrolledText(support_window, wrap=tk.WORD, state=tk.DISABLED, bg="#ffffff", font=self.arial_12)
        self.chat_log.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Фрейм для поля ввода и кнопки отправки
        input_frame = tk.Frame(support_window, bg="#f0f0f0")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Поле ввода для нового сообщения
        self.message_entry = tk.Entry(input_frame, font=self.arial_12)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Кнопка отправки сообщения
        send_button = tk.Button(input_frame, text="Отправить", command=self.send_message, bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=10, height=1, font=('Russo One', 10))
        send_button.pack(side=tk.RIGHT)

        # Сохраняем ссылку на окно поддержки, чтобы можно было его закрыть
        self.support_window = support_window

    def send_message(self):
        """Отправляет сообщение пользователя и добавляет ответ поддержки."""
        message = self.message_entry.get()
        if message:
            # Добавляем сообщение пользователя в чат
            self.chat_log.config(state=tk.NORMAL)  # Разблокируем для редактирования
            self.chat_log.insert(tk.END, f"Вы: {message}\n")
            self.chat_log.config(state=tk.DISABLED)  # Блокируем обратно

            # Очищаем поле ввода
            self.message_entry.delete(0, tk.END)

            # Запланировать добавление сообщения от поддержки через 2 секунды
            self.master.after(2000, self.add_support_response)

            # Прокручиваем чат к последнему сообщению
            self.chat_log.see(tk.END)

    def add_support_response(self):
        """Добавляет автоматический ответ от поддержки."""
        response = "Наш оператор свяжется с вами в ближайшее время.\n"
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"Поддержка: {response}")
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(tk.END)

    def toggle_menu(self):
        if self.menu_open:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        """Отображает меню."""
        self.menu_open = True
        # Получаем размеры главного окна
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()

        # Создаем красный прямоугольник
        self.menu_frame = tk.Frame(self.master, bg="#640101", width=300, height=main_height)
        self.menu_frame.place(x=0, y=0)  # Размещаем в левом верхнем углу

        # Создаем кнопки
        button_width = 280  # Ширина кнопок
        button_x = 10  # Отступ от края

        self.tariffs_button = tk.Button(self.menu_frame, text="Тарифы страхования", command=self.open_tariffs, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.tariffs_button.place(x=button_x, y=50)

        self.my_contracts_button = tk.Button(self.menu_frame, text="Мой договор", command=self.open_my_contracts, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.my_contracts_button.place(x=button_x, y=100)

        self.payment_button = tk.Button(self.menu_frame, text="Расчёт выплат", command=self.open_payment, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.payment_button.place(x=button_x, y=150)

        # Кнопка Выход
        self.exit_button = tk.Button(self.menu_frame, text="Выход", command=self.exit_program, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.exit_button.place(x=button_x, y=main_height - 50)  # Размещаем внизу

    def hide_menu(self):
        """Скрывает меню."""
        self.menu_open = False
        self.menu_frame.destroy()

    def open_tariffs(self):
        """Открывает файл тарифов."""
        subprocess.Popen(["python", "tariffs.py", self.username, self.password])
        self.master.destroy()

    def open_my_contracts(self):
        """Открывает файл моих договоров."""
        subprocess.Popen(["python", "my_contracts.py", self.username, self.password])
        self.master.destroy()

    def open_payment(self):
        """Открывает файл расчёта выплат."""
        subprocess.Popen(["python", "payment.py", self.username, self.password])
        self.master.destroy()

    def open_main_page(self):
        """Открывает файл главной страницы."""
        subprocess.Popen(["python", "main_page.py", self.username, self.password])
        self.master.destroy()

    def exit_program(self):
        """Закрывает программу."""
        self.master.destroy()

    def center_window(self, window, width, height):
        """Центрирует окно на экране."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

def main():
    root = tk.Tk()
    username = sys.argv[1]
    password = sys.argv[2]
    MainPage(root, username, password)
    root.mainloop()

if __name__ == "__main__":
    main()