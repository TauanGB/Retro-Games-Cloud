# Use a imagem oficial do Python
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . /app/

# Cria diretórios necessários
RUN mkdir -p /app/staticfiles /app/media

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta 8000
EXPOSE 8000

# Script de entrypoint
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Comando padrão
CMD ["/app/docker-entrypoint.sh"]
