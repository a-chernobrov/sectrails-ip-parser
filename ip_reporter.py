import os
import csv
from collections import defaultdict
import ipaddress

# Указываем каталог с CSV-файлами
directory = "./ip_data"  # Замени на свой путь

# Функция для парсинга IP и маски
def parse_ip(ip_str):
    clean_ip = ip_str.replace("*current*", "").strip('"')
    ip, mask = clean_ip.split('/')
    return ip, int(mask)

# Чтение всех CSV-файлов и сбор данных
raw_data = defaultdict(list)
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        filepath = os.path.join(directory, filename)
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ip, mask = parse_ip(row['IP'])
                sites = int(row['Sites'])
                third_octet = '.'.join(ip.split('.')[:3])
                raw_data[third_octet].append({
                    'ip': ip,
                    'mask': mask,
                    'sites': sites,
                    'children': []
                })

# Построение иерархии
def build_hierarchy(entries):
    entries.sort(key=lambda x: (x['mask'], x['ip']))
    hierarchy = []

    for entry in entries[:]:
        network = ipaddress.ip_network(f"{entry['ip']}/{entry['mask']}", strict=False)
        parent = None
        for existing in hierarchy:
            existing_network = ipaddress.ip_network(f"{existing['ip']}/{existing['mask']}", strict=False)
            if (network.subnet_of(existing_network) or
                (entry['mask'] == 32 and ipaddress.ip_address(entry['ip']) in existing_network)) and \
               existing['mask'] < entry['mask']:
                parent = existing
                break
        if parent:
            parent['children'].append(entry)
            entries.remove(entry)
        else:
            hierarchy.append(entry)

    for entry in hierarchy:
        if entry['children']:
            entry['children'] = build_hierarchy(entry['children'])

    return hierarchy

# Применяем иерархию к данным
data = {}
for third_octet in raw_data:
    data[third_octet] = build_hierarchy(raw_data[third_octet])

# Генерация HTML таблицы рекурсивно
def generate_html_table(entries, level=0):
    html = ''
    for entry in entries:
        ip_display = f"{entry['ip']}/{entry['mask']}"
        indent = '&nbsp;' * (level * 4)  # Отступ для вложенности
        if entry['mask'] == 32:
            # Добавляем кнопку копирования для /32
            copy_button = f'<button class="btn btn-sm btn-outline-secondary copy-btn" data-ip="{entry["ip"]}" onclick="copyToClipboard(this)">Copy</button>'
            ip_cell = f'{indent}{ip_display} {copy_button}'
        else:
            ip_cell = f'{indent}{ip_display}'
        html += f'<tr><td>{ip_cell}</td><td>{entry["sites"]}</td></tr>\n'
        if entry['children']:
            html += generate_html_table(entry['children'], level + 1)
    return html

# Генерация HTML-отчета
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IP Hierarchy Report</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <style>
        body { margin: 20px; }
        .third-octet { font-size: 1.2em; margin-top: 20px; margin-bottom: 10px; }
        .table { margin-bottom: 20px; }
        .copy-btn { margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">IP Hierarchy Report</h1>
"""

for third_octet in sorted(data.keys()):

    html_content += '<table class="table table-bordered table-hover">\n'
    html_content += '<thead class="table-light"><tr><th>IP</th><th>Sites</th></tr></thead>\n'
    html_content += '<tbody>\n'
    html_content += generate_html_table(data[third_octet])
    html_content += '</tbody>\n'
    html_content += '</table>\n'

html_content += """
    </div>
    <!-- Bootstrap JS and Popper.js -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js" integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>
    <script>
        function copyToClipboard(button) {
            const ip = button.getAttribute('data-ip');
            navigator.clipboard.writeText(ip).then(() => {
                button.textContent = 'Copied!';
                setTimeout(() => { button.textContent = 'Copy'; }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        }
    </script>
</body>
</html>
"""

# Сохранение HTML-файла
with open('ip_hierarchy_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML-отчет создан: ip_hierarchy_report.html")
