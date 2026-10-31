FROM python:3.12

# 1. Меняем рабочую директорию на папку с проектом
WORKDIR /backend/foodgram

RUN pip install gunicorn==25.3.0

# 2. Поднимаемся на уровень выше на хосте, чтобы взять requirements.txt, 
# либо, если он лежит внутри foodgram, оставьте просто COPY requirements.txt .
COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

# 3. Копируем всё содержимое локальной папки backend в /backend контейнера
COPY . /backend

CMD ["gunicorn", "--bind", "0.0.0.0:8888", "foodgram.wsgi:application"]
