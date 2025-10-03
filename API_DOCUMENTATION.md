# Documentação da API de Tokens - Retro Games Cloud

## Visão Geral

O sistema de tokens permite que outros sistemas validem o acesso de usuários a jogos específicos através de tokens seguros gerados após a compra. Cada token é único, possui hash seguro e pode ser validado via API REST.

## Funcionalidades Implementadas

### 1. Geração Automática de Tokens
- Tokens são gerados automaticamente após compra bem-sucedida de jogos
- Cada token é único e vinculado a um usuário e jogo específico
- Tokens são armazenados com hash SHA-256 para segurança

### 2. Validação de Tokens
- Validação via método de classe `GameToken.validate_token()`
- Suporte a validação com `game_id` específico
- Contador de uso automático
- Verificação de expiração e status

### 3. API REST para Validação Externa
- Endpoint para validação de tokens
- Endpoint para obter informações de jogos
- Endpoint para revogação de tokens
- Endpoint para listar tokens do usuário

## Endpoints da API

### 1. Validar Token
**POST** `/api/validate-token/`

Valida um token de acesso a jogo.

#### Request Body
```json
{
    "token": "string (obrigatório)",
    "game_id": "integer (opcional)"
}
```

#### Response (Sucesso - 200)
```json
{
    "valid": true,
    "game": {
        "id": 123,
        "title": "Super Mario World",
        "console": "SNES",
        "description": "Um clássico jogo de plataforma"
    },
    "user": {
        "id": 456,
        "username": "usuario",
        "email": "usuario@example.com"
    },
    "entitlement": {
        "is_perpetual": true,
        "granted_date": "2024-01-01T00:00:00Z"
    },
    "token_info": {
        "created_at": "2024-01-01T00:00:00Z",
        "last_used_at": "2024-01-01T00:00:00Z",
        "usage_count": 5,
        "expires_at": null
    }
}
```

#### Response (Erro - 400/401)
```json
{
    "valid": false,
    "error": "Token é obrigatório"
}
```

### 2. Obter Informações do Jogo
**GET** `/api/game/{game_id}/`

Obtém informações detalhadas de um jogo específico.

#### Response (Sucesso - 200)
```json
{
    "id": 123,
    "title": "Super Mario World",
    "console": "SNES",
    "description": "Um clássico jogo de plataforma",
    "price": "29.99",
    "cover_image": "https://example.com/mario.jpg",
    "rom_url": "https://example.com/mario.sfc",
    "categories": [
        {
            "id": 1,
            "name": "Ação",
            "color": "#ff0000",
            "icon": "fas fa-sword"
        }
    ]
}
```

#### Response (Erro - 404)
```json
{
    "error": "Jogo não encontrado"
}
```

### 3. Revogar Token
**POST** `/api/revoke-token/`

Revoga um token de acesso.

#### Request Body
```json
{
    "token": "string (obrigatório)"
}
```

#### Response (Sucesso - 200)
```json
{
    "success": true,
    "message": "Token revogado com sucesso"
}
```

#### Response (Erro - 400/404)
```json
{
    "success": false,
    "error": "Token não encontrado"
}
```

### 4. Listar Tokens do Usuário
**GET** `/api/user/tokens/`

Lista todos os tokens ativos do usuário logado.

#### Response (Sucesso - 200)
```json
{
    "tokens": [
        {
            "id": 123,
            "game": {
                "id": 456,
                "title": "Super Mario World",
                "console": "SNES"
            },
            "token": "5WiRyvf6fE3LkP7aekebV7sLN78MZN0-OnI4Em17pbI",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "last_used_at": "2024-01-01T00:00:00Z",
            "usage_count": 5,
            "expires_at": null
        }
    ]
}
```

## Modelo de Dados

### GameToken
```python
class GameToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    entitlement = models.ForeignKey(Entitlement, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    token_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
```

## Segurança

### 1. Hash de Tokens
- Tokens são armazenados com hash SHA-256
- O token original é mantido apenas para retorno ao usuário
- Validação é feita através do hash, não do token original

### 2. Validação de Acesso
- Tokens são vinculados a usuários e jogos específicos
- Verificação de status (ativo, expirado, revogado)
- Contador de uso para auditoria

### 3. Expiração
- Tokens podem ter data de expiração
- Verificação automática de expiração durante validação
- Status atualizado automaticamente para "expirado"

## Exemplos de Uso

### 1. Validação de Token em Sistema Externo
```python
import requests

# Validar token
response = requests.post(
    'http://localhost:8000/api/validate-token/',
    json={
        'token': '5WiRyvf6fE3LkP7aekebV7sLN78MZN0-OnI4Em17pbI',
        'game_id': 123
    }
)

if response.status_code == 200:
    data = response.json()
    if data['valid']:
        print(f"Usuário {data['user']['username']} tem acesso ao jogo {data['game']['title']}")
    else:
        print("Token inválido")
```

### 2. Obter Informações do Jogo
```python
# Obter informações do jogo
response = requests.get('http://localhost:8000/api/game/123/')

if response.status_code == 200:
    game_data = response.json()
    print(f"Jogo: {game_data['title']} ({game_data['console']})")
    print(f"Preço: R$ {game_data['price']}")
```

### 3. Revogar Token
```python
# Revogar token
response = requests.post(
    'http://localhost:8000/api/revoke-token/',
    json={'token': '5WiRyvf6fE3LkP7aekebV7sLN78MZN0-OnI4Em17pbI'}
)

if response.status_code == 200:
    data = response.json()
    if data['success']:
        print("Token revogado com sucesso")
```

## Integração com Sistema de Compras

### Fluxo de Geração de Token
1. Usuário realiza compra de jogo
2. Sistema cria `Purchase` com status "completed"
3. Sistema cria `Entitlement` vinculado à compra
4. Sistema gera automaticamente `GameToken` vinculado ao entitlement
5. Token fica disponível para uso imediato

### Fluxo de Validação
1. Sistema externo recebe token do usuário
2. Sistema externo faz requisição para `/api/validate-token/`
3. API valida token e retorna informações do jogo e usuário
4. Sistema externo permite ou nega acesso baseado na resposta

## Códigos de Status HTTP

- **200**: Sucesso
- **400**: Erro de validação (dados inválidos)
- **401**: Token inválido ou expirado
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor

## Considerações de Performance

- Tokens são indexados por hash para consultas rápidas
- Validação inclui `select_related` para otimizar consultas
- Cache pode ser implementado para tokens frequentemente validados
- Contador de uso é atualizado de forma eficiente

## Monitoramento e Auditoria

- Todos os usos de tokens são registrados com timestamp
- Contador de uso permite identificar tokens mais utilizados
- Status de tokens pode ser monitorado via admin do Django
- Logs de validação podem ser implementados para auditoria

## Próximos Passos

1. Implementar rate limiting para endpoints da API
2. Adicionar autenticação por API key para sistemas externos
3. Implementar cache Redis para validações frequentes
4. Adicionar logs detalhados de validação
5. Implementar notificações de expiração de tokens
6. Adicionar suporte a tokens com escopo limitado (tempo de uso)
