#!/bin/bash
# Script para iniciar o Retro Games Cloud com Nginx

set -e

echo "=========================================="
echo "Retro Games Cloud - Iniciando com Nginx"
echo "=========================================="

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
mkdir -p staticfiles media/game_covers media/user_uploads nginx_logs

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

# Constrói e inicia os containers
echo "🚀 Construindo e iniciando containers..."
docker-compose up -d --build

# Aguarda os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 5

# Verifica o status dos containers
echo ""
echo "📊 Status dos containers:"
docker-compose ps

# Mostra informações úteis
echo ""
echo "=========================================="
echo "✅ Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "🌐 Acesse a aplicação em:"
echo "   - http://localhost"
echo "   - http://localhost/admin (admin/admin123)"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Parar: docker-compose down"
echo "   - Reiniciar: docker-compose restart"
echo ""
echo "📚 Documentação completa: NGINX_SETUP.md"
echo ""

