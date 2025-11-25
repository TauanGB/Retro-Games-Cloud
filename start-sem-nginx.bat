@echo off
REM Script para iniciar o Retro Games Cloud SEM Nginx no Windows (MODO DEBUG)

echo ==========================================
echo Retro Games Cloud - Modo DEBUG (Sem Nginx)
echo ==========================================
echo.

REM Verifica se o Docker está instalado
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker nao esta instalado. Por favor, instale o Docker primeiro.
    exit /b 1
)

REM Verifica se o Docker está rodando
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker nao esta rodando. Por favor, inicie o Docker Desktop primeiro.
    exit /b 1
)

REM Verifica se o docker-compose está instalado
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] docker-compose nao esta instalado. Por favor, instale o docker-compose primeiro.
    exit /b 1
)

REM Cria diretórios necessários
echo [INFO] Criando diretorios necessarios...
if not exist "staticfiles" mkdir staticfiles
if not exist "media\game_covers" mkdir media\game_covers
if not exist "media\user_uploads" mkdir media\user_uploads

REM Verifica se o arquivo env.docker existe
if not exist "env.docker" (
    echo [AVISO] Arquivo env.docker nao encontrado. Criando a partir de env.example...
    if exist "env.example" (
        copy env.example env.docker >nul
        echo [OK] Arquivo env.docker criado. Por favor, edite-o com suas configuracoes.
    ) else (
        echo [ERRO] Arquivo env.example nao encontrado. Por favor, crie o arquivo env.docker manualmente.
        exit /b 1
    )
)

REM Para os containers se estiverem rodando
echo [INFO] Parando containers existentes (se houver)...
docker-compose down >nul 2>nul

REM Remove qualquer container do nginx que possa estar rodando
echo [INFO] Removendo containers do nginx (se existirem)...
docker stop retro_games_nginx >nul 2>nul
docker rm retro_games_nginx >nul 2>nul

REM Constrói e inicia apenas o serviço web (sem nginx)
echo [INFO] Construindo e iniciando containers (sem nginx)...
echo [INFO] NGINX COMPLETAMENTE DESABILITADO - Usando docker-compose.yml limpo...
docker-compose up -d --build

REM Aguarda os serviços ficarem prontos
echo [INFO] Aguardando servicos ficarem prontos...
timeout /t 10 /nobreak >nul

REM Verifica o status dos containers
echo.
echo [INFO] Status dos containers:
docker-compose ps

REM Mostra informações úteis
echo.
echo ==========================================
echo [OK] Sistema iniciado em modo DEBUG!
echo ==========================================
echo.
echo [INFO] Nginx DESABILITADO - Acesso direto ao Django
echo [INFO] Acesse a aplicacao em:
echo    - http://localhost:8000
echo    - http://localhost:8000/admin (admin/admin123)
echo.
echo [INFO] Comandos uteis:
echo    - Ver logs: docker-compose logs -f web
echo    - Ver logs apenas erros: docker-compose logs web ^| findstr /i "error"
echo    - Parar: docker-compose down
echo    - Reiniciar: docker-compose restart web
echo.
echo [INFO] Para ver logs em tempo real:
echo    docker-compose logs -f web
echo.

pause

