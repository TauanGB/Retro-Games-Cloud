# ✅ Configuração Completa do Nginx - Retro Games Cloud

## 📋 Estrutura da Configuração

O sistema está **COMPLETAMENTE CONFIGURADO** para funcionar com Nginx como proxy reverso:

```
Cliente → Nginx (porta 80) → Django Runserver (porta 8000 interno)
```

## 🔧 Arquivos Configurados

### 1. **docker-compose.yml**
- ✅ Serviço `web`: Django com runserver (porta 8000 interna)
- ✅ Serviço `nginx`: Proxy reverso (porta 80 pública)
- ✅ Serviço `db`: PostgreSQL (opcional)
- ✅ Web usa `expose` (não `ports`) - acessível apenas internamente
- ✅ Nginx depende do web estar saudável

### 2. **nginx.conf**
- ✅ Upstream configurado: `server web:8000`
- ✅ Proxy reverso para Django
- ✅ Servir arquivos estáticos (`/static/`)
- ✅ Servir arquivos de mídia (`/media/`)
- ✅ Rate limiting (API e login)
- ✅ Compressão Gzip
- ✅ Headers de segurança
- ✅ Health check (`/health/`)

### 3. **retro_games_cloud/settings.py**
- ✅ `USE_X_FORWARDED_HOST = True`
- ✅ `USE_X_FORWARDED_PORT = True`
- ✅ `SECURE_PROXY_SSL_HEADER` configurado
- ✅ `CSRF_TRUSTED_ORIGINS` sem porta (usa porta 80 do nginx)

### 4. **docker-entrypoint.sh**
- ✅ Executa migrações
- ✅ Coleta arquivos estáticos
- ✅ Executa comando do docker-compose (runserver)

### 5. **env.docker**
- ✅ `ALLOWED_HOSTS=localhost,127.0.0.1,web`
- ✅ `CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1`
- ✅ `DEBUG=True` (modo desenvolvimento)

## 🚀 Como Usar

### Iniciar o Sistema

```bash
docker-compose down
docker-compose up -d --build
```

Ou use o script:
```bash
start-nginx.bat  # Windows
```

### Acessar a Aplicação

- **URL**: http://localhost (porta 80 via nginx)
- **Admin**: http://localhost/admin
- **Login**: admin/admin123

### Ver Logs

```bash
# Logs do Django/runserver
docker-compose logs -f web

# Logs do nginx
docker-compose logs -f nginx

# Todos os logs
docker-compose logs -f
```

## 📊 Fluxo de Requisições

1. Cliente acessa `http://localhost`
2. Nginx recebe na porta 80
3. Nginx verifica se é arquivo estático (`/static/` ou `/media/`)
   - Se sim: serve diretamente
   - Se não: faz proxy para `web:8000`
4. Django runserver processa a requisição
5. Resposta é retornada via nginx

## 🔍 Verificações

### Verificar Status dos Containers

```bash
docker-compose ps
```

Deve mostrar:
- `retro_games_web` (up)
- `retro_games_nginx` (up)
- `retro_games_db` (up, se usar PostgreSQL)

### Testar Nginx

```bash
# Testar configuração do nginx
docker-compose exec nginx nginx -t

# Testar conectividade
curl http://localhost/health/
```

### Testar Django Diretamente

```bash
# Acessar shell do container
docker-compose exec web bash

# Verificar se runserver está rodando
docker-compose exec web ps aux | grep runserver
```

## 🐛 Troubleshooting

### Erro 502 Bad Gateway

1. Verifique se o container `web` está rodando:
   ```bash
   docker-compose ps web
   ```

2. Verifique os logs do Django:
   ```bash
   docker-compose logs web
   ```

3. Teste conectividade interna:
   ```bash
   docker-compose exec nginx wget -O- http://web:8000/
   ```

### Arquivos Estáticos não Carregam

1. Recolete os arquivos estáticos:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. Verifique permissões:
   ```bash
   docker-compose exec web ls -la /app/staticfiles/
   ```

### Erro CSRF

1. Verifique `CSRF_TRUSTED_ORIGINS` no `env.docker`
2. Deve estar sem porta: `http://localhost` (não `http://localhost:8000`)

## ✅ Checklist de Configuração

- [x] Nginx habilitado no docker-compose.yml
- [x] Web usando `expose` (não `ports`)
- [x] Nginx configurado como proxy reverso
- [x] Settings.py com configurações de proxy
- [x] CSRF_TRUSTED_ORIGINS sem porta 8000
- [x] ALLOWED_HOSTS configurado corretamente
- [x] Runserver configurado no docker-compose
- [x] Health checks configurados
- [x] Arquivos estáticos sendo servidos pelo nginx

## 📝 Notas

- **Modo Debug**: `DEBUG=True` está ativo (desenvolvimento)
- **Runserver**: Usando Django runserver (não Gunicorn)
- **Banco de Dados**: SQLite por padrão, pode usar PostgreSQL
- **Porta**: Nginx na porta 80, Django na porta 8000 (interna)

## 🔗 Próximos Passos

Para produção, considere:
1. Alterar `DEBUG=False`
2. Usar Gunicorn em vez de runserver
3. Configurar HTTPS/SSL
4. Ajustar rate limiting
5. Configurar backups do banco

---

**Status**: ✅ Sistema completamente configurado e pronto para uso com Nginx!

