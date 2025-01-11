FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0 

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir


COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:9009", "backend.wsgi"]

# RUN chmod +x start.sh

# Укажите команду для запуска вашего приложения
# CMD ["./start.sh"]

# CMD ["python", "upload_script.py"]

# COPY upload_script.py  ./
# COPY data/ingredients.json ./data/
