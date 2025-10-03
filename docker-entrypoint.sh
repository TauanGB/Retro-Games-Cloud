#!/bin/bash

# Executa migrações
echo "Executando migrações..."
python manage.py migrate

# Cria superusuário se não existir
echo "Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Executa o comando passado como argumento
exec "$@"
