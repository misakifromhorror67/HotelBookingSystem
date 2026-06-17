# 🏨 Информационная система бронирования номеров гостиницы

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-green.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 О проекте

Информационная система предназначена для автоматизации процесса бронирования номеров гостиницы, управления занятостью номерного фонда, учёта данных о гостях и формирования отчётности для руководства.

## ⚙️ Основные функции

- ✅ Авторизация и регистрация пользователей
- ✅ Просмотр свободных номеров
- ✅ Бронирование номеров с автоматическим расчётом стоимости
- ✅ Отмена бронирования
- ✅ Формирование отчётов по загрузке и доходам
- ✅ Экспорт данных в Excel и PDF
- ✅ Разграничение прав доступа (администратор / клиент)

## 🚀 Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/misakifromhorror67/HotelBookingSystem.git
cd HotelBookingSystem

# Установка зависимостей (для экспорта в Excel и PDF)
pip install openpyxl reportlab

# Запуск программы
python main.py
