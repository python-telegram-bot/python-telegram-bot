# Лёгкий базовый образ
FROM python:3.11-slim

# Обновим пакеты и поставим полезные утилиты (по минимуму)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl tini \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Скопируем зависимости отдельно для кеширования слоёв
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код
COPY app.py /app/app.py

# Нешелловый init для корректного reaping сигналов
ENTRYPOINT ["/usr/bin/tini", "--"]

# Файл-заглушка для healthcheck будет создаваться приложением
CMD ["python", "-u", "app.py"]
