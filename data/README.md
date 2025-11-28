# Pasta de Dados Iniciais

Esta pasta contém arquivos JSON com dados iniciais para popular o banco de dados.

## Arquivo de Jogos Iniciais

### Nome do Arquivo

O arquivo deve se chamar:
```
exemplos_iniciais.json
```

### Formato Esperado

O arquivo deve conter uma lista de objetos JSON, cada um representando um jogo:

```json
[
  {
    "name": "Nome do Jogo",
    "src": "https://www.retrogames.cc/embed/12345-exemplo.html",
    "image": "https://exemplo.com/imagem.png",
    "description": "Descrição opcional do jogo"
  }
]
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | string | ✅ Sim | Nome/título do jogo |
| `src` | string | ❌ Não | URL do embed/ROM do retrogames.cc ou serviço similar |
| `image` | string | ❌ Não | URL da imagem de capa do jogo (screenshot ou capa) |
| `description` | string | ❌ Não | Descrição do jogo (se não fornecido, será gerada automaticamente) |

### Mapeamento para o Modelo Game

O comando `load_initial_games` faz o seguinte mapeamento:

- `name` → `title` (modelo Game)
- `src` → `rom_url` (modelo Game) - URL da ROM/jogo no retrogames.cc
- `image` → `cover_image` (modelo Game) - URL da imagem de capa
- `description` → `description` (modelo Game) - usa a descrição fornecida ou gera uma padrão
- `slug` → gerado automaticamente a partir do título
- `is_active` → `True` por padrão

**Campos que não existem mais no modelo:**
- ❌ `console` - removido
- ❌ `is_visible` - removido (usamos apenas `is_active`)
- ❌ `categories` - removido

### Como Usar

Execute o comando Django:

```bash
python manage.py load_initial_games
```

Ou com Docker:

```bash
docker-compose exec web python manage.py load_initial_games
```

Para limpar todos os jogos existentes antes de recarregar:

```bash
python manage.py load_initial_games --reset
```

Para mais informações, consulte a documentação principal no README.md do projeto.
