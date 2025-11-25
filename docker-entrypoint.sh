#!/bin/bash
# Não usar set -e aqui para permitir tratamento de erros de conexão ao banco

echo "=========================================="
echo "Iniciando Retro Games Cloud"
echo "=========================================="

# Aguarda o banco de dados estar pronto (se usar PostgreSQL)
if [ "$DATABASE_URL" != "${DATABASE_URL#postgres}" ]; then
    echo "Aguardando banco de dados PostgreSQL..."
    max_attempts=30
    attempt=0
    until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
        attempt=$((attempt + 1))
        if [ $attempt -ge $max_attempts ]; then
            echo "Timeout aguardando banco de dados PostgreSQL. Continuando..."
            break
        fi
        echo "Banco de dados não está pronto ainda. Aguardando... ($attempt/$max_attempts)"
        sleep 2
    done
    if [ $attempt -lt $max_attempts ]; then
        echo "Banco de dados está pronto!"
    fi
else
    echo "Usando SQLite - sem necessidade de banco de dados externo"
fi

# Executa migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Cria superusuário se não existir (apenas em desenvolvimento)
if [ "${CREATE_SUPERUSER:-False}" = "True" ]; then
    echo "Verificando superusuário..."
    python manage.py shell <<EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superusuário criado: {username}')
else:
    print(f'Superusuário {username} já existe')
EOF
fi

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Cria diretórios necessários
mkdir -p /app/media/game_covers /app/media/user_uploads

echo "=========================================="
echo "Aplicação pronta para receber requisições"
echo "=========================================="

# Executa o servidor WSGI (runserver ou gunicorn)
if [ $# -eq 0 ]; then
    # Se não receber comando, usa variável de ambiente WSGI_SERVER
    WSGI_SERVER=${WSGI_SERVER:-runserver}
    
    if [ "$WSGI_SERVER" = "gunicorn" ]; then
        echo "Iniciando Gunicorn..."
        exec gunicorn retro_games_cloud.wsgi:application \
            --config gunicorn_config.py \
            --bind 0.0.0.0:8000 \
            --workers ${GUNICORN_WORKERS:-3} \
            --timeout 120 \
            --access-logfile - \
            --error-logfile - \
            --log-level ${GUNICORN_LOG_LEVEL:-info}
    else
        echo "Iniciando Django runserver..."
        exec python manage.py runserver 0.0.0.0:8000
    fi
else
    echo "Executando comando: $@"
    exec "$@"
fi

