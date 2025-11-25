@echo off
REM Script para parar o Retro Games Cloud no Windows

echo ==========================================
echo Parando Retro Games Cloud
echo ==========================================
echo.

docker-compose down

echo.
echo [OK] Sistema parado com sucesso!
echo.

pause

