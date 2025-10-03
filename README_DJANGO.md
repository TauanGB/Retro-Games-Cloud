# Retro Games Cloud - MVP Django

Um MVP funcional de uma plataforma de jogos retro em nuvem, desenvolvido em Django monolítico com Django ORM/SQL nativo e templates com Bootstrap.

## 🎮 Funcionalidades

### ✅ Implementadas

- **Catálogo Público**: Visualização de jogos e planos sem necessidade de login
- **Sistema de Autenticação**: Login e registro de usuários
- **Checkout Simulado**: Processo de compra com pagamento simulado
- **Biblioteca do Usuário**: Visualização de jogos comprados e de planos ativos
- **Gestão de Assinaturas**: Cancelamento mantendo acesso até o término do período
- **Entitlements Idempotentes**: Sistema que evita duplicação de direitos de acesso
- **Django Admin**: Interface administrativa completa

### 🎯 Características Técnicas

- **Django 4.2.7** com SQLite (padrão para agilizar desenvolvimento)
- **Bootstrap 5.3.0** para interface responsiva
- **Templates Django** reutilizando designs existentes
- **Views/URLs simples**: GET para listas/detalhes, POST para ações
- **Pagamento simulado** com botões "Aprovar"/"Falhar"
- **Sistema idempotente** para criação de entitlements

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar Migrações

```bash
python manage.py migrate
```

### 3. Criar Dados de Exemplo

```bash
python populate_data.py
```

### 4. Iniciar Servidor

```bash
python manage.py runserver
```

### 5. Acessar a Aplicação

- **Site Principal**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
  - Usuário: `admin`
  - Senha: `admin123`

## 📱 Páginas Disponíveis

### Públicas (sem login)
- `/` - Catálogo de jogos e planos
- `/game/<id>/` - Detalhes de um jogo
- `/plan/<id>/` - Detalhes de um plano
- `/login/` - Página de login
- `/register/` - Página de registro

### Autenticadas (com login)
- `/library/` - Biblioteca do usuário
- `/checkout/game/<id>/` - Checkout de jogo
- `/checkout/plan/<id>/` - Checkout de plano
- `/payment/<session_id>/` - Sessão de pagamento simulado

## 🎮 Fluxo de Uso

### 1. Navegação Pública
- Usuário acessa o catálogo
- Visualiza jogos e planos disponíveis
- Filtra por console (GBA, SNES, Mega Drive)

### 2. Autenticação
- Usuário se registra ou faz login
- Redirecionamento automático para o catálogo

### 3. Compra de Jogo
- Usuário clica em "Comprar Agora" em um jogo
- Redirecionado para checkout
- Criação de sessão de pagamento
- Página de pagamento simulado com botões "Aprovar"/"Falhar"

### 4. Assinatura de Plano
- Usuário clica em "Assinar Agora" em um plano
- Mesmo fluxo de checkout
- Criação de entitlements para todos os jogos do plano
- Período de 30 dias configurado automaticamente

### 5. Biblioteca
- Visualização de jogos comprados individualmente
- Visualização de jogos de planos ativos
- Informações de assinaturas ativas
- Opção de cancelar assinatura

## 🗄️ Modelos de Dados

### Game
- Jogos individuais com preço, console, descrição
- Status ativo/inativo

### Plan
- Planos de assinatura mensal
- Relacionamento many-to-many com jogos
- Preço mensal

### Purchase
- Compras de jogos individuais
- Status: pendente, concluída, falhou, cancelada
- ID de pagamento único

### Subscription
- Assinaturas de planos
- Período atual (início e fim)
- Status: ativa, cancelada, expirada
- Cancelamento mantém acesso até o fim do período

### Entitlement
- Direitos de acesso do usuário
- Tipo: compra ou assinatura
- Sistema idempotente (evita duplicação)

### PaymentSession
- Sessões de pagamento simulado
- Status: pendente, aprovado, falhou
- Vinculado a jogo ou plano

## 🔧 Funcionalidades Técnicas

### Idempotência
- Sistema evita criação de entitlements duplicados
- Verificação de existência antes da criação
- Uso de `get_or_create()` para garantir unicidade

### Pagamento Simulado
- Botões "Aprovar" e "Falhar" na interface
- Processamento idempotente de pagamentos
- Criação automática de entitlements em caso de sucesso

### Gestão de Assinaturas
- Cancelamento mantém acesso até `current_period_end`
- Verificação de status ativo considerando data de expiração
- Extensão automática de período (30 dias)

### Biblioteca Inteligente
- Separação entre jogos comprados e de planos
- Verificação de validade de entitlements
- Informações de expiração de assinaturas

## 🎨 Design

### Reutilização de Assets
- CSS existente (`styles.css`, `site.css`) integrado
- JavaScript existente (`script.js`, `signup.js`) mantido
- Templates Django com Bootstrap para responsividade

### Interface
- Design retro com cores neon
- Animações CSS para hover em imagens de jogos
- Layout responsivo com Bootstrap
- Navegação intuitiva

## 📊 Dados de Exemplo

### Jogos Criados
- Pokémon Emerald (GBA) - R$ 29,90
- Zelda: A Link to the Past (SNES) - R$ 39,90
- Sonic the Hedgehog 2 (Mega Drive) - R$ 24,90
- Metroid Fusion (GBA) - R$ 34,90
- Super Mario World (SNES) - R$ 44,90
- Streets of Rage 2 (Mega Drive) - R$ 19,90

### Planos Criados
- **Plano Básico** - R$ 19,90/mês
  - Inclui jogos GBA e Mega Drive
- **Plano Premium** - R$ 39,90/mês
  - Inclui todos os jogos da plataforma

## 🔐 Segurança

- Autenticação Django padrão
- Proteção CSRF em formulários
- Validação de permissões em views
- Verificação de propriedade em operações sensíveis

## 🚀 Próximos Passos

Para evoluir o MVP:

1. **Integração com Gateway de Pagamento Real**
2. **Sistema de Emulador Web** (JavaScript)
3. **Upload de ROMs** via Django Admin
4. **Sistema de Avaliações** e comentários
5. **Notificações por Email** para assinaturas
6. **API REST** para integração mobile
7. **Sistema de Recomendações** baseado em histórico

## 📝 Notas de Desenvolvimento

- Projeto desenvolvido como MVP funcional
- Foco em simplicidade e funcionalidade core
- Código limpo e bem documentado
- Estrutura escalável para futuras expansões
- Testes manuais realizados em todas as funcionalidades

---

**Desenvolvido com Django 4.2.7 + Bootstrap 5.3.0**


