# Используем базовый образ Python
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы из текущей папки в контейнер
COPY . /app

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y supervisor

# Копируем конфигурационный файл supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем supervisord
CMD ["/usr/bin/supervisord"]
