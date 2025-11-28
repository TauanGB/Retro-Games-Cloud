# Notas sobre a Migração 0004

## Problema Encontrado

Ao executar `python manage.py migrate`, o Django pode reclamar sobre campos que estão sendo alterados de nullable para non-nullable sem valores padrão.

## Solução Aplicada

### 1. Campos Ajustados no Modelo

Os campos `slug` e `retrogames_embed_url` agora permitem valores `null=True`:

```python
slug = models.SlugField(..., null=True, ...)
retrogames_embed_url = models.URLField(..., null=True, ...)
```

### 2. Migração com Preenchimento Automático

A migração `0004_update_game_model_for_tde.py` inclui:

- Adição dos campos como nullable
- Função `populate_slugs()` que preenche slugs automaticamente para registros existentes baseado no título
- Remoção dos campos antigos `price` e `rom_url`

### 3. Se os Campos `price` ou `rom_url` Não Existirem

Se você receber um erro ao tentar remover esses campos (porque já foram removidos anteriormente), você pode:

**Opção 1**: Comentar as linhas de remoção na migração:
```python
# migrations.RemoveField(
#     model_name='game',
#     name='price',
# ),
# migrations.RemoveField(
#     model_name='game',
#     name='rom_url',
# ),
```

**Opção 2**: Criar uma migração separada que verifica se os campos existem antes de remover.

## Como Executar a Migração

```bash
# Criar a migração (se ainda não foi criada)
python manage.py makemigrations

# Aplicar a migração
python manage.py migrate
```

## Valores Padrão

- **slug**: Será gerado automaticamente a partir do título quando um jogo for salvo
- **retrogames_embed_url**: Pode ser deixado em branco e preenchido depois via admin

## Verificação Pós-Migração

Após a migração, verifique:

1. Todos os jogos têm slug:
```python
from games.models import Game
Game.objects.filter(slug__isnull=True).count()  # Deve retornar 0
```

2. Os campos antigos foram removidos (se existiam):
```python
# Isso deve dar erro se os campos foram removidos corretamente
Game.objects.first().price  # AttributeError esperado
```

## Próximos Passos

1. Preencher `retrogames_embed_url` para os jogos existentes via admin
2. Verificar se todos os slugs foram gerados corretamente
3. Testar a visualização dos jogos no catálogo





