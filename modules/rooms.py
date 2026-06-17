# Модуль управления номерами
from modules.database import get_records, add_record, update_record, delete_record

def get_all_rooms():
    """Получение всех номеров"""
    return get_records("Rooms")

def get_free_rooms():
    """Получение свободных номеров"""
    return get_records("Rooms", "Status = 'свободен'")

def add_room(room_number, category, capacity, price_per_night):
    """Добавление нового номера"""
    # Проверка на дубликат
    existing = get_records("Rooms", f"RoomNumber = '{room_number}'")
    if existing:
        return {"success": False, "message": "Номер с таким номером уже существует"}
    
    room_id = add_record("Rooms", {
        "RoomNumber": room_number,
        "Category": category,
        "Capacity": capacity,
        "PricePerNight": price_per_night,
        "Status": "свободен"
    })
    
    return {"success": True, "room_id": room_id, "message": f"Номер {room_number} добавлен"}

def edit_room(room_id, field, value):
    """Редактирование номера"""
    rows = update_record("Rooms", {field: value}, f"RoomID = {room_id}")
    if rows > 0:
        return {"success": True, "message": "Номер обновлён"}
    return {"success": False, "message": "Номер не найден"}

def delete_room(room_id):
    """Удаление номера"""
    rows = delete_record("Rooms", f"RoomID = {room_id}")
    if rows > 0:
        return {"success": True, "message": "Номер удалён"}
    return {"success": False, "message": "Номер не найден"}
