from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from modules.database import create_tables, get_records
from modules.auth import create_admin_if_not_exists, login, register, check_role
from modules.rooms import get_all_rooms, get_free_rooms, add_room, edit_room, delete_room
from modules.bookings import create_booking, cancel_booking, get_active_bookings, get_bookings_by_user
from modules.reports import occupancy_report, revenue_report, export_to_excel, export_to_pdf
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # В продакшене изменить!

# Инициализация базы данных
create_tables()
create_admin_if_not_exists()

@app.route('/')
def index():
    """Главная страница"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Страница входа"""
    if request.method == 'POST':
        login_input = request.form['login']
        password = request.form['password']
        
        result = login(login_input, password)
        if result['success']:
            session['user_id'] = result['user_id']
            session['login'] = result['login']
            session['role'] = result['role']
            session['fio'] = result['fio']
            flash(f'Добро пожаловать, {result["fio"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """Страница регистрации"""
    if request.method == 'POST':
        login_input = request.form['login']
        password = request.form['password']
        fio = request.form['fio']
        email = request.form['email']
        phone = request.form['phone']
        
        result = register(login_input, password, fio, email, phone)
        if result['success']:
            flash('Регистрация успешна! Теперь войдите в систему.', 'success')
            return redirect(url_for('login_page'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Панель управления"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    role = session.get('role', 'client')
    return render_template('dashboard.html', role=role, user=session)

@app.route('/rooms')
def rooms():
    """Просмотр номеров"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    all_rooms = get_all_rooms()
    free_rooms = get_free_rooms()
    return render_template('rooms.html', all_rooms=all_rooms, free_rooms=free_rooms)

@app.route('/add_room', methods=['GET', 'POST'])
def add_room_page():
    """Добавление номера (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        room_number = request.form['room_number']
        category = request.form['category']
        capacity = int(request.form['capacity'])
        price = float(request.form['price'])
        
        result = add_room(room_number, category, capacity, price)
        flash(result['message'], 'success' if result['success'] else 'danger')
        return redirect(url_for('rooms'))
    
    return render_template('add_room.html')

@app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
def edit_room_page(room_id):
    """Редактирование номера (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        field = request.form['field']
        value = request.form['value']
        result = edit_room(room_id, field, value)
        flash(result['message'], 'success' if result['success'] else 'danger')
        return redirect(url_for('rooms'))
    
    rooms = get_all_rooms()
    room = None
    for r in rooms:
        if r[0] == room_id:
            room = r
            break
    
    if not room:
        flash('Номер не найден!', 'danger')
        return redirect(url_for('rooms'))
    
    return render_template('edit_room.html', room=room)

@app.route('/delete_room/<int:room_id>')
def delete_room_page(room_id):
    """Удаление номера (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    result = delete_room(room_id)
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('rooms'))

@app.route('/bookings')
def bookings():
    """Просмотр броней"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    if session.get('role') == 'admin':
        bookings_list = get_active_bookings()
    else:
        bookings_list = get_bookings_by_user(session['user_id'])
    
    return render_template('bookings.html', bookings=bookings_list)

@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking_page():
    """Создание брони"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        room_id = int(request.form['room_id'])
        guest_fio = request.form['guest_fio']
        guest_phone = request.form['guest_phone']
        guest_email = request.form['guest_email']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        user_id = session['user_id']
        
        result = create_booking(room_id, guest_fio, guest_phone, guest_email, 
                               check_in, check_out, user_id)
        flash(result['message'], 'success' if result['success'] else 'danger')
        return redirect(url_for('bookings'))
    
    free_rooms = get_free_rooms()
    return render_template('create_booking.html', rooms=free_rooms)

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking_page(booking_id):
    """Отмена брони"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    result = cancel_booking(booking_id)
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('bookings'))

@app.route('/reports')
def reports():
    """Отчёты (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    occupancy = occupancy_report()
    return render_template('reports.html', occupancy=occupancy)

@app.route('/revenue_report', methods=['GET', 'POST'])
def revenue_report_page():
    """Отчёт по доходам (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        result = revenue_report(start_date, end_date)
        return render_template('revenue_report.html', result=result, start=start_date, end=end_date)
    
    return render_template('revenue_report.html')

@app.route('/export_excel')
def export_excel():
    """Экспорт в Excel (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    rooms = get_all_rooms()
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    if export_to_excel(rooms, filename):
        return send_file(filename, as_attachment=True)
    else:
        flash('Ошибка экспорта! Установите openpyxl.', 'danger')
        return redirect(url_for('reports'))

@app.route('/export_pdf')
def export_pdf():
    """Экспорт в PDF (только админ)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещён!', 'danger')
        return redirect(url_for('dashboard'))
    
    rooms = get_all_rooms()
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    if export_to_pdf(rooms, filename):
        return send_file(filename, as_attachment=True)
    else:
        flash('Ошибка экспорта! Установите reportlab.', 'danger')
        return redirect(url_for('reports'))

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
