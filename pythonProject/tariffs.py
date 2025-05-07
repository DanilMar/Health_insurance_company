import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
from tkinter import scrolledtext
from datetime import datetime, timedelta
import subprocess
from PIL import Image, ImageTk

class InsuranceApp:
    def __init__(self, master, username, password):
        self.master = master
        self.username = username
        self.password = password
        self.master.iconbitmap("med.ico")
        self.master.title("Медицинская страховка")
        self.master.geometry(f"{1920}x{1080}")  # Установим размер окна
        self.master.state('zoomed')
        self.master.config(bg='white')  # Задаём белый фон для основного окна

        self.conn = sqlite3.connect('medicine.db')
        self.cursor = self.conn.cursor()

        self.selected_policy_id = None
        self.menu_open = False  # Добавляем переменную для отслеживания состояния меню
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
        menu_icon = Image.open("menu.png")  # Укажите правильный путь к вашей иконке
        menu_photo = ImageTk.PhotoImage(menu_icon)
        support_icon = Image.open("support.png")  # Укажите правильный путь к вашей иконке
        support_photo = ImageTk.PhotoImage(support_icon)
        user_icon = Image.open("user.png")  # Укажите правильный путь к вашей иконке
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

        # Заголовок "Привет"
        self.hello_label = tk.Label(self.master, text=f"Привет, {self.username}!", font=("Arial", 16, "bold"),
                                     bg="white")
        self.hello_label.pack(pady=10)

        # Стиль для Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 12))
        style.configure("Treeview", font=('Arial', 12), rowheight=25)


        # Treeview для отображения данных
        self.tree = ttk.Treeview(self.master, columns=("id", "Тип", "Описание", "Срок (мес)", "Цена", "Выплата"),
                                 show="headings", style="Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Срок (мес)", text="Срок (мес)")
        self.tree.heading("Цена", text="Цена")
        self.tree.heading("Выплата", text="Выплата")

        self.tree.column("id", width=30)
        self.tree.column("Тип", width=150)
        self.tree.column("Описание", width=400)
        self.tree.column("Срок (мес)", width=50)
        self.tree.column("Цена", width=70)
        self.tree.column("Выплата", width=100)

        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.tree.bind("<ButtonRelease-1>", self.select_item)

        self.load_data()

        # Кнопка "Оформить"
        self.buy_button = tk.Button(self.master, text="Оформить", command=self.buy_insurance, state=tk.DISABLED,
                                     bg='white', fg='black', relief='solid', highlightbackground='#810000',
                                     highlightthickness=2, width=12, height=1, font=('Russo One', 14))
        self.buy_button.pack(pady=10)

        self.menu_frame = None


    def load_data(self):
        self.cursor.execute(
            "SELECT id, coverage_type, coverage_desc, duration_months, price, payout_amount FROM insurance_policies")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def select_item(self, event):
        try:
            selected_item = self.tree.selection()[0]
            item_details = self.tree.item(selected_item)
            self.selected_policy_id = item_details['values'][0]
            self.buy_button.config(state=tk.NORMAL)

        except IndexError:
            pass

    def buy_insurance(self):
        if self.selected_policy_id is None:
            messagebox.showerror("Ошибка", "Выберите полис для оформления")
            return

        # Проверка, оформлена ли страховка
        self.cursor.execute("SELECT insurance_number, date FROM users WHERE username = ?", (self.username,))
        result = self.cursor.fetchone()

        if result and result[0]:
            messagebox.showerror("Ошибка",
                                 "Одна страховка уже оформлена. Чтобы оформить другую страховку, необходимо аннулировать имеющуюся страховку. Для этого перейдите в 'Мой договор'")
            return

        # Открытие окна оплаты
        self.open_payment_window(self.selected_policy_id)

    def open_payment_window(self, policy_id):
        payment_window = tk.Toplevel(self.master)
        payment_window.title("Оплата страховки")
        payment_window.geometry("300x200")
        payment_window.transient(self.master)
        payment_window.grab_set()
        payment_window.attributes('-topmost', True)

        tk.Label(payment_window, text="Номер карты:", font=("Arial", 12)).pack()
        card_number_entry = tk.Entry(payment_window, font=("Arial", 12))
        card_number_entry.pack()

        tk.Label(payment_window, text="Пин код:", font=("Arial", 12)).pack()
        pin_code_entry = tk.Entry(payment_window, show="*", font=("Arial", 12))
        pin_code_entry.pack()

        def pay():
            card_number = card_number_entry.get()
            pin_code = pin_code_entry.get()

            if not card_number or not pin_code:
                messagebox.showerror("Ошибка", "Необходимо заполнить все поля")
                payment_window.attributes('-topmost', True)
                return

            # Получаем цену и длительность страховки
            self.cursor.execute("SELECT price, duration_months FROM insurance_policies WHERE id = ?", (policy_id,))
            policy_info = self.cursor.fetchone()

            if not policy_info:
                messagebox.showerror("Ошибка", "Полис не найден.")
                return

            price, duration_months = policy_info
            messagebox.showinfo("Успех", f"Оплата успешна! Вы заплатили {price} рублей")

            # Рассчитываем дату окончания страховки
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30 * duration_months)
            end_date_str = end_date.strftime('%Y-%m-%d')

            # Обновляем данные пользователя
            self.cursor.execute(
                "UPDATE users SET insurance_number = ?, date = ? WHERE username = ?",
                (policy_id, end_date_str, self.username)
            )
            self.conn.commit()

            payment_window.destroy()

        pay_button = tk.Button(payment_window, text="Оплатить", command=pay, bg='#d24a43', fg='white', relief='solid',
                                highlightbackground='#810000', highlightthickness=2, width=12, height=1,
                                font=('Russo One', 14))
        pay_button.pack(pady=10)

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
        self.menu_frame.place(x=0, y=0)

        # Создаем кнопки
        button_width = 280  # Ширина кнопок
        button_x = 10  # Отступ от края

        self.tariffs_button = tk.Button(self.menu_frame, text="Тарифы страхования", command=self.open_tariffs,
                                        bg='#640101', fg='white', relief='solid', highlightthickness=0, borderwidth=0,
                                        width=20, height=1, font=('Arial', 14, 'bold'))
        self.tariffs_button.place(x=button_x, y=50)

        self.my_contracts_button = tk.Button(self.menu_frame, text="Мой договор", command=self.open_my_contracts, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.my_contracts_button.place(x=button_x, y=100)

        self.payment_button = tk.Button(self.menu_frame, text="Расчёт выплат", command=self.open_payment, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.payment_button.place(x=button_x, y=150)

        self.exit_button = tk.Button(self.menu_frame, text="Выход", command=self.exit_program, bg='#640101', fg='white', relief='solid', highlightthickness=0,  borderwidth=0, width=20, height=1, font=('Arial', 14, 'bold'))
        self.exit_button.place(x=button_x, y=main_height - 50)

    def hide_menu(self):
        """Скрывает меню."""
        self.menu_open = False
        self.menu_frame.destroy()

    def open_tariffs(self):
        """Открывает файл тарифов."""
        subprocess.Popen(["python", "tariffs.py", self.username, self.password])
        self.master.destroy()

    def open_my_contracts(self):
        """Открывает окно моих договоров."""
        subprocess.Popen(["python", "my_contracts.py", self.username, self.password])
        self.master.destroy()

    def open_payment(self):
        """Открывает окно расчёта выплат."""
        subprocess.Popen(["python", "payment.py", self.username, self.password])
        self.master.destroy()

    def open_main_page(self):
        subprocess.Popen(["python", "main_page.py", self.username, self.password])
        self.master.destroy()

    def open_support_chat(self):
        """Открывает окно с чатом поддержки."""
        support_window = tk.Toplevel(self.master)
        support_window.title("Чат с поддержкой")

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

        self.chat_log = scrolledtext.ScrolledText(support_window, wrap=tk.WORD, state=tk.DISABLED,
                                                    bg="#ffffff", font=("Arial", 12))  # Шрифт и фон текста
        self.chat_log.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        input_frame = tk.Frame(support_window, bg="#f0f0f0")  # Фон фрейма
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.message_entry = tk.Entry(input_frame, font=("Arial", 12))  # Шрифт поля ввода
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        send_button = tk.Button(input_frame, text="Отправить", command=self.send_message, bg='white', fg='black',
                                 relief='solid', highlightbackground='#810000', highlightthickness=2, width=10,
                                 height=1, font=('Russo One', 10))  # Стиль кнопки
        send_button.pack(side=tk.RIGHT)

        self.support_window = support_window

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.insert(tk.END, f"Вы: {message}\n")
            self.chat_log.config(state=tk.DISABLED)

            self.message_entry.delete(0, tk.END)
            self.master.after(2000, self.add_support_response)
            self.chat_log.see(tk.END)

    def add_support_response(self):
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
    app = InsuranceApp(root, username, password)
    root.mainloop()


if __name__ == "__main__":
    main()