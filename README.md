# Jogos Retro - TDE

PWA (Progressive Web App) educacional desenvolvido como Trabalho de Desenvolvimento de Engenharia (TDE).

## 📋 Descrição

Este projeto é um Progressive Web App que permite aos usuários explorar um catálogo de jogos retro clássicos e jogá-los diretamente no navegador através do emulador fornecido pelo serviço [retrogames.cc](https://www.retrogames.cc).

### Características Principais

- **Catálogo de Jogos Retro**: Lista de jogos organizados por console e categoria
- **Emulador Embutido**: Jogos executados via iframe do retrogames.cc
- **PWA Funcional**: Instalável em dispositivos móveis e desktop
- **Suporte Offline**: Interface e informações dos jogos funcionam offline (o emulador requer internet)
- **Design Responsivo**: Interface mobile-first com Bootstrap 5

## 🛠️ Tecnologias

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **PWA**: Service Worker, Web App Manifest
- **Emulador**: retrogames.cc (via iframe)

## 📦 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Docker e Docker Compose (opcional, mas recomendado)
- PostgreSQL (opcional, SQLite é usado por padrão)

### Instalação Local

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Retro-Games-Cloud
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp env.example env.docker
# Edite env.docker com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

7. Execute o servidor de desenvolvimento:
```bash
python manage.py runserver
```

### Instalação com Docker

1. Configure as variáveis de ambiente:
```bash
cp env.example env.docker
# Edite env.docker conforme necessário
```

2. Inicie os containers:
```bash
docker-compose up -d
```

3. Execute as migrações:
```bash
docker-compose exec web python manage.py migrate
```

4. Crie um superusuário (opcional):
```bash
docker-compose exec web python manage.py createsuperuser
```

O aplicativo estará disponível em `http://localhost` (via Nginx) ou `http://localhost:8000` (Django direto).

## 🎮 Cadastrando Jogos

### Via Admin do Django

1. Acesse o admin: `http://localhost:8000/admin/`
2. Faça login com um superusuário
3. Vá em **Games** > **Add Game**
4. Preencha os campos:
   - **Título**: Nome do jogo
   - **Slug**: Será gerado automaticamente se deixado em branco
   - **Descrição**: Descrição do jogo
   - **Console/Plataforma**: Ex: SNES, NES, GBA, etc.
   - **URL da Capa**: URL da imagem de capa do jogo
   - **URL de Embed do Retrogames.cc**: URL completa do embed
     - Exemplo: `https://www.retrogames.cc/embed/[ID_DO_JOGO]`
   - **Categorias**: Selecione as categorias do jogo
   - **Ativo** e **Visível no Catálogo**: Marque para que o jogo apareça

### Como Obter a URL de Embed do Retrogames.cc

1. Acesse [retrogames.cc](https://www.retrogames.cc)
2. Encontre o jogo desejado
3. Na página do jogo, procure pela opção de embed ou compartilhamento
4. Copie a URL do embed (geralmente no formato `https://www.retrogames.cc/embed/[ID]`)
5. Cole essa URL no campo **URL de Embed do Retrogames.cc** no admin

### Carregar Jogos Iniciais do JSON

O projeto inclui um management command para popular o banco de dados com jogos a partir de um arquivo JSON.

#### Localização do Arquivo

O arquivo JSON deve estar localizado em:
```
<project_root>/data/exemplos_iniciais.json
```

Se a pasta `data/` não existir, ela será criada automaticamente quando você executar o comando (mas você precisa criar o arquivo JSON manualmente).

#### Formato do JSON

O arquivo deve conter uma lista de objetos, cada um representando um jogo:

```json
[
  {
    "name": "Nome do Jogo",
    "src": "https://www.retrogames.cc/embed/12345-exemplo.html",
    "image": "https://exemplo.com/imagem.png",
    "description": "Descrição opcional do jogo"
  },
  ...
]
```

**Campos do JSON:**
- `name` (obrigatório): Nome/título do jogo
- `src` (opcional): URL do embed/ROM do retrogames.cc ou serviço similar
- `image` (opcional): URL da imagem de capa do jogo (screenshot ou capa)
- `description` (opcional): Descrição do jogo (se não fornecido, será gerada automaticamente)

**Mapeamento automático:**
- `name` → `title` (modelo Game)
- `src` → `rom_url` (modelo Game) - URL da ROM/jogo
- `image` → `cover_image` (modelo Game) - URL da imagem de capa
- `description` → `description` (modelo Game) - ou descrição padrão se não fornecido
- O slug é gerado automaticamente a partir do título
- Jogos são marcados como ativos (`is_active=True`) por padrão

**Nota:** O modelo atual foi simplificado. Campos como `console`, `is_visible` e `categories` foram removidos.

#### Executando o Comando

**Carregar jogos (idempotente - não cria duplicatas):**
```bash
python manage.py load_initial_games
```

**Limpar todos os jogos existentes antes de recarregar:**
```bash
python manage.py load_initial_games --reset
```

**Usar um arquivo JSON em outro caminho:**
```bash
python manage.py load_initial_games --json-file caminho/para/seu/arquivo.json
```

#### Com Docker

Se estiver usando Docker, execute o comando dentro do container:

```bash
docker-compose exec web python manage.py load_initial_games
```

#### Características do Comando

- ✅ **Idempotente**: Pode ser executado múltiplas vezes sem criar duplicatas (usa slug como identificador único)
- ✅ **Atualização inteligente**: Se um jogo já existe, apenas atualiza campos modificados
- ✅ **Detecção automática de console**: Identifica o console a partir do nome do jogo ou padrões nos URLs
- ✅ **Tratamento de erros**: Exibe mensagens claras sobre problemas e continua processando outros jogos
- ✅ **Logs detalhados**: Mostra quais jogos foram criados, atualizados ou ignorados

## 📱 Funcionalidades PWA

### Instalação

O PWA pode ser instalado em dispositivos móveis e desktop:

- **Android/Chrome**: Menu > "Adicionar à tela inicial"
- **iOS/Safari**: Compartilhar > "Adicionar à Tela de Início"
- **Desktop/Chrome**: Ícone de instalação na barra de endereços

### Funcionamento Offline

- **Interface**: Funciona offline após o primeiro carregamento
- **Informações dos Jogos**: Textos e imagens são cacheados
- **Emulador**: Requer conexão com a internet (fornecido pelo retrogames.cc)

Quando o usuário estiver offline, a interface mostrará uma mensagem informando que o emulador só funciona online.

## 🗂️ Estrutura do Projeto

```
Retro-Games-Cloud/
├── games/                    # App principal
│   ├── models.py            # Modelos: Game, Category
│   ├── views.py             # Views simplificadas
│   ├── urls.py              # Rotas
│   ├── admin.py             # Configuração do admin
│   └── templates/           # Templates HTML
├── static/                   # Arquivos estáticos
│   ├── css/                 # Estilos CSS
│   ├── manifest.json        # Manifest do PWA
│   └── service-worker.js    # Service Worker
├── retro_games_cloud/       # Configurações do Django
│   ├── settings.py         # Configurações
│   └── urls.py             # URLs principais
├── docker-compose.yml       # Configuração Docker
├── Dockerfile              # Imagem Docker
└── requirements.txt        # Dependências Python
```

## 🔧 Configurações Importantes

### Variáveis de Ambiente

Principais variáveis em `env.docker`:

- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: Modo debug (True/False)
- `ALLOWED_HOSTS`: Hosts permitidos
- `DATABASE_URL`: URL do banco de dados (SQLite por padrão)

### Service Worker

O Service Worker está configurado em `static/service-worker.js` e implementa:

- Cache de arquivos estáticos (app shell)
- Estratégia Network First com fallback para Cache
- Suporte offline para interface e conteúdo textual

## 🚀 Deploy

### Produção

1. Configure `DEBUG=False` em `env.docker`
2. Configure `ALLOWED_HOSTS` com seu domínio
3. Configure SSL/HTTPS (recomendado)
4. Use PostgreSQL em produção (não SQLite)
5. Configure variáveis de ambiente de produção

### Docker em Produção

```bash
docker-compose -f docker-compose.yml up -d
```

## 📝 Notas Importantes

- O emulador é fornecido por terceiros (retrogames.cc) e requer conexão com a internet
- O PWA funciona offline apenas para a interface e informações dos jogos
- Não há sistema de autenticação obrigatória - o catálogo é público
- O sistema foi simplificado removendo funcionalidades de compra/assinatura/tokens do projeto original

## 🐛 Troubleshooting

### Service Worker não registra

- Verifique se está servindo via HTTPS ou localhost
- Verifique o console do navegador para erros
- Limpe o cache do navegador

### Iframe do emulador não carrega

- Verifique se a URL de embed está correta
- Verifique se há bloqueadores de conteúdo (AdBlock, etc.)
- Verifique a conexão com a internet

### Migrações não aplicam

```bash
python manage.py makemigrations
python manage.py migrate
```

## 📄 Licença

Este projeto foi desenvolvido como Trabalho de Desenvolvimento de Engenharia (TDE) e é destinado a fins educacionais.

## 👨‍💻 Desenvolvimento

Para desenvolvimento local:

```bash
python manage.py runserver
```

Acesse `http://localhost:8000` para ver o aplicativo.

## 📚 Recursos Adicionais

- [Documentação Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [retrogames.cc](https://www.retrogames.cc)
- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

