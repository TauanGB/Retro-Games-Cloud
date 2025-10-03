#!/bin/bash

# Aguarda o banco de dados estar disponível
echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Banco de dados disponível!"

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

# Executa o comando passado como argumento
exec "$@"
