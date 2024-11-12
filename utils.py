import random
import tkinter as tk
import openpyxl

def load_xlsx_content(filename):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    content = []
    for row in sheet.iter_rows(values_only=True):
        if row[0]:  # Проверяем, что ячейка не пустая
            content.append(str(row[0]))
    return content

def load_file_content(filename):
    with open(filename, 'r') as file:
        content = file.readlines()
    return [line.strip() for line in content if line.strip()]

def get_random_line(lines):
    return random.choice(lines)