# Configuração do Nginx para Retro Games Cloud

Este documento explica como o sistema está configurado para funcionar com Nginx como proxy reverso.

## 📋 Estrutura da Configuração

O sistema está configurado para rodar completamente com Nginx usando Docker Compose:

- **Nginx**: Servidor web e proxy reverso (porta 80/443)
- **Django/Gunicorn**: Aplicação web (porta 8000 interna)
- **PostgreSQL**: Banco de dados (opcional, pode usar SQLite)

## 🚀 Como Iniciar

### 1. Verificar as Configurações

Certifique-se de que o arquivo `env.docker` está configurado corretamente:

```bash
# Para usar PostgreSQL
DATABASE_URL=postgres://postgres:postgres@db:5432/retro_games

# Para usar SQLite (padrão)
DATABASE_URL=sqlite:///db.sqlite3
```

### 2. Iniciar os Serviços

```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Ver logs apenas do nginx
docker-compose logs -f nginx

# Ver logs apenas do Django
docker-compose logs -f web
```

### 3. Acessar a Aplicação

Após iniciar, acesse:
- **Aplicação**: http://localhost
- **Admin Django**: http://localhost/admin

## 📁 Arquivos de Configuração

### nginx.conf

Configuração principal do Nginx com:
- Proxy reverso para Django
- Servir arquivos estáticos (`/static/`)
- Servir arquivos de mídia (`/media/`)
- Rate limiting para APIs e login
- Compressão Gzip
- Headers de segurança
- Health check endpoint (`/health/`)

### docker-compose.yml

Define três serviços:
1. **web**: Aplicação Django com Gunicorn
2. **nginx**: Servidor Nginx
3. **db**: PostgreSQL (opcional)

## 🔧 Configurações do Django

O Django está configurado para trabalhar com Nginx através de:

```python
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

Isso permite que o Django reconheça corretamente:
- O host original da requisição
- O protocolo (HTTP/HTTPS)
- O IP real do cliente

## 📊 Monitoramento

### Logs do Nginx

Os logs do Nginx são salvos em `nginx_logs/`:
- `access.log`: Requisições HTTP
- `error.log`: Erros do Nginx

Para visualizar em tempo real:
```bash
tail -f nginx_logs/access.log
tail -f nginx_logs/error.log
```

### Health Check

O Nginx expõe um endpoint de health check:
```bash
curl http://localhost/health/
# Retorna: healthy
```

## 🔒 Segurança

### Rate Limiting

O Nginx está configurado com rate limiting:

- **Login/Register**: 5 requisições por minuto por IP
- **API**: 10 requisições por segundo por IP

### Headers de Segurança

Headers de segurança configurados:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### HTTPS (Produção)

Para configurar HTTPS em produção:

1. Adicione certificados SSL ao diretório do projeto
2. Atualize `nginx.conf` para incluir configuração SSL
3. Configure redirecionamento HTTP → HTTPS
4. Atualize `CSRF_TRUSTED_ORIGINS` no `env.docker`

## 🛠️ Comandos Úteis

### Reiniciar Serviços

```bash
# Reiniciar todos os serviços
docker-compose restart

# Reiniciar apenas o nginx
docker-compose restart nginx

# Reiniciar apenas o Django
docker-compose restart web
```

### Verificar Status

```bash
# Status dos containers
docker-compose ps

# Verificar logs de erro
docker-compose logs --tail=50 web
docker-compose logs --tail=50 nginx
```

### Testar Configuração do Nginx

```bash
# Testar configuração do nginx (dentro do container)
docker-compose exec nginx nginx -t
```

### Coletar Arquivos Estáticos

```bash
# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

### Executar Migrações

```bash
# Executar migrações
docker-compose exec web python manage.py migrate
```

### Acessar Shell do Django

```bash
# Shell do Django
docker-compose exec web python manage.py shell

# Criar superusuário
docker-compose exec web python manage.py createsuperuser
```

## 🐛 Troubleshooting

### Nginx não inicia

1. Verifique se a porta 80 está disponível:
   ```bash
   netstat -an | grep :80
   ```

2. Verifique a configuração do Nginx:
   ```bash
   docker-compose exec nginx nginx -t
   ```

3. Verifique os logs:
   ```bash
   docker-compose logs nginx
   ```

### Arquivos estáticos não aparecem

1. Verifique se o diretório `staticfiles` existe e tem arquivos
2. Verifique as permissões:
   ```bash
   ls -la staticfiles/
   ```

3. Recolete os arquivos estáticos:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Erro 502 Bad Gateway

Isso geralmente significa que o Nginx não consegue se conectar ao Django:

1. Verifique se o container `web` está rodando:
   ```bash
   docker-compose ps web
   ```

2. Verifique os logs do Django:
   ```bash
   docker-compose logs web
   ```

3. Verifique se o Gunicorn está respondendo:
   ```bash
   docker-compose exec web curl http://localhost:8000/health/
   ```

## 📝 Notas de Produção

Para produção, considere:

1. **Variáveis de Ambiente**: Use `.env` com valores seguros
2. **Secret Key**: Gere uma nova SECRET_KEY para produção
3. **DEBUG**: Defina `DEBUG=False`
4. **ALLOWED_HOSTS**: Configure com seu domínio
5. **HTTPS**: Configure certificados SSL
6. **Backup**: Configure backups do banco de dados
7. **Monitoramento**: Configure monitoramento de logs e performance

## 🔗 Recursos

- [Documentação do Nginx](https://nginx.org/en/docs/)
- [Documentação do Docker Compose](https://docs.docker.com/compose/)
- [Deploy Django com Nginx e Gunicorn](https://docs.djangoproject.com/en/stable/howto/deployment/)

