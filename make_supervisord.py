import os

# Путь к файлу с тикерами
tickers_file = '12'

# Шаблон для программы в supervisord.conf
program_template = """
[program:{ticker}]
command=python /app/{ticker}/main.py
autostart=true
autorestart=true
stderr_logfile=/var/log/{ticker}.err.log
stdout_logfile=/var/log/{ticker}.out.log
"""

# Функция для генерации supervisord.conf
def generate_supervisord_conf(tickers):
    supervisord_header = "[supervisord]\nnodaemon=true\n"
    programs = []

    for ticker in tickers:
        program = program_template.format(ticker=ticker.lower())
        programs.append(program)

    # Соединяем все части
    supervisord_content = supervisord_header + "".join(programs)

    # Записываем результат в supervisord.conf
    with open('supervisord.conf', 'w') as f:
        f.write(supervisord_content)
        print("supervisord.conf успешно создан!")

# Чтение тикеров из файла и генерация supervisord.conf
if os.path.exists(tickers_file):
    with open(tickers_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]
        generate_supervisord_conf(tickers)
else:
    print(f"Файл {tickers_file} не найден!")
