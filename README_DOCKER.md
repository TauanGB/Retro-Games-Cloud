# Retro Games Cloud - Docker Setup

Este documento explica como executar o projeto Retro Games Cloud usando Docker.

## Pré-requisitos

- Docker
- Docker Compose

## Estrutura dos Arquivos Docker

### Arquivos Principais

- `Dockerfile` - Configuração da imagem da aplicação Django
- `docker-compose.yml` - Configuração para produção (com Nginx)
- `docker-compose.dev.yml` - Configuração para desenvolvimento
- `docker-entrypoint.sh` - Script de inicialização do container
- `nginx.conf` - Configuração do servidor web Nginx
- `.dockerignore` - Arquivos ignorados no build da imagem

### Configurações

- `env.docker` - Variáveis de ambiente para Docker
- `requirements.txt` - Dependências Python atualizadas

## Como Executar

### Desenvolvimento (Recomendado)

```bash
# Usar o compose de desenvolvimento
docker-compose -f docker-compose.dev.yml up --build

# Ou apenas
docker-compose -f docker-compose.dev.yml up
```

### Produção

```bash
# Usar o compose de produção (com Nginx)
docker-compose up --build

# Ou apenas
docker-compose up
```

## Acessos

- **Aplicação**: http://localhost:8000 (desenvolvimento) ou http://localhost (produção)
- **Admin Django**: http://localhost:8000/admin/ (desenvolvimento) ou http://localhost/admin/ (produção)
- **Banco PostgreSQL**: localhost:5432

### Credenciais Padrão

- **Superusuário**: admin
- **Senha**: admin123
- **Banco**: retro_games_cloud
- **Usuário DB**: postgres
- **Senha DB**: postgres

## Comandos Úteis

### Parar os containers
```bash
docker-compose down
```

### Ver logs
```bash
docker-compose logs -f web
```

### Executar comandos Django
```bash
# Criar migrações
docker-compose exec web python manage.py makemigrations

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic

# Acessar shell Django
docker-compose exec web python manage.py shell
```

### Limpar volumes (CUIDADO: apaga dados)
```bash
docker-compose down -v
```

## Estrutura dos Volumes

- `postgres_data` - Dados do PostgreSQL
- `static_volume` - Arquivos estáticos coletados
- `media_volume` - Arquivos de mídia enviados

## Configurações de Ambiente

As configurações são gerenciadas através de variáveis de ambiente:

- `SECRET_KEY` - Chave secreta do Django
- `DEBUG` - Modo debug (True/False)
- `ALLOWED_HOSTS` - Hosts permitidos
- `DATABASE_URL` - URL de conexão com o banco

## Troubleshooting

### Problema: Container não inicia
```bash
# Verificar logs
docker-compose logs web

# Rebuild da imagem
docker-compose build --no-cache web
```

### Problema: Banco de dados não conecta
```bash
# Verificar se o PostgreSQL está rodando
docker-compose ps

# Verificar logs do banco
docker-compose logs db
```

### Problema: Arquivos estáticos não carregam
```bash
# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

## Desenvolvimento

Para desenvolvimento, use o `docker-compose.dev.yml` que:
- Monta o código fonte como volume
- Não inclui Nginx
- Permite hot-reload do Django

## Produção

Para produção, use o `docker-compose.yml` que:
- Inclui Nginx como proxy reverso
- Serve arquivos estáticos
- Configurações otimizadas
- Não monta código fonte (usa imagem)

## Segurança

⚠️ **IMPORTANTE**: Para produção, altere:
- `SECRET_KEY` no arquivo de ambiente
- Senhas do banco de dados
- Configurações de segurança no Django
- Use HTTPS com certificados SSL
