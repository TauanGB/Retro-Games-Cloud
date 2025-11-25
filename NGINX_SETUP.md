# Configuração do Nginx para Retro Games Cloud

Este documento descreve como configurar e executar o sistema Retro Games Cloud usando Nginx como proxy reverso.

## 📋 Pré-requisitos

- Docker (versão 20.10 ou superior)
- Docker Compose (versão 2.0 ou superior)

## 🚀 Início Rápido

### 1. Preparação

Certifique-se de que o arquivo `env.docker` está configurado corretamente:

```bash
# Copie o arquivo de exemplo se necessário
cp env.example env.docker
```

Edite `env.docker` com suas configurações, especialmente:
- `SECRET_KEY`: Chave secreta do Django
- `ALLOWED_HOSTS`: Domínios permitidos
- `CSRF_TRUSTED_ORIGINS`: Origens confiáveis para CSRF

### 2. Construir e Iniciar os Containers

```bash
# Construir as imagens
docker-compose build

# Iniciar os serviços
docker-compose up -d

# Verificar o status
docker-compose ps
```

### 3. Verificar os Logs

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas do Django
docker-compose logs -f web

# Logs apenas do Nginx
docker-compose logs -f nginx
```

### 4. Acessar a Aplicação

- **Aplicação**: http://localhost
- **Admin Django**: http://localhost/admin
- **Health Check**: http://localhost/health/

Credenciais padrão do superusuário (apenas em DEBUG=True):
- Usuário: `admin`
- Senha: `admin123`

## 🏗️ Arquitetura

O sistema está configurado com:

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ HTTP/HTTPS (porta 80/443)
       ▼
┌─────────────┐
│    Nginx    │ ← Proxy Reverso
│  (porta 80) │
└──────┬──────┘
       │
       │ Proxy HTTP (porta 8000)
       ▼
┌─────────────┐
│    Django   │ ← Gunicorn WSGI
│  (porta 8000)│
└─────────────┘
```

### Serviços

1. **Web (Django)**: Aplicação Django rodando com Gunicorn
2. **Nginx**: Proxy reverso que serve arquivos estáticos e encaminha requisições

## 📁 Estrutura de Arquivos

```
.
├── docker-compose.yml      # Orquestração dos serviços
├── Dockerfile              # Imagem do Django
├── Dockerfile.nginx        # Imagem do Nginx
├── nginx.conf              # Configuração do Nginx
├── docker-entrypoint.sh    # Script de inicialização do Django
├── env.docker              # Variáveis de ambiente para Docker
└── nginx_logs/             # Logs do Nginx (criado automaticamente)
```

## ⚙️ Configurações

### Nginx

O arquivo `nginx.conf` está configurado para:

- Servir arquivos estáticos (`/static/`) diretamente
- Servir arquivos de mídia (`/media/`) diretamente
- Encaminhar todas as outras requisições para o Django
- Suportar uploads de até 100MB
- Compressão gzip para melhor performance
- Headers de cache para arquivos estáticos

### Django

Configurado para funcionar atrás de proxy reverso:

- `USE_X_FORWARDED_HOST = True`: Respeita o host do proxy
- `SECURE_PROXY_SSL_HEADER`: Configurado para HTTPS (quando habilitado)
- `STATIC_ROOT` e `MEDIA_ROOT`: Configurados para volumes Docker

### Volumes

O docker-compose cria volumes nomeados para:

- `static_volume`: Arquivos estáticos coletados pelo Django
- `media_volume`: Arquivos de mídia enviados pelos usuários

Esses volumes são compartilhados entre os containers.

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Parar e remover volumes (CUIDADO: remove dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart web
docker-compose restart nginx

# Reconstruir após mudanças
docker-compose up -d --build
```

### Comandos Django

```bash
# Executar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic

# Acessar shell do Django
docker-compose exec web python manage.py shell

# Executar comandos customizados
docker-compose exec web python manage.py <comando>
```

### Logs e Debug

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver últimos 100 linhas
docker-compose logs --tail=100

# Ver logs de erro do Nginx
docker-compose exec nginx tail -f /var/log/nginx/error.log

# Verificar configuração do Nginx
docker-compose exec nginx nginx -t
```

## 🔒 Configuração HTTPS/SSL

Para habilitar HTTPS:

1. Obtenha certificados SSL (Let's Encrypt, etc.)
2. Coloque os certificados em um diretório `ssl/`:
   - `ssl/cert.pem`
   - `ssl/key.pem`

3. Descomente e ajuste a seção HTTPS no `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... resto da configuração
}
```

4. Adicione o volume no `docker-compose.yml`:

```yaml
volumes:
  - ./ssl:/etc/nginx/ssl:ro
```

5. Configure as variáveis de ambiente:

```env
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
```

6. Reinicie os serviços:

```bash
docker-compose down
docker-compose up -d
```

## 🐛 Troubleshooting

### Problema: Arquivos estáticos não aparecem

**Solução**: Execute o collectstatic novamente:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Problema: Erro 502 Bad Gateway

**Solução**: Verifique se o container `web` está rodando:
```bash
docker-compose ps
docker-compose logs web
```

### Problema: Erro de permissão

**Solução**: Verifique as permissões dos volumes:
```bash
docker-compose exec web ls -la /app/staticfiles
docker-compose exec nginx ls -la /app/staticfiles
```

### Problema: Nginx não inicia

**Solução**: Verifique a sintaxe do nginx.conf:
```bash
docker-compose exec nginx nginx -t
```

### Problema: CSRF token inválido

**Solução**: Verifique `CSRF_TRUSTED_ORIGINS` no `env.docker`:
```env
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://seu-dominio.com
```

## 📊 Monitoramento

### Health Checks

O sistema inclui health checks automáticos:

- **Django**: `/health/` - Verifica se a aplicação e banco estão funcionando
- **Nginx**: Verifica a sintaxe da configuração

Para verificar manualmente:

```bash
# Django
curl http://localhost/health/

# Nginx
docker-compose exec nginx nginx -t
```

### Logs

Os logs são salvos em:

- **Django**: Saída padrão (via `docker-compose logs`)
- **Nginx**: `./nginx_logs/` (no host) e `/var/log/nginx/` (no container)

## 🔄 Atualização

Para atualizar o sistema:

```bash
# Parar serviços
docker-compose down

# Atualizar código (git pull, etc.)

# Reconstruir imagens
docker-compose build

# Iniciar novamente
docker-compose up -d

# Executar migrações se necessário
docker-compose exec web python manage.py migrate
```

## 📝 Notas Importantes

1. **Produção**: Altere `DEBUG=False` e configure uma `SECRET_KEY` forte
2. **Banco de Dados**: Para produção, use PostgreSQL ou MySQL ao invés de SQLite
3. **Segurança**: Configure HTTPS antes de colocar em produção
4. **Backup**: Configure backups regulares do banco de dados e arquivos de mídia
5. **Performance**: Ajuste o número de workers do Gunicorn conforme necessário

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `docker-compose logs`
2. Consulte a documentação do Django: https://docs.djangoproject.com/
3. Consulte a documentação do Nginx: https://nginx.org/en/docs/

---

**Desenvolvido com ❤️ para a comunidade de jogos retrô**

