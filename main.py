import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Jukijuki12!",
            database="KinoDBB"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Błąd połączenia", f"Nie można połączyć z bazą danych: {err}")
        return None

# Rejestracja klienta
def register_client():
    global entry_email, entry_password, entry_first_name, entry_last_name, entry_phone
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Rejestracja klienta").pack()

    tk.Label(root, text="Email:").pack()
    entry_email = tk.Entry(root)
    entry_email.pack()
    tk.Label(root, text="Hasło:").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()
    tk.Label(root, text="Imię:").pack()
    entry_first_name = tk.Entry(root)
    entry_first_name.pack()
    tk.Label(root, text="Nazwisko:").pack()
    entry_last_name = tk.Entry(root)
    entry_last_name.pack()
    tk.Label(root, text="Numer telefonu:").pack()
    entry_phone = tk.Entry(root)
    entry_phone.pack()

    tk.Button(root, text="Zarejestruj się", command=submit_registration).pack()

def submit_registration():
    email = entry_email.get()
    password = entry_password.get()
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    phone = entry_phone.get()

    if not email or not password or not first_name or not last_name or not phone:
        messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione.")
        return

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = "INSERT INTO Klient (email, Imie, Nazwisko, Nr_Tel) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (email, first_name, last_name, phone))
            query_password = "INSERT INTO Uzytkownik (email, haslo) VALUES (%s, %s)"
            cursor.execute(query_password, (email, password))
            connection.commit()
            messagebox.showinfo("Sukces", "Rejestracja zakończona pomyślnie.")
            show_login_view()
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można zarejestrować klienta: {err}")
        finally:
            cursor.close()
            connection.close()
# Logowanie użytkownika (bez zmian)
def login_user():
    email = entry_login_email.get()
    password = entry_login_password.get()
    user_type = user_type_var.get()

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if user_type == "Klient":
                query = "SELECT * FROM Uzytkownik WHERE email = %s AND haslo = %s"
                cursor.execute(query, (email, password))
                result = cursor.fetchone()
                if result:
                    messagebox.showinfo("Sukces", "Zalogowano jako klient. Możesz teraz korzystać z funkcji aplikacji.")
                    show_client_selection_view(email)
                else:
                    messagebox.showerror("Błąd", "Nieprawidłowy email lub hasło.")
            elif user_type == "Admin":
                if email == "admin" and password == "admin":
                    messagebox.showinfo("Sukces", "Zalogowano jako administrator.")
                    show_admin_view()
                else:
                    messagebox.showerror("Błąd", "Nieprawidłowy email lub hasło administratora.")
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można się zalogować: {err}")
        finally:
            cursor.close()
            connection.close()

