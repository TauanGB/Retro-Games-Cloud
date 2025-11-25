#!/bin/bash
set -e

echo "=========================================="
echo "Iniciando Retro Games Cloud"
echo "=========================================="

# Executa migrações
echo "[1/4] Executando migrações do banco de dados..."
python manage.py migrate --noinput

# Cria superusuário se não existir (apenas em desenvolvimento)
if [ "$DEBUG" = "True" ]; then
    echo "[2/4] Verificando superusuário..."
    python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
" 2>/dev/null || echo "Aviso: Não foi possível criar o superusuário"
else
    echo "[2/4] Modo produção - pulando criação de superusuário"
fi

# Coleta arquivos estáticos
echo "[3/4] Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "[4/4] Tudo pronto! Iniciando servidor Gunicorn..."
echo "=========================================="

# Executa o comando passado como argumento (geralmente gunicorn)
exec "$@"
