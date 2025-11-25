#!/bin/bash
# Script para parar o Retro Games Cloud

echo "=========================================="
echo "Parando Retro Games Cloud"
echo "=========================================="

docker-compose down

echo ""
echo "✅ Sistema parado com sucesso!"
echo ""

