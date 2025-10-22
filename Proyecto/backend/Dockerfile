FROM python:3.9

WORKDIR /code

# Instalar dependencias del sistema para mysqlclient
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    apt-get clean

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]0.0:8000"]