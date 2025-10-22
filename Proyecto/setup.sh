#!/usr/bin/env bash
set -e

echo "=== PREPARACIÓN INICIAL DEL PROYECTO ==="

echo "1. Levantando repositorio con Docker Compose..."
docker-compose up --build -d

echo "2. Esperando que MySQL esté listo..."
sleep 10

echo "3. Instalando dependencias y configurando..."
docker-compose exec web python manage.py makemigrations --noinput || true
docker-compose exec web python manage.py migrate --noinput

echo "4. Ejecutando pruebas básicas..."
# Placeholder para pruebas futuras - actualmente no hay tests implementados
echo "   (Pruebas no implementadas aún - se ejecutarán aquí en el futuro)"

echo "=== CONFIGURACIÓN COMPLETADA ==="
echo "Aplicación disponible en: http://localhost:8000"