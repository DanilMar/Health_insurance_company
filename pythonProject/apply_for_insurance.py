import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys  # Для получения аргументов командной строки
import subprocess

# Файл, куда перебрасываем при успешной подаче заявки или наличии данных
MAIN_PAGE_FILENAME = "main_page.py"

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

        # Шапка
        self.red_frame = tk.Frame(self.master, bg="#810000", height=110)
        self.red_frame.pack(fill=tk.X)

        # Заголовок "МедСтрах"
        self.title_label = tk.Label(self.red_frame, text="МЕДСТРАХ", font=("Impact", 48, "bold"), fg="white", bg="#810000")
        self.title_label.pack(pady=20)
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        self.user_data = self.load_user_data()  # Загружаем данные пользователя после создания шапки

        # Проверяем, есть ли уже информация в базе данных
        if self.user_data['full_name'] and self.user_data['birth_date'] and self.user_data['passport_series'] and self.user_data['passport_number']:
            # Если данные уже есть, сразу переходим на страницу успеха
            self.open_main_page()
            return  # Важно: выходим из конструктора, чтобы не создавать интерфейс
        else:
            self.create_widgets()  # Создаем интерфейс, если данных нет

    def entry_with_placeholder(self, parent, placeholder, width):
        """Создает поле ввода с подсказкой."""
        entry = tk.Entry(parent, fg='#504e4e', bg='#d7d3d3', bd=2, highlightbackground='#810000', highlightcolor='#810000', highlightthickness=2, width=width, font=('Arial', 16))
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, placeholder))
        entry.bind("<FocusOut>", lambda e: self.set_placeholder(e, placeholder))
        return entry

    def clear_placeholder(self, event, placeholder):
        """Очищает подсказку при фокусе."""
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')  # Меняем цвет текста на черный

    def set_placeholder(self, event, placeholder):
        """Устанавливает подсказку, если поле пустое."""
        if event.widget.get() == "":
            event.widget.insert(0, placeholder)
            event.widget.config(fg='#504e4e')  # Меняем цвет текста на серый

    def create_widgets(self):
        """Создает элементы интерфейса."""
        # Заголовок
        tk.Label(self.master, text="Подать заявку", font=("Arial", 24), bg='white').pack(pady=10)

        # Данные пользователя (email, phone)
        self.create_user_info_section()

        # Поля для ввода информации
        self.full_name_entry = self.entry_with_placeholder(self.master, "ФИО полностью", 30)
        self.full_name_entry.pack(pady=5)

        self.birth_date_entry = self.entry_with_placeholder(self.master, "Дата рождения", 30)
        self.birth_date_entry.pack(pady=5)

        self.passport_series_entry = self.entry_with_placeholder(self.master, "Серия паспорта", 30)
        self.passport_series_entry.pack(pady=5)

        self.passport_number_entry = self.entry_with_placeholder(self.master, "Номер паспорта", 30)
        self.passport_number_entry.pack(pady=5)

        # Кнопка "Подать"
        tk.Button(self.master, text="Подать", command=self.submit_application, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightthickness=2, width=20, height=1, font=('Russo One', 14)).pack(pady=10)

    def create_user_info_section(self):
        """Создает секцию для отображения email и phone."""
        frame = tk.Frame(self.master, bg='white')
        frame.pack(pady=5)

        # Email Frame
        email_frame = tk.Frame(frame, bg='white')
        email_frame.pack(pady=2)

        # Email
        email_label = tk.Label(email_frame, text="Email: ", font=("Arial", 16), bg='white')
        email_label.pack(side=tk.LEFT)

        self.email_value_label = tk.Label(email_frame, text=self.user_data['email'], font=("Arial", 16), bg='white')
        self.email_value_label.pack(side=tk.LEFT)

        # Phone Frame
        phone_frame = tk.Frame(frame, bg='white')
        phone_frame.pack(pady=2)

        # Phone
        phone_label = tk.Label(phone_frame, text="Телефон: ", font=("Arial", 16), bg='white')
        phone_label.pack(side=tk.LEFT)

        self.phone_value_label = tk.Label(phone_frame, text=self.user_data['phone'], font=("Arial", 16), bg='white')
        self.phone_value_label.pack(side=tk.LEFT)

    def load_user_data(self):
        """Загружает данные пользователя из базы данных."""
        try:
            conn = sqlite3.connect('medicine.db')
            cursor = conn.cursor()
            cursor.execute('SELECT email, phone, full_name, birth_date, passport_series, passport_number FROM users WHERE username = ? AND password = ?', (self.username, self.password))
            row = cursor.fetchone()
            conn.close()

            if row:
                # Возвращаем данные пользователя в виде словаря
                return {
                    'email': row[0],
                    'phone': row[1],
                    'full_name': row[2],
                    'birth_date': row[3],
                    'passport_series': row[4],
                    'passport_number': row[5]
                }
            else:
                # Если данные не найдены, возвращаем пустой словарь
                return {
                    'email': '',
                    'phone': '',
                    'full_name': '',
                    'birth_date': '',
                    'passport_series': '',
                    'passport_number': ''
                }
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных пользователя: {e}")
            return {
                    'email': '',
                    'phone': '',
                    'full_name': '',
                    'birth_date': '',
                    'passport_series': '',
                    'passport_number': ''
                }

    def submit_application(self):
        """Обрабатывает отправку заявки."""
        full_name = self.full_name_entry.get()
        birth_date = self.birth_date_entry.get()
        passport_series = self.passport_series_entry.get()
        passport_number = self.passport_number_entry.get()

        # Значения placeholder
        full_name_placeholder = "ФИО полностью"
        birth_date_placeholder = "Дата рождения"
        passport_series_placeholder = "Серия паспорта"
        passport_number_placeholder = "Номер паспорта"

        # Проверка, что поля не содержат текст placeholder
        if (full_name == full_name_placeholder or
            birth_date == birth_date_placeholder or
            passport_series == passport_series_placeholder or
            passport_number == passport_number_placeholder):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        if not all([full_name, birth_date, passport_series, passport_number]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Обновляем данные в базе данных
        try:
            conn = sqlite3.connect('medicine.db')
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET full_name=?, birth_date=?, passport_series=?, passport_number=? WHERE username=? AND password=?',
                (full_name, birth_date, passport_series, passport_number, self.username, self.password)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Заявка успешно подана!")
            self.open_main_page()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {e}")

    def open_main_page(self):
        """Открывает страницу успеха."""
        # Закрываем текущее окно
        self.master.destroy()
        # Запускаем файл main_page.py, передавая имя пользователя
        subprocess.Popen(["python", MAIN_PAGE_FILENAME, self.username, self.password])

def main():
    root = tk.Tk()
    # Получаем имя пользователя из аргументов командной строки
    username = sys.argv[1]
    password = sys.argv[2]
    MainPage(root, username, password)
    root.mainloop()

if __name__ == "__main__":
    main()