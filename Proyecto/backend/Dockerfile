FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

# Copiar el script de espera y dar permisos
COPY wait_for_db.sh /code/
RUN chmod +x /code/wait_for_db.sh

EXPOSE 8000

CMD ["./wait_for_db.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]