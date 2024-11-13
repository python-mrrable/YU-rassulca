import random
import tkinter as tk
import openpyxl

def load_xlsx_content(filename):
    content = []
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active
        for row in sheet.iter_rows(values_only=True):
            if row[0]:  # Проверяем, что ячейка не пустая
                content.append(str(row[0]))
    except Exception as e:
        logging.error(f"Ошибка при загрузке XLSX файла {filename}: {str(e)}")
    return content

def load_file_content(filename):
    content = []
    try:
        with open(filename, 'r') as file:
            content = file.readlines()
        content = [line.strip() for line in content if line.strip()]
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла {filename}: {str(e)}")
    return content

def get_random_line(lines):
    return random.choice(lines)

def save_file_content(file_path, content):
    with open(file_path, 'w') as file:
        for line in content:
            file.write(line + '\n')