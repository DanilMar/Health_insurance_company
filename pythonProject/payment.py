import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys
from tkinter import scrolledtext
import subprocess
from PIL import Image, ImageTk

class PaymentWindow:
    def __init__(self, master, username, password):
        self.master = master
        self.username = username
        self.password = password
        self.master.iconbitmap("med.ico")
        self.master.title("Расчёт выплат")
        self.master.geometry(f"{1920}x{1080}")  # Установим размер окна
        self.master.state('zoomed')
        self.master.config(bg='white')

        self.conn = sqlite3.connect('medicine.db')
        self.cursor = self.conn.cursor()
        self.arial_12 = ("Arial", 12)
        self.menu_open = False

        self.create_widgets()

    def create_widgets(self):
        # Шапка
        self.red_frame = tk.Frame(self.master, bg="#810000", height=110)
        self.red_frame.pack(fill=tk.X)

        # Заголовок "Медстрах"
        self.title_label = tk.Label(self.red_frame, text="МЕДСТРАХ", font=("Impact", 48, "bold"), fg="white",
                                     bg="#810000")
        self.title_label.pack(pady=20)
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Загрузка иконок
        menu_icon = Image.open("menu.png")
        menu_photo = ImageTk.PhotoImage(menu_icon)
        support_icon = Image.open("support.png")
        support_photo = ImageTk.PhotoImage(support_icon)
        user_icon = Image.open("user.png")
        user_photo = ImageTk.PhotoImage(user_icon)

        # Кнопка Меню в левом верхнем углу
        self.menu_button = tk.Button(self.master, image=menu_photo, command=self.toggle_menu, bg='#810000',
                                 activebackground='white', relief='flat')
        self.menu_button.image = menu_photo  # Сохраняем ссылку на объект изображения
        self.menu_button.place(x=0, y=-6)

        # Кнопка поддержки в правом верхнем углу
        self.support_button = tk.Button(self.master, image=support_photo, command=self.open_support_chat, bg='#810000',
                                    activebackground='white', relief='flat')
        self.support_button.image = support_photo  # Сохраняем ссылку на объект изображения
        self.support_button.place(x=1160, y=-6)

        # Кнопка пользователя в правом верхнем углу
        self.user_button = tk.Button(self.master, image=user_photo, command=self.open_main_page, bg='#810000',
                                    activebackground='white', relief='flat')
        self.user_button.image = user_photo  # Сохраняем ссылку на объект изображения
        self.user_button.place(x=1040, y=-6)

        # Заголовок "Расчёт выплат"
        self.payment_label = tk.Label(self.master, text="Расчёт выплат".upper(), font=("Arial", 16, "bold"), bg="white")
        self.payment_label.pack(pady=15)

        # Область для вывода информации о страховке и выплате
        self.info_label = tk.Label(self.master, text="", justify=tk.LEFT, font=self.arial_12, bg="white")
        self.info_label.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Кнопка "Получить выплату"
        self.claim_button = tk.Button(self.master, text="Получить выплату", command=self.show_claim_message, bg='white', fg='black', relief='solid', highlightbackground='#810000', highlightthickness=2, width=20, height=1, font=('Russo One', 14))
        self.claim_button.pack(pady=10)
        self.claim_button.config(state=tk.DISABLED)

        self.load_payment_info()

        self.menu_frame = None

    def load_payment_info(self):
        # Получаем номер страховки пользователя
        self.cursor.execute("SELECT insurance_number FROM users WHERE username = ?", (self.username,))
        result = self.cursor.fetchone()

        if result and result[0]:
            insurance_number = result[0]

            # Получаем информацию о страховке
            self.cursor.execute("""
                SELECT coverage_type, coverage_desc, payout_amount
                FROM insurance_policies
                WHERE id = ?
            """, (insurance_number,))
            contract_info = self.cursor.fetchone()

            if contract_info:
                # Формируем текст для отображения
                coverage_type, coverage_desc, payout_amount = contract_info
                info_text = f"Тип страховки: {coverage_type}\n\n"
                info_text += f"Условия страховки: {coverage_desc}\n\n"
                info_text += f"Сумма выплаты: {payout_amount}"

                self.info_label.config(text=info_text)
                self.claim_button.config(state=tk.NORMAL)
            else:
                self.info_label.config(text="Произошла ошибка при загрузке данных о страховке.")

        else:
            self.info_label.config(text="Вы пока не оформили страховку")

    def show_claim_message(self):
        # Сообщение для получения выплаты
        messagebox.showinfo(
            "Получение выплаты",
            "Для получения выплаты за страховку необходимо очно явится в нашу клинику для подтверждения условий страхования. Адрес: г.Барнаул, ул. Путиловская д. 53, к.417"
        )

    def toggle_menu(self):
        if self.menu_open:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        """Отображает меню."""
        self.menu_open = True
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

        self.contracts_button = tk.Button(self.menu_frame, text="Мой договор", command=self.open_my_contracts, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.contracts_button.place(x=button_x, y=100)

        self.payment_button = tk.Button(self.menu_frame, text="Расчёт выплат", command=self.open_payment, bg='#640101',
                                        fg='white', relief='solid', highlightthickness=0, borderwidth=0, width=20,
                                        height=1, font=('Arial', 14, 'bold'))
        self.payment_button.place(x=button_x, y=150)

        # Кнопка Выход
        self.exit_button = tk.Button(self.menu_frame, text="Выход", command=self.exit_program, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.exit_button.place(x=button_x, y=main_height - 50)  # Размещаем внизу

    def hide_menu(self):
        """Скрывает меню."""
        self.menu_open = False
        self.menu_frame.destroy()

    def open_tariffs(self):
        """Открывает окно тарифов."""
        subprocess.Popen(["python", "tariffs.py", self.username, self.password])
        self.master.destroy()

    def open_my_contracts(self):
        """Открывает окно моего договора."""
        subprocess.Popen(["python", "my_contracts.py", self.username, self.password])
        self.master.destroy()

    def open_payment(self):
        """Открывает файл расчёта выплат."""
        subprocess.Popen(["python", "payment.py", self.username, self.password])
        self.master.destroy()

    def open_main_page(self):
        """Открывает файл главной страницы выплат."""
        subprocess.Popen(["python", "main_page.py", self.username, self.password])
        self.master.destroy()

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

        # Задаём фон окна поддержки
        support_window.configure(bg="#f0f0f0")

        # Текстовое поле для отображения сообщений (с возможностью прокрутки)
        self.chat_log = scrolledtext.ScrolledText(support_window, wrap=tk.WORD, state=tk.DISABLED,
                                                    bg="#ffffff", font=self.arial_12)  # Шрифт и фон текста
        self.chat_log.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Фрейм для поля ввода и кнопки отправки
        input_frame = tk.Frame(support_window, bg="#f0f0f0")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Поле ввода для нового сообщения
        self.message_entry = tk.Entry(input_frame, font=self.arial_12)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Кнопка отправки сообщения
        send_button = tk.Button(input_frame, text="Отправить", command=self.send_message, bg='white', fg='black',
                                 relief='solid', highlightbackground='#810000', highlightthickness=2, width=10,
                                 height=1, font=('Russo One', 10))
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

    def exit_program(self):
        """Закрывает программу."""
        self.conn.close()
        self.master.destroy()

def main():
    root = tk.Tk()
    username = sys.argv[1]
    password = sys.argv[2]
    app = PaymentWindow(root, username, password)
    root.mainloop()

if __name__ == "__main__":
    main()