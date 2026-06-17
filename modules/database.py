# Модуль работы с базой данных
import sqlite3
import os
from config.config import DB_NAME

def connect():
    """Подключение к базе данных"""
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Создание всех таблиц"""
    conn = connect()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL,
            FIO TEXT NOT NULL,
            Email TEXT,
            Phone TEXT
        )
    ''')
    
    # Таблица номеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rooms (
            RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoomNumber TEXT UNIQUE NOT NULL,
            Category TEXT NOT NULL,
            Capacity INTEGER NOT NULL,
            PricePerNight REAL NOT NULL,
            Status TEXT DEFAULT 'свободен'
        )
    ''')
    
    # Таблица гостей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Guests (
            GuestID INTEGER PRIMARY KEY AUTOINCREMENT,
            FIO TEXT NOT NULL,
            Passport TEXT,
            Phone TEXT NOT NULL,
            Email TEXT
        )
    ''')
    
    # Таблица бронирований
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bookings (
            BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoomID INTEGER NOT NULL,
            GuestID INTEGER NOT NULL,
            UserID INTEGER NOT NULL,
            CheckInDate TEXT NOT NULL,
            CheckOutDate TEXT NOT NULL,
            Status TEXT DEFAULT 'активна',
            TotalPrice REAL NOT NULL,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
            FOREIGN KEY (GuestID) REFERENCES Guests(GuestID),
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Таблицы созданы (или уже существуют)")

def add_record(table, data):
    """Добавление записи в таблицу"""
    conn = connect()
    cursor = conn.cursor()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    cursor.execute(sql, list(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def update_record(table, data, condition):
    """Обновление записи"""
    conn = connect()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    
    cursor.execute(sql, list(data.values()))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected

def delete_record(table, condition):
    """Удаление записи"""
    conn = connect()
    cursor = conn.cursor()
    sql = f"DELETE FROM {table} WHERE {condition}"
    cursor.execute(sql)
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected

def get_records(table, condition=""):
    """Получение записей"""
    conn = connect()
    cursor = conn.cursor()
    
    sql = f"SELECT * FROM {table}"
    if condition:
        sql += f" WHERE {condition}"
    
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return result

def execute_query(sql, params=()):
    """Выполнение произвольного запроса"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = cursor.fetchall()
    conn.close()
    return result
