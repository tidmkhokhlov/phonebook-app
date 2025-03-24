from flask import Flask, request, render_template, redirect, url_for
from psycopg import connect, sql, errors
import re

app = Flask(__name__)

# Функция для проверки номера телефона
def validate_phone_number(phone_number):
    # Проверяем, что номер состоит только из цифр и имеет длину от 10 до 15 символов
    if re.match(r'^\d{10,15}$', phone_number):
        return True
    return False

# Функция для подключения к базе данных
def connect_db():
    try:
        conn = connect(
            dbname="phonebook",
            user="postgres",
            password="111",
            host="db",
            port="5432"
        )
        return conn
    except errors.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Главная страница (список контактов)
@app.route('/')
def index():
    conn = connect_db()
    if conn is None:
        return "Ошибка подключения к базе данных", 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM contacts")
            contacts = cur.fetchall()
        return render_template('index.html', contacts=contacts)
    except errors.Error as e:
        return f"Ошибка при получении контактов: {e}", 500
    finally:
        if conn:
            conn.close()

# Добавление контакта
@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        note = request.form['note']

        # Проверка номера телефона
        if not validate_phone_number(phone_number):
            return render_template('add.html', error="Номер телефона должен состоять из 10-15 цифр")

        conn = connect_db()
        if conn is None:
            return "Ошибка подключения к базе данных", 500

        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("INSERT INTO contacts (full_name, phone_number, note) VALUES (%s, %s, %s)"),
                    (full_name, phone_number, note)
                )
                conn.commit()
            return redirect(url_for('index'))
        except errors.Error as e:
            return f"Ошибка при вставке контакта: {e}", 500
        finally:
            if conn:
                conn.close()
    return render_template('add.html')

# Редактирование контакта
@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    conn = connect_db()
    if conn is None:
        return "Ошибка подключения к базе данных", 500

    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        note = request.form['note']

        # Проверка номера телефона
        if not validate_phone_number(phone_number):
            return render_template('edit.html', contact=(contact_id, full_name, phone_number, note), error="Номер телефона должен состоять из 10-15 цифр")

        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("UPDATE contacts SET full_name = %s, phone_number = %s, note = %s WHERE id = %s"),
                    (full_name, phone_number, note, contact_id)
                )
                conn.commit()
            return redirect(url_for('index'))
        except errors.Error as e:
            return f"Ошибка при обновлении контакта: {e}", 500
        finally:
            if conn:
                conn.close()
    else:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
                contact = cur.fetchone()
            return render_template('edit.html', contact=contact)
        except errors.Error as e:
            return f"Ошибка при получении контакта: {e}", 500
        finally:
            if conn:
                conn.close()

# Удаление контакта
@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    conn = connect_db()
    if conn is None:
        return "Ошибка подключения к базе данных", 500

    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("DELETE FROM contacts WHERE id = %s"),
                (contact_id,)
            )
            conn.commit()
        return redirect(url_for('index'))
    except errors.Error as e:
        return f"Ошибка при удалении контакта: {e}", 500
    finally:
        if conn:
            conn.close()

# Запуск приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)