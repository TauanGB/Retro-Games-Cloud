#!/bin/bash
# Script para verificar se tudo está funcionando

echo "=========================================="
echo "Verificando Configuração do Nginx"
echo "=========================================="
echo ""

echo "1. Verificando containers..."
docker-compose ps
echo ""

echo "2. Verificando logs do Django (web)..."
docker-compose logs --tail=20 web
echo ""

echo "3. Verificando logs do Nginx..."
docker-compose logs --tail=20 nginx
echo ""

echo "4. Testando conectividade interna..."
docker-compose exec nginx wget -O- http://web:8000/ 2>&1 | head -20
echo ""

echo "5. Verificando configuração do Nginx..."
docker-compose exec nginx nginx -t
echo ""

echo "6. Testando endpoint de health..."
curl -v http://localhost/health/ 2>&1
echo ""

