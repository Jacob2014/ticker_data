import os

# Путь к файлу с тикерами
tickers_file = '12'

# Шаблон для сервиса в docker-compose
service_template = """
  {ticker}:
    build: ./{ticker}
    container_name: {ticker}_container
    environment:
      - TZ=Europe/Moscow
    volumes:
      - ./{ticker}:/app
    restart: unless-stopped
"""

# Функция для генерации docker-compose.yml
def generate_docker_compose(tickers):
    compose_header = "version: '3.8'\nservices:\n"
    services = []

    for ticker in tickers:
        service = service_template.format(ticker=ticker)
        services.append(service)

    # Соединяем все части
    docker_compose_content = compose_header + "".join(services)

    # Записываем результат в docker-compose.yml
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)

# Чтение тикеров из файла и генерация docker-compose.yml
if os.path.exists(tickers_file):
    with open(tickers_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]
        generate_docker_compose(tickers)
        print("docker-compose.yml успешно создан!")
else:
    print(f"Файл {tickers_file} не найден!")
