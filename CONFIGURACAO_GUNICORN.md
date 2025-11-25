# 🔧 Configuração Gunicorn + Runserver

O sistema está configurado para funcionar com **ambos** os servidores: Runserver (desenvolvimento) e Gunicorn (produção).

## 📋 Como Funciona

O sistema escolhe automaticamente qual servidor usar baseado na variável de ambiente `WSGI_SERVER`:

- **`runserver`** (padrão): Django development server
- **`gunicorn`**: Gunicorn WSGI server (produção)

## ⚙️ Configuração

### 1. Via arquivo `env.docker`

```env
# Para desenvolvimento
WSGI_SERVER=runserver

# Para produção
WSGI_SERVER=gunicorn

# Configurações do Gunicorn (usado apenas quando WSGI_SERVER=gunicorn)
GUNICORN_WORKERS=3
GUNICORN_LOG_LEVEL=info
```

### 2. Via docker-compose.yml

Você pode sobrescrever no `docker-compose.yml`:

```yaml
environment:
  - WSGI_SERVER=gunicorn
  - GUNICORN_WORKERS=4
```

Ou comentar/descomentar o comando:

```yaml
# Para runserver (padrão)
# command: ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Para gunicorn
command: ["gunicorn", "retro_games_cloud.wsgi:application", "--config", "gunicorn_config.py", "--bind", "0.0.0.0:8000"]
```

## 🚀 Usar Runserver (Desenvolvimento)

**Arquivo `env.docker`:**
```env
WSGI_SERVER=runserver
```

Ou deixe sem configurar (é o padrão).

**Iniciar:**
```bash
docker-compose up -d --build
```

## 🏭 Usar Gunicorn (Produção)

**Arquivo `env.docker`:**
```env
WSGI_SERVER=gunicorn
GUNICORN_WORKERS=3
GUNICORN_LOG_LEVEL=info
```

**Iniciar:**
```bash
docker-compose up -d --build
```

## 📁 Arquivos de Configuração

### `gunicorn_config.py`

Arquivo de configuração do Gunicorn com:
- Workers baseados em CPU cores
- Timeout de 120 segundos
- Logging para stdout/stderr
- Configurações de performance e segurança

### `docker-entrypoint.sh`

Script que:
1. Verifica a variável `WSGI_SERVER`
2. Inicia runserver ou gunicorn conforme configurado
3. Se receber comando explícito do docker-compose, usa esse comando

## 🔄 Alternar entre Runserver e Gunicorn

### Opção 1: Alterar env.docker

1. Edite `env.docker`
2. Mude `WSGI_SERVER=runserver` para `WSGI_SERVER=gunicorn` (ou vice-versa)
3. Reinicie: `docker-compose restart web`

### Opção 2: Sobrescrever no docker-compose.yml

1. Edite `docker-compose.yml`
2. Comente/descomente o comando apropriado
3. Reinicie: `docker-compose restart web`

## 📊 Comparação

| Recurso | Runserver | Gunicorn |
|---------|-----------|----------|
| **Uso** | Desenvolvimento | Produção |
| **Performance** | Baixa | Alta |
| **Auto-reload** | ✅ Sim | ❌ Não |
| **Workers** | 1 processo | Múltiplos workers |
| **Timeout** | Sem limite prático | Configurável |
| **Logs detalhados** | ✅ Sim | ⚠️ Configurável |
| **Debug** | ✅ Fácil | ⚠️ Mais difícil |

## 🎯 Recomendações

### Desenvolvimento
- Use **runserver** para desenvolvimento
- Permite auto-reload ao alterar código
- Logs mais detalhados de erros

### Produção
- Use **gunicorn** para produção
- Melhor performance e estabilidade
- Suporta múltiplos workers
- Melhor para carga alta

## 🔍 Verificar qual servidor está rodando

```bash
# Ver processos
docker-compose exec web ps aux

# Ver logs
docker-compose logs web | grep -i "runserver\|gunicorn"
```

## ⚙️ Configurações do Gunicorn

As configurações podem ser ajustadas no `gunicorn_config.py` ou via variáveis de ambiente:

- `GUNICORN_WORKERS`: Número de workers (padrão: 3)
- `GUNICORN_LOG_LEVEL`: Nível de log (padrão: info)

Ou edite diretamente `gunicorn_config.py` para configurações mais avançadas.

## 📝 Exemplo de Uso

### Desenvolvimento
```bash
# env.docker
WSGI_SERVER=runserver

# Iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f web
```

### Produção
```bash
# env.docker
WSGI_SERVER=gunicorn
GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=warning

# Iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f web
```

## ✅ Checklist

- [x] Gunicorn configurado
- [x] Runserver configurado
- [x] Variável WSGI_SERVER funcionando
- [x] gunicorn_config.py criado
- [x] docker-entrypoint.sh atualizado
- [x] env.docker atualizado
- [x] docker-compose.yml atualizado
- [x] Nginx funciona com ambos

---

**Status**: ✅ Sistema configurado para funcionar com Runserver e Gunicorn!