def show_client_selection_view(client_email):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Wybór biletu na seans i produktu").pack()

    # Lista filmów
    tk.Label(root, text="Wybierz film:").pack()
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT Tytul FROM Film")
            films = [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można pobrać listy filmów: {err}")
            films = []
        finally:
            cursor.close()
            connection.close()

    global film_select
    film_select = ttk.Combobox(root, values=films)
    film_select.pack()

    # Lista seansów
    tk.Label(root, text="Wybierz seans:").pack()
    global seans_select
    seans_select = ttk.Combobox(root, values=[])
    seans_select.pack()

    def update_seans_options(event):
        selected_film = film_select.get()
        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT Seans.ID_Seansu, Seans.Data, Seans.Godzina FROM Seans INNER JOIN Film ON Seans.ID_Seansu = Film.ID_Seansu WHERE Film.Tytul = %s", (selected_film,))
                seans_data = [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
                seans_select["values"] = seans_data
            except mysql.connector.Error as err:
                messagebox.showerror("Błąd", f"Nie można pobrać seansów: {err}")
            finally:
                cursor.close()
                connection.close()

    film_select.bind("<<ComboboxSelected>>", update_seans_options)

    # Lista produktów
    tk.Label(root, text="Wybierz produkt (opcjonalnie):").pack()
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT Nazwa FROM Produkt")
            products = [row[0] for row in cursor.fetchall()]
            products.insert(0, "Brak")
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można pobrać listy produktów: {err}")
            products = ["Brak"]
        finally:
            cursor.close()
            connection.close()

    global product_select
    product_select = ttk.Combobox(root, values=products)
    product_select.pack()

    tk.Button(root, text="Zatwierdź wybór", command=lambda: confirm_selection(client_email)).pack()

def confirm_selection(client_email):
    selected_film = film_select.get()
    selected_seans = seans_select.get()
    selected_product = product_select.get()

    if not selected_film or not selected_seans:
        messagebox.showwarning("Ostrzeżenie", "Musisz wybrać film i seans.")
        return

    # Wyciągnięcie ID seansu
    seans_id = selected_seans.split(" - ")[0]

    # Pobranie ceny biletu
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT Cena FROM Bilet WHERE ID_Seansu = %s LIMIT 1", (seans_id,))
            result_bilet = cursor.fetchone()
            if not result_bilet:
                messagebox.showerror("Błąd", "Brak biletu dla wybranego seansu!")
                return

            bilet_cena = result_bilet[0]
            product_cena = 0

            if selected_product and selected_product != "Brak":
                cursor.execute("SELECT Cena FROM Produkt WHERE Nazwa = %s", (selected_product,))
                product_cena = cursor.fetchone()[0]

            total_cena = bilet_cena + product_cena

            cursor.execute(
                "INSERT INTO Transakcja (ID_Biletu, Nazwa, email, Data, Kwota) VALUES (%s, %s, %s, %s, %s)",
                (seans_id, selected_product if selected_product != "Brak" else "", client_email, datetime.now(), total_cena)
            )
            connection.commit()
            messagebox.showinfo("Sukces", f"Transakcja zapisana! Łączna kwota: {total_cena:.2f} zł.")
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można zapisać transakcji: {err}")
        finally:
            cursor.close()
            connection.close()

# Widok logowania
def show_login_view():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Logowanie").pack()

    tk.Label(root, text="Email:").pack()
    global entry_login_email
    entry_login_email = tk.Entry(root)
    entry_login_email.pack()

    tk.Label(root, text="Hasło:").pack()
    global entry_login_password
    entry_login_password = tk.Entry(root, show="*")
    entry_login_password.pack()

    tk.Label(root, text="Wybierz typ użytkownika:").pack()
    global user_type_var
    user_type_var = tk.StringVar()
    user_type_var.set("Klient")
    tk.Radiobutton(root, text="Klient", variable=user_type_var, value="Klient").pack()
    tk.Radiobutton(root, text="Admin", variable=user_type_var, value="Admin").pack()

    tk.Button(root, text="Zaloguj się", command=login_user).pack()
    tk.Button(root, text="Zarejestruj się", command=register_client).pack()

#  1) RAPORT Z WYKRESEM
def open_chart_filter_window():
    filter_window = tk.Toplevel(root)
    filter_window.title("Filtry - Raport z wykresem suma kwot transakcji")

    tk.Label(filter_window, text="Data od (RRRR-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = tk.Entry(filter_window)
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_window, text="Data do (RRRR-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    end_date_entry = tk.Entry(filter_window)
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)

    def on_confirm():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        filter_window.destroy()
        generate_chart_report_with_filters(start_date, end_date)

    tk.Button(filter_window, text="Generuj", command=on_confirm).grid(row=2, column=0, columnspan=2, pady=10)


def generate_chart_report_with_filters(start_date, end_date):

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            where_clauses = []
            params = []

            if start_date:
                where_clauses.append("Data >= %s")
                params.append(start_date)
            if end_date:
                where_clauses.append("Data <= %s")
                params.append(end_date)

            where_str = " AND ".join(where_clauses)
            if where_str:
                where_str = "WHERE " + where_str

            query = f"""
                SELECT Data, SUM(Kwota) AS Sprzedaż
                FROM Transakcja
                {where_str}
                GROUP BY Data
                ORDER BY Data
            """
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()

            if not data:
                messagebox.showinfo("Brak danych", "Brak wyników dla wybranych filtrów.")
                return

            dates = [str(row[0]) for row in data]  # row[0] to obiekt date, rzutujemy na str
            sales = [row[1] for row in data]

            # Tworzenie okna dla wykresu
            chart_window = tk.Toplevel(root)
            chart_window.title("Raport z wykresem")
            chart_window.geometry("800x600")

            # Tworzenie figury Matplotlib
            fig = Figure(figsize=(8, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(dates, sales, color="blue")
            ax.set_title("Raport z wykresem - Suma Kwot Transakcji", fontsize=14)
            ax.set_xlabel("Data", fontsize=12)
            ax.set_ylabel("Sprzedaż (zł)", fontsize=12)
            ax.tick_params(axis='x', rotation=45)

            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            tk.Button(chart_window, text="Zamknij", command=chart_window.destroy).pack()
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można wygenerować raportu: {err}")
        finally:
            cursor.close()
            connection.close()

#  2) RAPORT W FORMIE FORMULARZA (z dwoma filtrami)
def open_form_filter_window():
    filter_window = tk.Toplevel(root)
    filter_window.title("Filtry - Raport w formie formularza")

    tk.Label(filter_window, text="Imię zawiera:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(filter_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_window, text="Nazwisko zawiera:").grid(row=1, column=0, padx=5, pady=5)
    surname_entry = tk.Entry(filter_window)
    surname_entry.grid(row=1, column=1, padx=5, pady=5)

    def on_confirm():
        name_filter = name_entry.get()
        surname_filter = surname_entry.get()
        filter_window.destroy()
        generate_form_report_with_filters(name_filter, surname_filter)

    tk.Button(filter_window, text="Generuj", command=on_confirm).grid(row=2, column=0, columnspan=2, pady=10)

def generate_form_report_with_filters(name_filter, surname_filter):

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Składamy warunki do WHERE
            where_clauses = []
            params = []

            if name_filter:
                where_clauses.append("Imie LIKE %s")
                params.append(f"%{name_filter}%")
            if surname_filter:
                where_clauses.append("Nazwisko LIKE %s")
                params.append(f"%{surname_filter}%")

            where_str = " AND ".join(where_clauses)
            if where_str:
                where_str = "WHERE " + where_str

            query = f"SELECT * FROM Klient {where_str}"
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            if not data:
                messagebox.showinfo("Brak danych", "Brak wyników dla wybranych filtrów.")
                return

            df = pd.DataFrame(data, columns=columns)

            messagebox.showinfo("Raport w formie formularza", df.to_string(index=False))
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można wygenerować raportu: {err}")
        finally:
            cursor.close()
            connection.close()

#  3) RAPORT Z GRUPOWANIEM
def open_grouping_filter_window():

    filter_window = tk.Toplevel(root)
    filter_window.title("Filtry - Raport z grupowaniem")

    tk.Label(filter_window, text="ID_Kino od:").grid(row=0, column=0, padx=5, pady=5)
    kino_from_entry = tk.Entry(filter_window)
    kino_from_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_window, text="ID_Kino do:").grid(row=1, column=0, padx=5, pady=5)
    kino_to_entry = tk.Entry(filter_window)
    kino_to_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filter_window, text="Minimalna suma wynagrodzeń:").grid(row=2, column=0, padx=5, pady=5)
    min_sum_entry = tk.Entry(filter_window)
    min_sum_entry.grid(row=2, column=1, padx=5, pady=5)

    def on_confirm():
        kino_from = kino_from_entry.get()
        kino_to = kino_to_entry.get()
        min_sum = min_sum_entry.get()
        filter_window.destroy()
        generate_grouping_report_with_filters(kino_from, kino_to, min_sum)

    tk.Button(filter_window, text="Generuj", command=on_confirm).grid(row=3, column=0, columnspan=2, pady=10)

def generate_grouping_report_with_filters(kino_from, kino_to, min_sum):

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if not kino_from:
                kino_from = "1"
            if not kino_to:
                kino_to = "9999"
            if not min_sum:
                min_sum = "0"

            query = f"""
                SELECT Kino.ID_Kino, Kino.Nazwa_kina, SUM(Pracownik.Wyplata) AS Wynagrodzenia
                FROM Pracownik
                INNER JOIN Kino ON Pracownik.ID_Kino = Kino.ID_Kino
                WHERE Kino.ID_Kino BETWEEN %s AND %s
                GROUP BY Kino.ID_Kino, Kino.Nazwa_kina
                HAVING SUM(Pracownik.Wyplata) >= %s
                ORDER BY Kino.ID_Kino
            """
            cursor.execute(query, (kino_from, kino_to, min_sum))
            data = cursor.fetchall()

            if not data:
                messagebox.showinfo("Brak danych", "Brak wyników dla wybranych filtrów.")
                return

            report = ""
            for row in data:
                report += f"Kino ID: {row[0]}, Nazwa: {row[1]}, Suma wynagrodzeń: {row[2]} zł\n"

            messagebox.showinfo("Raport z grupowaniem", report)
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można wygenerować raportu: {err}")
        finally:
            cursor.close()
            connection.close()

# Panel administratora
def show_admin_view():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Panel administratora").pack()

    # Wybór tabeli
    tk.Label(root, text="Wybierz tabelę:").pack()
    global table_select
    table_select = ttk.Combobox(root, values=[
        "Kino", "Adres", "Pracownik", "Kierownik", "Sprzedawca", "Ochroniarz", "Sprzatacz",
        "Seans", "Sala", "Film", "Bilet", "Klient", "Produkt", "Transakcja"
    ])
    table_select.pack()

    # Przyciski
    tk.Button(root, text="Pokaż dane", command=show_data).pack()
    tk.Label(root, text="Dodaj dane (wpisz wartości rozdzielone przecinkiem):").pack()
    global entry_values
    entry_values = tk.Entry(root, width=50)
    entry_values.pack()
    tk.Button(root, text="Dodaj dane", command=add_data).pack()
    tk.Button(root, text="Usuń zaznaczone dane", command=delete_data).pack()

    tk.Label(root, text="Generowanie raportów:").pack()
    tk.Button(root, text="Raport z wykresem (filtry)", command=open_chart_filter_window).pack()
    tk.Button(root, text="Raport w formie formularza (filtry)", command=open_form_filter_window).pack()
    tk.Button(root, text="Raport z grupowaniem (filtry)", command=open_grouping_filter_window).pack()

    # Tabela danych
    global tree
    tree = ttk.Treeview(root)
    tree.pack(expand=True, fill="both")

    show_data()

def show_data():
    selected_table = table_select.get()
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if not selected_table:
                messagebox.showwarning("Ostrzeżenie", "Proszę wybrać tabelę.")
                return
            cursor.execute(f"SELECT * FROM {selected_table}")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            for item in tree.get_children():
                tree.delete(item)

            tree["columns"] = columns
            tree["show"] = "headings"

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            for row in rows:
                tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można wyświetlić danych: {err}")
        finally:
            cursor.close()
            connection.close()

def add_data():
    selected_table = table_select.get()
    values = entry_values.get()
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if not selected_table or not values:
                messagebox.showwarning("Ostrzeżenie", "Proszę wybrać tabelę i wprowadzić dane.")
                return
            query = f"INSERT INTO {selected_table} VALUES ({values})"
            cursor.execute(query)
            connection.commit()
            messagebox.showinfo("Sukces", "Dane zostały dodane.")
            show_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można dodać danych: {err}")
        finally:
            cursor.close()
            connection.close()

def delete_data():
    selected_table = table_select.get()
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Błąd", "Nie wybrano rekordu do usunięcia.")
        return
    values = tree.item(selected_item)["values"]
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            primary_key = tree["columns"][0]
            query = f"DELETE FROM {selected_table} WHERE {primary_key} = %s"
            cursor.execute(query, (values[0],))
            connection.commit()
            messagebox.showinfo("Sukces", "Dane zostały usunięte.")
            show_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Błąd", f"Nie można usunąć danych: {err}")
        finally:
            cursor.close()
            connection.close()

# Główne okno
root = tk.Tk()
root.title("Kino Paweł Ciepłuch")
root.geometry("600x600")
show_login_view()
root.mainloop()
