# 🔧 Nginx Desabilitado - Modo Debug

**Status**: Nginx está **DESABILITADO** temporariamente para identificar erros.

## 📋 Configuração Atual

- ✅ **Nginx**: Desabilitado (comentado no docker-compose.yml)
- ✅ **Django/Gunicorn**: Rodando diretamente na porta 8000
- ✅ **WhiteNoise**: Ativado para servir arquivos estáticos
- ✅ **Acesso direto**: http://localhost:8000

## 🚀 Como Usar

### 1. Iniciar o Sistema

```bash
docker-compose down
docker-compose up -d --build
```

### 2. Ver Logs em Tempo Real

```bash
# Windows
docker-compose logs -f web

# Linux/Mac
docker-compose logs -f web | tee logs-debug.txt
```

Ou use o script:
```bash
# Windows
check-logs.bat

# Linux/Mac
./check-logs.sh
```

### 3. Acessar a Aplicação

- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Login padrão**: admin/admin123

## 🔍 Verificações de Debug

### Verificar Status dos Containers

```bash
docker-compose ps
```

### Ver Logs Recentes

```bash
docker-compose logs --tail=100 web
```

### Verificar Erros Específicos

```bash
docker-compose logs web | grep -i error
docker-compose logs web | grep -i traceback
docker-compose logs web | grep -i exception
```

### Acessar Shell do Container

```bash
docker-compose exec web bash
```

### Testar Conectividade Interna

```bash
docker-compose exec web curl http://localhost:8000/
```

### Verificar Configurações do Django

```bash
docker-compose exec web python manage.py check
docker-compose exec web python manage.py check --deploy
```

### Verificar Banco de Dados

```bash
docker-compose exec web python manage.py dbshell
```

## 🐛 Problemas Comuns

### Container não inicia

1. Verifique os logs:
   ```bash
   docker-compose logs web
   ```

2. Verifique se a porta 8000 está disponível:
   ```bash
   netstat -ano | findstr :8000  # Windows
   lsof -i :8000                 # Linux/Mac
   ```

### Erro "DisallowedHost"

Adicione o host no `env.docker`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,web,0.0.0.0,SEU_IP
```

### Arquivos Estáticos não Carregam

1. Recolete os arquivos estáticos:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. Verifique se o WhiteNoise está funcionando:
   ```bash
   docker-compose exec web curl http://localhost:8000/static/css/modern-retro.css
   ```

### Erro de Banco de Dados

1. Execute as migrações:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

2. Verifique a conexão:
   ```bash
   docker-compose exec web python manage.py dbshell
   ```

## 📝 Reabilitar Nginx

Quando terminar o debug, para reabilitar o nginx:

1. **Descomente o serviço nginx** no `docker-compose.yml`
2. **Mude `ports` para `expose`** no serviço `web`:
   ```yaml
   expose:
     - "8000"
   ```
3. **Reabilite as configurações de proxy** no `settings.py`:
   ```python
   USE_X_FORWARDED_HOST = True
   USE_X_FORWARDED_PORT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

## 📞 Informações Úteis

- **Logs do Gunicorn**: Saída direta no console (--access-logfile - --error-logfile -)
- **Allowed Hosts**: Configurado via variável de ambiente `ALLOWED_HOSTS`
- **CSRF Origins**: Configurado via variável de ambiente `CSRF_TRUSTED_ORIGINS`
- **Banco de Dados**: SQLite por padrão, pode usar PostgreSQL alterando `DATABASE_URL`

## 🔗 Comandos Rápidos

```bash
# Reiniciar apenas o serviço web
docker-compose restart web

# Rebuild e reiniciar
docker-compose up -d --build web

# Parar tudo
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

