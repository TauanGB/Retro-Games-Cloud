# Como usar o Sistema de Configuração de Dados

## Visão Geral

Todos os scripts de criação de planos e consoles foram consolidados em um único comando Django e uma URL API. Agora você pode configurar os dados iniciais do sistema de duas formas:

## 1. Via Comando Django (Terminal)

### Comando Básico
```bash
python manage.py setup_data
```

### Opções Disponíveis
```bash
# Criar apenas categorias
python manage.py setup_data --categories-only

# Criar apenas planos
python manage.py setup_data --plans-only

# Forçar recriação (atualizar dados existentes)
python manage.py setup_data --force

# Combinar opções
python manage.py setup_data --categories-only --force
```

## 2. Via URL API (HTTP)

### Endpoint
```
POST /api/setup-data/
```

### Exemplos de Uso

#### Configuração Completa
```bash
curl -X POST http://localhost:8000/api/setup-data/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Apenas Categorias
```bash
curl -X POST http://localhost:8000/api/setup-data/ \
  -H "Content-Type: application/json" \
  -d '{"categories_only": true}'
```

#### Apenas Planos
```bash
curl -X POST http://localhost:8000/api/setup-data/ \
  -H "Content-Type: application/json" \
  -d '{"plans_only": true}'
```

#### Forçar Recriação
```bash
curl -X POST http://localhost:8000/api/setup-data/ \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Resposta da API
```json
{
  "success": true,
  "message": "Dados iniciais configurados com sucesso",
  "output": "=== CONFIGURANDO DADOS INICIAIS ===\n\n=== CRIANDO CATEGORIAS ===\n[OK] Categoria criada: Ação\n..."
}
```

## O que o Sistema Faz

### 1. Criação de Categorias
- Cria 10 categorias padrão (Ação, Aventura, RPG, Plataforma, etc.)
- Associa categorias aos jogos baseado em palavras-chave
- Atribui categorias padrão para jogos sem classificação específica

### 2. Criação de Planos por Console
- Cria planos específicos para cada console (NES, SNES, PlayStation, etc.)
- Define preços baseados na popularidade/era do console
- Associa todos os jogos do console ao plano correspondente

### 3. Criação de Planos Gerais
- **Plano Básico**: Jogos dos consoles clássicos (NES, Game Boy, GBA, Mega Drive) - R$ 19,90
- **Plano Premium**: Todos os jogos da plataforma - R$ 39,90

### 4. Estatísticas
- Mostra total de planos criados
- Lista jogos por categoria
- Breakdown por console
- Jogos sem categoria

## Preços dos Planos por Console

| Console | Preço |
|---------|-------|
| Arcade | R$ 15,90 |
| GBA | R$ 12,90 |
| Game Boy | R$ 9,90 |
| Mega Drive | R$ 14,90 |
| NES | R$ 11,90 |
| Neo Geo | R$ 19,90 |
| PC | R$ 16,90 |
| PlayStation | R$ 18,90 |
| SNES | R$ 13,90 |

## Vantagens da Nova Implementação

1. **Consolidação**: Todos os scripts em um único comando
2. **Flexibilidade**: Opções para executar partes específicas
3. **API**: Execução via HTTP para integração com outros sistemas
4. **Logs**: Saída detalhada do processo
5. **Segurança**: Transações atômicas para evitar dados inconsistentes
6. **Manutenção**: Código centralizado e mais fácil de manter

## Scripts Removidos

Os seguintes scripts foram removidos após a consolidação:
- `create_console_plans_simple.py`
- `create_plans_console.py`
- `populate_console_plans.py`
- `populate_categories.py`

Toda a funcionalidade foi movida para `games/management/commands/setup_data.py`.
