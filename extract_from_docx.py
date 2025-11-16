#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Извлечение текста из Word документа с правильной кодировкой
"""

from docx import Document
import sys

def extract_text_from_docx(docx_file, output_file=None):
    """
    Извлекает текст из Word документа и сохраняет в UTF-8
    """
    try:
        # Открываем Word документ
        doc = Document(docx_file)
        
        # Извлекаем весь текст
        full_text = []
        
        # Извлекаем текст из всех параграфов
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:  # Добавляем только непустые строки
                full_text.append(text)
        
        # Объединяем все строки
        text_content = '\n'.join(full_text)
        
        # Если указан выходной файл, сохраняем
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"Текст успешно извлечен и сохранен в: {output_file}")
        else:
            # Просто выводим на экран
            print(text_content)
        
        # Показываем статистику
        lines_count = len(full_text)
        chars_count = len(text_content)
        cyrillic_count = sum(1 for c in text_content if '\u0400' <= c <= '\u04FF')
        
        print(f"\nСтатистика:")
        print(f"  Строк: {lines_count}")
        print(f"  Символов: {chars_count}")
        print(f"  Кириллических символов: {cyrillic_count}")
        
        # Показываем первые несколько строк
        print(f"\nПервые 10 строк:")
        try:
            for i, line in enumerate(full_text[:10], 1):
                print(f"{i}. {line[:80]}")
        except UnicodeEncodeError:
            # Если консоль не поддерживает UTF-8, просто пропускаем вывод
            print("(Текст успешно сохранен в файл)")
        
        return text_content
        
    except Exception as e:
        print(f"Ошибка при извлечении текста: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    input_file = 'full_txt.docx'
    output_file = 'text_extracted.txt'  # Сохраняем в новый файл
    
    extract_text_from_docx(input_file, output_file)

