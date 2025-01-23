from flask import Flask, render_template, request, make_response, send_from_directory
import sqlite3
import csv
import os
import io
from typing import List, Tuple

# инициализация Flask-приложения
app = Flask(__name__)

# прописываем БД  
database: str = 'my_data.db'

# Подготовленные SQL запросы
sql_queries = {
    "Вывести транскрипцию для cta0003": "SELECT unit FROM Ideal_transcription WHERE filename = '333333'",
    "Вывести сколько слов в каждом файле ": "SELECT filename, COUNT(*) AS WordCount FROM Words GROUP BY filename",
    "Вывести все ИК для слова <она>": "SELECT unit, words_in_sintagmas FROM Sintagmas WHERE words_in_sintagmas LIKE '% она %'"
}

def execute_sql_query(query: str) -> List[Tuple]:
    """Выполняет SQL запрос к базе данных SQLite."""
    conn = sqlite3.connect(database) # Создаем соединение с базой данных
    cursor = conn.cursor() # Создаем курсор для выполнения SQL-запросов
    cursor.execute(query) # Выполняем SQL-запрос execute() принимает строку с SQL-командой
    results = cursor.fetchall() # Извлекаем все результаты запроса fetchall() возвращает список кортежей, где каждый кортеж представляет собой одну строку из результата запроса
    conn.close()
    return results # Возвращаем список кортежей (результаты запроса)

def get_table_names() -> List[str]:
    """Возвращает список имен таблиц в базе данных."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # Запросом получаем список имен таблиц
    table_names = [row[0] for row in cursor.fetchall()] # Извлекаем все результаты запроса и создаем список имен таблиц (1 эл-т)
    conn.close()
    return table_names

@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница, где можно выбрать и выполнить SQL-запрос"""
    # Заведем переменные для хранения результатов
    selected_query_result = None
    query_result = None

    # Получаем список имен таблиц из функции get_table_names()
    table_names = get_table_names()

    # Проверяем, был ли отправлен POST-запрос
    if request.method == 'POST':
        # Проверяем, было ли отправлено поле query в форме
        if 'query' in request.form: # обработка SQL-запросов
            # Получаем запрос
            selected_query = request.form.get('query')
            # Проверяем, существует ли выбранный запрос в словаре sql_queries
            if selected_query and selected_query in sql_queries:
                # Получаем SQL-запрос из словаря по ключу (выбранному запросу)
                query = sql_queries[selected_query]
                # Выполняем запрос и сохраняем результаты
                selected_query_result = execute_sql_query(query) 
                query_result = None # Очищаем результаты пользовательского запроса
            # Если пишем запрос сами    
            elif selected_query: # проверяем что запрос есть  
                # Выполняем запрос и сохраняем результаты
                query_result = execute_sql_query(selected_query) 
                selected_query_result = None # Очищаем результаты запроса из списка

    # render_template -> отображает HTML-шаблон и передает ему переменные для отображения данных    
    return render_template('index.html', queries=sql_queries, table_names=table_names, selected_results=selected_query_result, user_results=query_result) 

# Запускаем приложение, если этот файл запущен напрямую
if __name__ == '__main__':
    # Запускаем приложение, debug=True чтобы ошибки выводились на веб-странице
    app.run(debug=True, port=5000, host="0.0.0.0")