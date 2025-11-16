#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Улучшенная конвертация текста в HTML с якорями и ссылками
"""

import re
import html

def create_slug(text):
    """Создает URL-friendly идентификатор из текста"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def is_header(line, prev_line, next_line):
    """Определяет, является ли строка заголовком"""
    line = line.strip()
    
    # Заголовок уровня 1: начинается с цифры и точки
    if re.match(r'^\d+\.\s+', line):
        return 'h1'
    
    # Специальные заголовки
    if line in ['Введение', 'Актуальность', 'Список литературы']:
        return 'h1'
    
    # Заголовок уровня 2: короткая строка, начинается с заглавной, 
    # предыдущая строка пустая или заканчивается точкой/двоеточием,
    # следующая строка начинается с маленькой буквы или тире
    if (len(line) < 80 and 
        line[0].isupper() and 
        not line.endswith('.') and
        not line.endswith(',') and
        not ':' in line and
        not line.startswith('В ') and
        not line.startswith('На ') and
        not line.startswith('Для ') and
        not line.startswith('Пример') and
        not line.startswith('Цель') and
        not line.startswith('Отличие') and
        not line.startswith('Применение') and
        not line.startswith('Основная') and
        prev_line and (not prev_line.strip() or prev_line.strip().endswith('.') or prev_line.strip().endswith(':') or re.match(r'^\d+\.', prev_line.strip())) and
        next_line and (next_line.strip()[0].islower() if next_line.strip() else True or next_line.strip().startswith('—') or next_line.strip().startswith('Пример'))):
        return 'h2'
    
    return None

def parse_text_to_html(text_content):
    """Парсит текст и создает HTML с якорями"""
    lines = text_content.split('\n')
    html_parts = []
    toc = []
    in_list = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        prev_line = lines[i-1] if i > 0 else ''
        next_line = lines[i+1] if i < len(lines) - 1 else ''
        
        if not line:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append('<p></p>')
            i += 1
            continue
        
        # Проверяем, является ли строка заголовком
        header_type = is_header(line, prev_line, next_line)
        
        if header_type == 'h1':
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            section_text = re.sub(r'^\d+\.\s+', '', line)
            section_id = create_slug(section_text)
            toc.append(('h1', section_text, section_id))
            html_parts.append(f'<h1 id="{section_id}">{html.escape(section_text)}</h1>')
        
        elif header_type == 'h2':
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            section_id = create_slug(line)
            toc.append(('h2', line, section_id))
            html_parts.append(f'<h2 id="{section_id}">{html.escape(line)}</h2>')
        
        # Строки, начинающиеся с "Пример:" или "Примечание:"
        elif line.startswith('Пример:') or line.startswith('Примечание:'):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append(f'<p class="example"><strong>{html.escape(line)}</strong></p>')
        
        # Строки с кодом Python
        elif (line.startswith('import ') or 
              line.startswith('from ') or 
              line.startswith('# ') or 
              ('=' in line and ('pd.' in line or 'sklearn' in line or 'plt.' in line or 'clf.' in line or 'data[' in line))):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            # Начинаем блок кода
            code_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if (next_line.startswith('import ') or 
                    next_line.startswith('from ') or 
                    next_line.startswith('# ') or
                    next_line.startswith('    ') or
                    next_line.startswith('\t') or
                    '=' in next_line or
                    next_line.startswith('print(') or
                    next_line.startswith('plt.') or
                    next_line.startswith('clf.') or
                    next_line.startswith('data[') or
                    next_line.startswith('X_') or
                    next_line.startswith('y_') or
                    next_line == ''):
                    if next_line:
                        code_lines.append(next_line)
                    elif i + 1 < len(lines) and lines[i+1].strip() and ('import' in lines[i+1] or 'from' in lines[i+1] or '=' in lines[i+1]):
                        code_lines.append('')
                    else:
                        break
                else:
                    break
                i += 1
            code_block = '\n'.join(code_lines)
            html_parts.append(f'<pre><code class="language-python">{html.escape(code_block)}</code></pre>')
            continue
        
        # Списки
        elif (line.startswith('*') or 
              line.startswith('o') or 
              line.startswith('•') or
              (line.startswith('-') and not line.startswith('--'))):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            clean_line = line.lstrip("*o•- ")
            html_parts.append(f'<li>{html.escape(clean_line)}</li>')
        
        # Обычный текст
        else:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append(f'<p>{html.escape(line)}</p>')
        
        i += 1
    
    if in_list:
        html_parts.append('</ul>')
    
    return html_parts, toc

def create_html_document(text_content, output_file='text.html'):
    """Создает полный HTML документ"""
    html_parts, toc = parse_text_to_html(text_content)
    
    # Создаем оглавление
    toc_html = '<div class="toc"><h2>Содержание</h2><ul>'
    for level, text, anchor in toc:
        toc_html += f'<li class="toc-{level}"><a href="#{anchor}">{html.escape(text)}</a></li>'
    toc_html += '</ul></div>'
    
    # Объединяем все части
    body_content = '\n'.join(html_parts)
    
    # Создаем полный HTML
    html_doc = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Классификация отходов с использованием методов интеллектуального анализа данных</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #0F4761;
            border-bottom: 3px solid #0F4761;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            scroll-margin-top: 20px;
        }}
        h2 {{
            color: #467886;
            margin-top: 25px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #467886;
            scroll-margin-top: 20px;
        }}
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        .toc {{
            background-color: #f9f9f9;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .toc h2 {{
            margin-top: 0;
            color: #0F4761;
            border: none;
            padding: 0;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        .toc-h1 {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .toc-h2 {{
            font-weight: normal;
            font-size: 0.95em;
            padding-left: 30px;
        }}
        .toc a {{
            color: #467886;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
            color: #0F4761;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        pre {{
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        code {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .example {{
            background-color: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        a {{
            color: #467886;
        }}
        a:hover {{
            color: #0F4761;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {toc_html}
        <hr>
        {body_content}
    </div>
</body>
</html>'''
    
    # Сохраняем файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    print(f"HTML файл создан: {output_file}")
    print(f"Найдено разделов в оглавлении: {len(toc)}")
    for level, text, anchor in toc[:10]:
        print(f"  {level}: {text[:50]}")
    
    return output_file

if __name__ == '__main__':
    # Читаем текст
    with open('text_extracted.txt', 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Создаем HTML
    create_html_document(text_content, 'text.html')


