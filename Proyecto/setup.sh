#!/usr/bin/env bash
set -e
echo "Construyendo y levantando servicios (docker-compose)..."
docker-compose up --build -d
echo "Esperando 10 segundos para que MySQL arranque..."
sleep 10
echo "Ejecutando migraciones Django..."
docker-compose exec web python manage.py makemigrations --noinput || true
docker-compose exec web python manage.py migrate --noinput
echo "Listo. Abre http://localhost:8000/ para ver el Hola Mundo."
