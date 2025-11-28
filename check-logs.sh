#!/bin/bash
# Script para verificar logs e status do sistema

echo "=========================================="
echo "Verificando Status e Logs do Sistema"
echo "=========================================="
echo ""

echo "📊 Status dos Containers:"
docker-compose ps
echo ""

echo "📝 Últimas 50 linhas dos logs do Django (web):"
echo "----------------------------------------"
docker-compose logs --tail=50 web
echo ""

echo "🔍 Verificando erros nos logs:"
echo "----------------------------------------"
docker-compose logs web | grep -i error | tail -20
echo ""

echo "💡 Para ver logs em tempo real, execute:"
echo "   docker-compose logs -f web"
echo ""






