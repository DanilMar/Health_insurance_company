import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys

class AdministrationModule:
    def __init__(self, master, username, password):
        self.master = master
        self.master.title("Модуль администрирования")
        self.master.iconbitmap("med.ico")
        self.username = username
        self.password = password
        self.master.geometry(f"{1920}x{1080}")  # Размер окна
        self.master.state('zoomed')
        self.selected_policy_id = None

        # Подключение к базе данных
        self.conn = sqlite3.connect('medicine.db')
        self.cursor = self.conn.cursor()

        self.create_widgets()
        self.load_users_data()
        self.load_insurance_policies_data()

    def create_widgets(self):
        # Кнопка "Выйти"
        self.exit_button = tk.Button(self.master, text="Выйти", command=self.exit_program, bg='white', fg='black', relief='solid', highlightbackground='#810000',
                                     highlightthickness=2, width=12, height=1, font=('Russo One', 14))
        self.exit_button.place(relx=0.0, rely=0.0, anchor='nw')

        # Заголовок
        tk.Label(self.master, text="Модуль администрирования", font=("Arial", 16, "bold")).pack(pady=10)

        # --- Таблица пользователей ---
        tk.Label(self.master, text="Пользователи", font=("Arial", 14)).pack()
        self.users_tree = ttk.Treeview(self.master, columns=(
            "id", "Логин", "Пароль", "Email", "Телефон", "ФИО", "Дата рождения", "Серия паспорта", "Номер паспорта", "Номер договора", "Номер страховки", "Дата окончания страховки"),
                                        show="headings")
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("Логин", text="Логин")
        self.users_tree.heading("Пароль", text="Пароль")
        self.users_tree.heading("Email", text="Email")
        self.users_tree.heading("Телефон", text="Телефон")
        self.users_tree.heading("ФИО", text="ФИО")
        self.users_tree.heading("Дата рождения", text="Дата рождения")
        self.users_tree.heading("Серия паспорта", text="Серия паспорта")
        self.users_tree.heading("Номер паспорта", text="Номер паспорта")
        self.users_tree.heading("Номер договора", text="Номер договора")
        self.users_tree.heading("Номер страховки", text="Номер страховки")
        self.users_tree.heading("Дата окончания страховки", text="Дата окончания страховки")

        self.users_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- Таблица страховок ---
        tk.Label(self.master, text="Страховки", font=("Arial", 14)).pack()
        self.insurance_policies_tree = ttk.Treeview(self.master, columns=(
            "id", "Тип", "Описание", "Срок (мес)", "Цена", "Выплата"), show="headings")
        self.insurance_policies_tree.heading("id", text="ID")
        self.insurance_policies_tree.heading("Тип", text="Тип")
        self.insurance_policies_tree.heading("Описание", text="Описание")
        self.insurance_policies_tree.heading("Срок (мес)", text="Срок (мес)")
        self.insurance_policies_tree.heading("Цена", text="Цена")
        self.insurance_policies_tree.heading("Выплата", text="Выплата")
        self.insurance_policies_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.insurance_policies_tree.bind("<ButtonRelease-1>", self.select_item)
        for col in ["id", "Логин", "Пароль", "Email", "Телефон", "ФИО", "Дата рождения", "Серия паспорта",
                    "Номер паспорта", "Номер договора", "Номер страховки", "Дата окончания страховки"]:
            self.users_tree.column(col, stretch=True, width=100)

        # Кнопки для управления страховками
        self.edit_button = tk.Button(self.master, text="Редактировать", command=self.edit_insurance_policy, state=tk.DISABLED, bg='white', fg='black', relief='solid', highlightbackground='#810000',
                                     highlightthickness=2, width=12, height=1, font=('Russo One', 14))
        self.edit_button.pack(side=tk.LEFT, padx=5)
        self.add_button = tk.Button(self.master, text="Добавить", command=self.add_insurance_policy, bg='white', fg='black', relief='solid', highlightbackground='#810000',
                                     highlightthickness=2, width=12, height=1, font=('Russo One', 14))
        self.add_button.pack(side=tk.LEFT, padx=5)

    def load_users_data(self):
        """Загружает данные пользователей в таблицу."""
        try:
            self.users_tree.delete(*self.users_tree.get_children())  # Очищаем таблицу

            self.cursor.execute("SELECT id, username, password, email, phone, full_name, birth_date, passport_series, passport_number, contract_number, insurance_number, date FROM users WHERE username != 'admin'")
            users = self.cursor.fetchall()

            for user in users:
                self.users_tree.insert("", tk.END, values=user)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных пользователей: {e}")

    def load_insurance_policies_data(self):
        """Загружает данные о страховках в таблицу."""
        try:
            self.insurance_policies_tree.delete(*self.insurance_policies_tree.get_children())  # Очищаем таблицу

            self.cursor.execute("SELECT id, coverage_type, coverage_desc, duration_months, price, payout_amount FROM insurance_policies")
            policies = self.cursor.fetchall()

            for policy in policies:
                self.insurance_policies_tree.insert("", tk.END, values=policy)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных о страховках: {e}")

    def select_item(self, event):
        try:
            selected_item = self.insurance_policies_tree.selection()[0]
            item_details = self.insurance_policies_tree.item(selected_item)
            self.selected_policy_id = item_details['values'][0]
            self.edit_button.config(state=tk.NORMAL)

        except IndexError:
            pass

    def edit_insurance_policy(self):
        """Открывает окно для редактирования выбранной страховки."""
        if self.selected_policy_id is None:
            messagebox.showerror("Ошибка", "Выберите страховку для редактирования.")
            return

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Редактировать страховку")
        self.center_window(edit_window, 400, 230)  # Центрируем окно
        edit_window.configure(bg="#f0f0f0")  # Задаем фон

        # Получаем данные о выбранной страховке
        self.cursor.execute("SELECT coverage_type, coverage_desc, duration_months, price, payout_amount FROM insurance_policies WHERE id = ?", (self.selected_policy_id,))
        policy_data = self.cursor.fetchone()

         # Стили для Label
        label_style = {"font": ("Arial", 12), "bg": "#f0f0f0"}

        # Стили для Entry
        entry_style = {"font": ("Arial", 12), "width": 30}

        # Создаем поля для редактирования
        tk.Label(edit_window, text="Тип:", **label_style).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        coverage_type_entry = tk.Entry(edit_window, **entry_style)
        coverage_type_entry.insert(0, policy_data[0])
        coverage_type_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(edit_window, text="Описание:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        coverage_desc_entry = tk.Entry(edit_window, **entry_style)
        coverage_desc_entry.insert(0, policy_data[1])
        coverage_desc_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(edit_window, text="Срок (мес):", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        duration_months_entry = tk.Entry(edit_window, **entry_style)
        duration_months_entry.insert(0, policy_data[2])
        duration_months_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(edit_window, text="Цена:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        price_entry = tk.Entry(edit_window, **entry_style)
        price_entry.insert(0, policy_data[3])
        price_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(edit_window, text="Выплата:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        payout_amount_entry = tk.Entry(edit_window, **entry_style)
        payout_amount_entry.insert(0, policy_data[4])
        payout_amount_entry.grid(row=4, column=1, padx=10, pady=5)

        def save_changes():
            try:
                coverage_type = coverage_type_entry.get()
                coverage_desc = coverage_desc_entry.get()
                duration_months = int(duration_months_entry.get())
                price = float(price_entry.get())
                payout_amount = float(payout_amount_entry.get())

                self.cursor.execute("""
                    UPDATE insurance_policies
                    SET coverage_type = ?, coverage_desc = ?, duration_months = ?, price = ?, payout_amount = ?
                    WHERE id = ?
                """, (coverage_type, coverage_desc, duration_months, price, payout_amount, self.selected_policy_id))
                self.conn.commit()

                messagebox.showinfo("Успех", "Страховка успешно отредактирована.")
                edit_window.destroy()
                self.load_insurance_policies_data()  # Обновляем таблицу
                self.edit_button.config(state=tk.DISABLED)
                self.selected_policy_id = None

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при редактировании страховки: {e}")

        save_button = tk.Button(edit_window, text="Сохранить", command=save_changes, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightcolor='#810000', highlightthickness=2, width=9, height=1, font=('Russo One', 14))
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

    def add_insurance_policy(self):
        """Открывает окно для добавления новой страховки."""
        add_window = tk.Toplevel(self.master)
        add_window.title("Добавить страховку")
        self.center_window(add_window, 400, 230)  # Центрируем окно
        add_window.configure(bg="#f0f0f0")  # Задаем фон

         # Стили для Label
        label_style = {"font": ("Arial", 12), "bg": "#f0f0f0"}

        # Стили для Entry
        entry_style = {"font": ("Arial", 12), "width": 30}

        # Создаем поля для ввода данных
        tk.Label(add_window, text="Тип:", **label_style).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        coverage_type_entry = tk.Entry(add_window, **entry_style)
        coverage_type_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Описание:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        coverage_desc_entry = tk.Entry(add_window, **entry_style)
        coverage_desc_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Срок (мес):", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        duration_months_entry = tk.Entry(add_window, **entry_style)
        duration_months_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Цена:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        price_entry = tk.Entry(add_window, **entry_style)
        price_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Выплата:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        payout_amount_entry = tk.Entry(add_window, **entry_style)
        payout_amount_entry.grid(row=4, column=1, padx=10, pady=5)

        def add_policy():
            try:
                coverage_type = coverage_type_entry.get()
                coverage_desc = coverage_desc_entry.get()
                duration_months = int(duration_months_entry.get())
                price = float(price_entry.get())
                payout_amount = float(payout_amount_entry.get())

                # Получаем id последней страховки
                self.cursor.execute("SELECT MAX(id) FROM insurance_policies")
                last_id = self.cursor.fetchone()[0]
                new_id = 1 if last_id is None else last_id + 1 #Если это первая страховка

                self.cursor.execute("""
                    INSERT INTO insurance_policies (id, coverage_type, coverage_desc, duration_months, price, payout_amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (new_id, coverage_type, coverage_desc, duration_months, price, payout_amount))
                self.conn.commit()

                messagebox.showinfo("Успех", "Страховка успешно добавлена.")
                add_window.destroy()
                self.load_insurance_policies_data()  # Обновляем таблицу

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении страховки: {e}")

        # Стили для Button
        button_style = {"font": ("Arial", 12), "bg": "#4CAF50", "fg": "white", "relief": "raised"}

        add_button = tk.Button(add_window, text="Добавить", command=add_policy, bg='#d24a43', fg='white', relief='solid', highlightbackground='#810000', highlightcolor='#810000', highlightthickness=2, width=9, height=1, font=('Russo One', 14))
        add_button.grid(row=5, column=0, columnspan=2, pady=10)

    def center_window(self, window, width, height):
        """Центрирует окно на экране."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

    def exit_program(self):
        """Закрывает программу."""
        self.conn.close()
        self.master.destroy()


def main():
    root = tk.Tk()
    username = sys.argv[1]
    password = sys.argv[2]
    app = AdministrationModule(root, username, password)
    root.mainloop()


if __name__ == "__main__":
    main()