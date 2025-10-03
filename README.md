# Retro Games Cloud

Uma plataforma web para jogar jogos retrô clássicos diretamente no navegador.

## 🎮 Características

- Biblioteca de jogos retrô organizados por console
- Emulador web integrado
- Sistema de autenticação de usuários
- Interface moderna e responsiva
- Suporte para GBA, SNES, Mega Drive e outros consoles

## 🚀 Tecnologias Utilizadas

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite (desenvolvimento)
- **Processamento de Imagens**: Pillow

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/retro-games-cloud.git
   cd retro-games-cloud
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Execute o servidor de desenvolvimento**
   ```bash
   python manage.py runserver
   ```

8. **Acesse a aplicação**
   - Abra seu navegador e vá para `http://127.0.0.1:8000`

## 📁 Estrutura do Projeto

```
retro-games-cloud/
├── games/                    # App principal
│   ├── templates/games/      # Templates HTML
│   ├── static/games/         # Arquivos estáticos
│   │   ├── css/             # Estilos CSS
│   │   ├── js/              # Scripts JavaScript
│   │   └── images/          # Imagens
│   ├── models.py            # Modelos de dados
│   ├── views.py             # Views da aplicação
│   └── urls.py              # URLs da aplicação
├── retro_games_cloud/       # Configurações do projeto
│   ├── settings.py          # Configurações Django
│   └── urls.py              # URLs principais
├── media/                   # Arquivos de mídia
│   ├── game_covers/         # Capas dos jogos
│   └── user_uploads/        # Uploads dos usuários
├── static/                  # Arquivos estáticos
├── requirements.txt         # Dependências Python
└── manage.py               # Script de gerenciamento Django
```

## 🎯 Funcionalidades

### Autenticação
- Login e registro de usuários
- Validação de senhas seguras
- Recuperação de senha

### Biblioteca de Jogos
- Visualização de jogos por console
- Filtros por categoria
- Detalhes dos jogos
- Sistema de busca

### Emulador
- Jogos retrô executáveis no navegador
- Controles de teclado
- Interface de emulador integrada

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `env.example`:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configurações de Produção

Para produção, configure:

- `DEBUG=False`
- `ALLOWED_HOSTS` com seu domínio
- Configurações de banco de dados adequadas
- Configurações de segurança SSL

## 📝 Uso

1. **Registre-se** na plataforma
2. **Faça login** com suas credenciais
3. **Navegue** pela biblioteca de jogos
4. **Filtre** por console desejado
5. **Clique** em um jogo para ver detalhes
6. **Jogue** diretamente no navegador

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🐛 Problemas Conhecidos

- Alguns jogos podem ter problemas de performance em dispositivos móveis
- Controles de teclado podem não funcionar em todos os navegadores

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique se seguiu todos os passos de instalação
2. Consulte a documentação do Django
3. Abra uma issue no GitHub

## 🔮 Roadmap

- [ ] Suporte para mais consoles
- [ ] Sistema de favoritos
- [ ] Modo multiplayer
- [ ] App mobile
- [ ] Sistema de conquistas
- [ ] Chat em tempo real

---

Desenvolvido com ❤️ para a comunidade de jogos retrô.