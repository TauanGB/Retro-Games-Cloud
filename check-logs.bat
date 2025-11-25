@echo off
REM Script para verificar logs e status do sistema no Windows

echo ==========================================
echo Verificando Status e Logs do Sistema
echo ==========================================
echo.

echo [INFO] Status dos Containers:
docker-compose ps
echo.

echo [INFO] Ultimas 50 linhas dos logs do Django (web):
echo ----------------------------------------
docker-compose logs --tail=50 web
echo.

echo [INFO] Verificando erros nos logs:
echo ----------------------------------------
docker-compose logs web | findstr /i "error"
echo.

echo [INFO] Para ver logs em tempo real, execute:
echo    docker-compose logs -f web
echo.

pause

