#!/bin/bash

# (a) Принимаем аргумент - имя файла
filename=$1

# (b) Проверяем, существует ли файл
if [ ! -f "$filename" ]; then
    echo "Ошибка: Файл не существует или не указан"
else
    # (c) Выводим статистику
    echo "Статистика для файла: $filename"
    
    # (i) Количество строк
    lines=$(wc -l < "$filename")
    echo "Количество строк: $lines"
    
    # (ii) Количество слов  
    words=$(wc -w < "$filename")
    echo "Количество слов: $words"
    
    # (iii) Количество символов
    chars=$(wc -m < "$filename")
    echo "Количество символов: $chars"
fi