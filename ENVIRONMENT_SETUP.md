# Configuração de Variáveis de Ambiente

Este projeto está configurado para usar variáveis de ambiente para todas as configurações sensíveis e específicas do ambiente.

## Como usar

### 1. Desenvolvimento Local

1. Copie o arquivo de exemplo:
```bash
cp env.example .env
```

2. Edite o arquivo `.env` com suas configurações:
```bash
# Configurações do Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados (SQLite para desenvolvimento)
DATABASE_URL=sqlite:///db.sqlite3

# Configurações de email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### 2. Produção com Docker

Use o arquivo `env.docker` que já está configurado para o ambiente Docker.

### 3. Produção com PostgreSQL

Para usar PostgreSQL em produção, configure a variável `DATABASE_URL`:

```bash
DATABASE_URL=postgres://usuario:senha@localhost:5432/nome_do_banco
```

### 4. Produção com MySQL

Para usar MySQL em produção, configure a variável `DATABASE_URL`:

```bash
DATABASE_URL=mysql://usuario:senha@localhost:3306/nome_do_banco
```

## Variáveis Disponíveis

### Configurações Básicas
- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: Modo debug (True/False)
- `ALLOWED_HOSTS`: Hosts permitidos (separados por vírgula)

### Banco de Dados
- `DATABASE_URL`: URL completa do banco de dados

### Email
- `EMAIL_HOST`: Servidor SMTP
- `EMAIL_PORT`: Porta do servidor SMTP
- `EMAIL_USE_TLS`: Usar TLS (True/False)
- `EMAIL_HOST_USER`: Usuário do email
- `EMAIL_HOST_PASSWORD`: Senha do email
- `DEFAULT_FROM_EMAIL`: Email remetente padrão

### Segurança
- `SECURE_SSL_REDIRECT`: Redirecionar para HTTPS (True/False)
- `SECURE_HSTS_SECONDS`: Duração do HSTS em segundos
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`: Incluir subdomínios no HSTS (True/False)
- `SECURE_HSTS_PRELOAD`: Pré-carregar HSTS (True/False)

### Mídia e Arquivos Estáticos
- `MEDIA_URL`: URL para arquivos de mídia
- `STATIC_URL`: URL para arquivos estáticos

## Exemplos de Configuração

### Desenvolvimento
```bash
SECRET_KEY=dev-key-123
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Produção com PostgreSQL
```bash
SECRET_KEY=production-secret-key-very-long-and-secure
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DATABASE_URL=postgres://usuario:senha@localhost:5432/retro_games_db
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## Segurança

⚠️ **IMPORTANTE**: 
- Nunca commite arquivos `.env` no Git
- Use chaves secretas diferentes para cada ambiente
- Em produção, sempre use `DEBUG=False`
- Configure HTTPS em produção com `SECURE_SSL_REDIRECT=True`
