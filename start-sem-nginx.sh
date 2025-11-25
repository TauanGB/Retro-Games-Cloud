#!/bin/bash
# Script para iniciar o Retro Games Cloud SEM Nginx (MODO DEBUG)

echo "=========================================="
echo "Retro Games Cloud - Modo DEBUG (Sem Nginx)"
echo "=========================================="
echo ""

# Verifica se o Docker está instalado e rodando
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verifica se o docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não está instalado. Por favor, instale o docker-compose primeiro."
    exit 1
fi

# Cria diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p staticfiles media/game_covers media/user_uploads

# Verifica se o arquivo env.docker existe
if [ ! -f "env.docker" ]; then
    echo "⚠️  Arquivo env.docker não encontrado. Criando a partir de env.example..."
    if [ -f "env.example" ]; then
        cp env.example env.docker
        echo "✅ Arquivo env.docker criado. Por favor, edite-o com suas configurações."
    else
        echo "❌ Arquivo env.example não encontrado. Por favor, crie o arquivo env.docker manualmente."
        exit 1
    fi
fi

# Para os containers se estiverem rodando
echo "🛑 Parando containers existentes (se houver)..."
docker-compose down 2>/dev/null || true

# Remove qualquer container do nginx que possa estar rodando
echo "🗑️  Removendo containers do nginx (se existirem)..."
docker stop retro_games_nginx 2>/dev/null || true
docker rm retro_games_nginx 2>/dev/null || true

# Constrói e inicia apenas o serviço web (sem nginx)
echo "🚀 Construindo e iniciando containers (sem nginx)..."
docker-compose up -d --build web db

# Aguarda os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verifica o status dos containers
echo ""
echo "📊 Status dos containers:"
docker-compose ps

# Mostra informações úteis
echo ""
echo "=========================================="
echo "✅ Sistema iniciado em modo DEBUG!"
echo "=========================================="
echo ""
echo "🌐 Nginx DESABILITADO - Acesso direto ao Django"
echo "Acesse a aplicação em:"
echo "   - http://localhost:8000"
echo "   - http://localhost:8000/admin (admin/admin123)"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f web"
echo "   - Ver apenas erros: docker-compose logs web | grep -i error"
echo "   - Parar: docker-compose down"
echo "   - Reiniciar: docker-compose restart web"
echo ""
echo "📚 Para ver logs em tempo real:"
echo "   docker-compose logs -f web"
echo ""

