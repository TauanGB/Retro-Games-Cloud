import json
import requests
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from decouple import config

from .models import Game, GameRequest
from .forms import GameRequestForm, AdminGameRequestForm
from .utils import search_games_on_retrogames, search_multiple_games
import logging

logger = logging.getLogger(__name__)


def home(request):
    """
    Página inicial do TDE - PWA educacional de jogos retro.
    Apresenta o contexto do trabalho e destaca alguns jogos.
    """
    # Jogos em destaque (primeiros 6 jogos ativos)
    featured_games = Game.objects.filter(is_active=True)[:6]
    
    # Todos os jogos ativos para estatísticas
    all_games = Game.objects.filter(is_active=True)
    
    context = {
        'featured_games': featured_games,
        'total_games': all_games.count(),
    }
    
    return render(request, 'games/home.html', context)


def catalog(request):
    """
    Página de catálogo completo de jogos retro.
    Lista simples de todos os jogos ativos.
    """
    games = Game.objects.filter(is_active=True).order_by('title')
    
    context = {
        'games': games,
    }
    
    return render(request, 'games/catalog.html', context)


def game_detail(request, slug):
    """
    Página de detalhes do jogo com iframe do emulador.
    O jogo é acessível publicamente, sem necessidade de autenticação.
    """
    game = get_object_or_404(Game, slug=slug, is_active=True)
    
    # Jogos relacionados (outros jogos ativos, limitado a 4)
    related_games = Game.objects.filter(
        is_active=True
    ).exclude(id=game.id)[:4]
    
    context = {
        'game': game,
        'related_games': related_games,
    }
    
    return render(request, 'games/game_detail.html', context)


# ============================================================================
# AUTENTICAÇÃO (OPCIONAL - mantida para demonstração/futuros recursos)
# ============================================================================

def user_login(request):
    """Página de login (opcional para o TDE)"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'games/login.html')


def user_logout(request):
    """Logout do usuário"""
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('home')


def register(request):
    """Página de registro (opcional para o TDE)"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'games/register.html', {'form': form})


# ============================================================================
# API ENDPOINTS (simplificados)
# ============================================================================

@require_http_methods(["GET"])
def api_get_game_info(request, slug):
    """
    API para obter informações de um jogo específico.
    Endpoint: GET /api/game/<slug>/
    """
    try:
        game = get_object_or_404(Game, slug=slug, is_active=True)
        
        return JsonResponse({
            'id': game.id,
            'title': game.title,
            'slug': game.slug,
            'description': game.description,
            'cover_image': game.cover_image,
            'rom_url': game.rom_url,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Jogo não encontrado'
        }, status=404)


# ============================================================================
# SOLICITAÇÃO DE JOGOS (para usuários autenticados)
# ============================================================================

@login_required
def request_game(request):
    """
    View protegida por login para usuários solicitarem a inclusão de um novo jogo.
    Apenas usuários autenticados podem acessar esta página.
    """
    if request.method == 'POST':
        form = GameRequestForm(request.POST)
        if form.is_valid():
            game_request = form.save(commit=False)
            game_request.user = request.user
            game_request.status = 'pending'
            game_request.save()
            
            messages.success(
                request,
                'Seu pedido foi enviado com sucesso! O administrador irá analisar sua solicitação em breve.'
            )
            return redirect('my_game_requests')
    else:
        form = GameRequestForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'games/request_game.html', context)


@login_required
def my_game_requests(request):
    """
    View protegida por login para usuários visualizarem seus pedidos anteriores.
    Apenas usuários autenticados podem acessar esta página e veem apenas seus próprios pedidos.
    """
    game_requests = GameRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'game_requests': game_requests,
        'total_requests': game_requests.count(),
        'pending_count': game_requests.filter(status='pending').count(),
        'approved_count': game_requests.filter(status='approved').count(),
        'rejected_count': game_requests.filter(status='rejected').count(),
    }
    
    return render(request, 'games/my_game_requests.html', context)


# ============================================================================
# ADMINISTRAÇÃO DE REQUISIÇÕES (apenas para staff)
# ============================================================================

def staff_required(user):
    """Verifica se o usuário é staff"""
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_required, login_url='home')
def admin_game_requests_list(request):
    """
    View para administradores visualizarem todas as requisições de jogos.
    Apenas usuários staff podem acessar esta página.
    Esta página permite ao administrador ver os pedidos e preparar as consultas para IA.
    """
    # Filtro por status (opcional via query parameter)
    status_filter = request.GET.get('status', '')
    ready_filter = request.GET.get('ready_for_ai', '')
    
    # Query base
    game_requests = GameRequest.objects.all().select_related('user')
    
    # Aplicar filtros
    if status_filter:
        game_requests = game_requests.filter(status=status_filter)
    
    if ready_filter == 'true':
        game_requests = game_requests.filter(ready_for_ai=True)
    elif ready_filter == 'false':
        game_requests = game_requests.filter(ready_for_ai=False)
    
    # Ordenação padrão: mais recentes primeiro
    game_requests = game_requests.order_by('-created_at')
    
    # Estatísticas
    total = GameRequest.objects.count()
    pending = GameRequest.objects.filter(status='pending').count()
    approved = GameRequest.objects.filter(status='approved').count()
    rejected = GameRequest.objects.filter(status='rejected').count()
    ready_for_ai_count = GameRequest.objects.filter(ready_for_ai=True).count()
    
    context = {
        'game_requests': game_requests,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'ready_for_ai_count': ready_for_ai_count,
        'current_status_filter': status_filter,
        'current_ready_filter': ready_filter,
    }
    
    return render(request, 'games/admin_game_requests_list.html', context)


@user_passes_test(staff_required, login_url='home')
def admin_game_request_detail(request, pk):
    """
    View para administradores visualizarem e editarem uma requisição específica.
    Apenas usuários staff podem acessar esta página.
    Permite editar a consulta para IA e marcar como pronta para processamento.
    """
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    # Se ai_query estiver vazio, preencher com sugestão padrão
    if not game_request.ai_query:
        game_request.ai_query = f"{game_request.title} jogo retro"
        game_request.save(update_fields=['ai_query'])
    
    if request.method == 'POST':
        form = AdminGameRequestForm(request.POST, instance=game_request)
        if form.is_valid():
            # Salvar o texto da consulta
            form.save()
            
            # Se for requisição AJAX, enviar direto para a API
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Atualizar o objeto do banco antes de chamar approve
                game_request.refresh_from_db()
                # Chamar a função de aprovação diretamente (ela já retorna JSON para AJAX)
                try:
                    return admin_approve_request(request, pk)
                except Exception as e:
                    import traceback
                    print(f"Erro ao chamar admin_approve_request: {traceback.format_exc()}")
                    return JsonResponse({
                        'error': f'Erro ao enviar para API: {str(e)}'
                    }, status=500)
            
            # Se não for AJAX, apenas salvar e redirecionar
            messages.success(request, 'Texto para busca na IA atualizado! Clique em "Aprovar e Buscar na API" para enviar.')
            return redirect('admin_game_request_detail', pk=game_request.pk)
    else:
        form = AdminGameRequestForm(instance=game_request)
    
    # Preparar dados para exibição (JSON de exemplo)
    ai_data_example = {
        "ai_query": game_request.ai_query,
        "title": game_request.title,
        "description": game_request.details or "",
    }
    
    ai_data_json = json.dumps(ai_data_example, indent=2, ensure_ascii=False)
    
    # Formatar ai_response_data para exibição se existir
    ai_response_json = None
    if game_request.ai_response_data:
        ai_response_json = json.dumps(game_request.ai_response_data, indent=2, ensure_ascii=False)
    
    context = {
        'game_request': game_request,
        'form': form,
        'ai_data_json': ai_data_json,
        'ai_response_json': ai_response_json,
    }
    
    return render(request, 'games/admin_game_request_detail.html', context)


# ============================================================================
# AÇÕES DE ADMINISTRAÇÃO (Aprovar/Rejeitar e Integração com API)
# ============================================================================

# URL base da API externa
API_BASE_URL = "https://simple-game-name-collector-v1-ca4edf88-5b8a-ef2ee057.crewai.com"

# Token de autenticação da API (lido do .env)
API_TOKEN = config('GAME_COLLECTOR_API_TOKEN', default='')

# Função helper para obter headers de autenticação
def get_api_headers():
    """Retorna os headers necessários para autenticação na API"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Adicionar token de autenticação se disponível
    if API_TOKEN:
        # Tentar diferentes formatos de autenticação comuns
        if API_TOKEN.startswith('Bearer ') or API_TOKEN.startswith('Token '):
            headers['Authorization'] = API_TOKEN
        else:
            # Se não tiver prefixo, adicionar Bearer
            headers['Authorization'] = f'Bearer {API_TOKEN}'
        # Também tentar como X-API-Key (algumas APIs usam isso)
        headers['X-API-Key'] = API_TOKEN
        # Algumas APIs também usam X-Auth-Token
        headers['X-Auth-Token'] = API_TOKEN
    else:
        print("AVISO: GAME_COLLECTOR_API_TOKEN não configurado no .env!")
    
    return headers


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["POST"])
def admin_approve_request(request, pk):
    """
    Aprova uma requisição de jogo e inicia o processo de busca na API externa.
    Suporta requisições AJAX e requisições normais.
    """
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    if game_request.status == 'approved':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Esta requisição já foi aprovada.'
            }, status=400)
        messages.warning(request, 'Esta requisição já foi aprovada.')
        return redirect('admin_game_request_detail', pk=pk)
    
    try:
        # Garantir que temos um título válido
        if not game_request.title or not game_request.title.strip():
            error_msg = 'O título do jogo é obrigatório e não pode estar vazio.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('admin_game_request_detail', pk=pk)
        
        # Garantir que ai_query existe e não está vazio
        if not game_request.ai_query or not game_request.ai_query.strip():
            game_request.ai_query = f"{game_request.title.strip()} jogo retro"
            game_request.save(update_fields=['ai_query'])
        
        # Preparar dados para kickoff (enviar direto, sem chamar /inputs)
        # Garantir que query_text sempre tenha um valor válido e não vazio
        title_stripped = game_request.title.strip() if game_request.title else ""
        
        # Construir query_text com fallbacks
        if game_request.ai_query and game_request.ai_query.strip():
            query_text = game_request.ai_query.strip()
        elif title_stripped:
            query_text = f"{title_stripped} jogo retro"
        else:
            query_text = "jogo retro"  # Fallback final
        
        # Garantir que query_text é uma string válida e não vazia
        query_text = str(query_text).strip()
        if not query_text:
            query_text = "jogo retro"
        
        # A API espera apenas o search_term - garantir que seja uma string não vazia
        search_term_value = str(query_text).strip()
        if not search_term_value:
            error_msg = 'Não foi possível gerar um termo de busca válido. Por favor, verifique o título e a consulta para IA.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('admin_game_request_detail', pk=pk)
        
        # A API espera a estrutura com "inputs" contendo "search_term"
        kickoff_payload = {
            "inputs": {
                "search_term": search_term_value
            },
            "taskWebhookUrl": "",
            "stepWebhookUrl": "",
            "crewWebhookUrl": "",
            "trainingFilename": "",
            "generateArtifact": False
        }
        
        # Validação final: garantir que search_term existe e não está vazio dentro de inputs
        if "inputs" not in kickoff_payload or "search_term" not in kickoff_payload["inputs"]:
            error_msg = 'Erro: estrutura do payload inválida!'
            print(f"ERRO CRÍTICO: {error_msg}")
            print(f"Payload: {kickoff_payload}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('admin_game_request_detail', pk=pk)
        
        if not kickoff_payload["inputs"]["search_term"] or not str(kickoff_payload["inputs"]["search_term"]).strip():
            error_msg = 'Erro: search_term não pode estar vazio!'
            print(f"ERRO CRÍTICO: {error_msg}")
            print(f"Payload: {kickoff_payload}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('admin_game_request_detail', pk=pk)
        
        # Debug: Print do payload que será enviado
        print("=" * 80)
        print("DEBUG - Enviando requisição para API")
        print("=" * 80)
        print(f"URL: {API_BASE_URL}/kickoff")
        print(f"search_term (tipo: {type(kickoff_payload['inputs']['search_term'])}, valor: '{kickoff_payload['inputs']['search_term']}', tamanho: {len(str(kickoff_payload['inputs']['search_term']))})")
        print(f"Payload JSON completo:")
        print(json.dumps(kickoff_payload, indent=2, ensure_ascii=False))
        print("-" * 80)
        
        # Enviar direto para /kickoff com autenticação
        kickoff_url = f"{API_BASE_URL}/kickoff"
        api_headers = get_api_headers()
        
        # Debug: Print dos headers de autenticação (sem mostrar o token completo por segurança)
        if API_TOKEN:
            token_preview = API_TOKEN[:10] + "..." if len(API_TOKEN) > 10 else API_TOKEN
            print(f"Token configurado: {token_preview} (tamanho: {len(API_TOKEN)} caracteres)")
        else:
            print("AVISO: Nenhum token configurado! Adicione GAME_COLLECTOR_API_TOKEN no arquivo .env")
        print(f"Headers de autenticação que serão enviados:")
        for key, value in api_headers.items():
            if 'token' in key.lower() or 'auth' in key.lower() or 'key' in key.lower():
                # Mascarar tokens nos logs
                if value and len(value) > 10:
                    masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else value[:10] + "..."
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        print("-" * 80)
        
        # Serializar o JSON manualmente para debug
        json_body = json.dumps(kickoff_payload, ensure_ascii=False)
        print(f"Body JSON que será enviado (tamanho: {len(json_body)} bytes):")
        print(json_body)
        print("-" * 80)
        
        kickoff_response = requests.post(
            kickoff_url,
            json=kickoff_payload,
            headers=api_headers,
            timeout=30
        )
        
        # Debug: Print da resposta
        print(f"Status Code: {kickoff_response.status_code}")
        print(f"Response Headers:")
        for key, value in kickoff_response.headers.items():
            print(f"  {key}: {value}")
        print(f"Response Text (primeiros 1000 caracteres):")
        print(kickoff_response.text[:1000])
        print("=" * 80)
        
        # Verificar se houve erro antes de fazer raise_for_status
        if not kickoff_response.ok:
            print(f"ERRO: Status {kickoff_response.status_code}")
            try:
                error_json = kickoff_response.json()
                print(f"Erro JSON:")
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except:
                print(f"Erro como texto: {kickoff_response.text}")
        
        kickoff_response.raise_for_status()
        kickoff_data = kickoff_response.json()
        
        # Debug: Print dos dados retornados
        print("Dados retornados pela API:")
        print(json.dumps(kickoff_data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # 4. Salvar kickoff_id e atualizar status
        game_request.kickoff_id = kickoff_data.get('kickoff_id') or kickoff_data.get('id')
        game_request.status = 'approved'
        game_request.execution_status = 'running'
        game_request.save()
        
        # Se for requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Requisição aprovada! Busca iniciada na API. ID: {game_request.kickoff_id}',
                'kickoff_id': game_request.kickoff_id,
                'status': 'running'
            })
        
        messages.success(
            request,
            f'Requisição aprovada! Busca iniciada na API. ID: {game_request.kickoff_id}'
        )
        
    except requests.exceptions.HTTPError as e:
        # Debug detalhado para erros HTTP
        print("=" * 80)
        print("ERRO HTTP ao comunicar com a API")
        print("=" * 80)
        print(f"Status Code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
        if hasattr(e, 'response'):
            print(f"Response Headers:")
            for key, value in e.response.headers.items():
                print(f"  {key}: {value}")
            print(f"Response Text:")
            print(e.response.text)
            try:
                error_json = e.response.json()
                print(f"Erro JSON:")
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except:
                pass
        print("=" * 80)
        
        error_msg = f'Erro HTTP {e.response.status_code if hasattr(e, "response") else "desconhecido"} ao comunicar com a API: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': error_msg,
                'status_code': e.response.status_code if hasattr(e, 'response') else None,
                'response_text': e.response.text[:500] if hasattr(e, 'response') else str(e)
            }, status=500)
        messages.error(request, error_msg)
    except requests.exceptions.Timeout:
        print("=" * 80)
        print("ERRO: Timeout ao comunicar com a API")
        print("=" * 80)
        error_msg = 'Timeout ao comunicar com a API. Tente novamente.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': error_msg
            }, status=500)
        messages.error(request, error_msg)
    except requests.exceptions.RequestException as e:
        print("=" * 80)
        print("ERRO ao comunicar com a API")
        print("=" * 80)
        print(f"Tipo de exceção: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text[:500]}")
        print("=" * 80)
        error_msg = f'Erro ao comunicar com a API: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': error_msg
            }, status=500)
        messages.error(request, error_msg)
    except Exception as e:
        import traceback
        error_msg = f'Erro inesperado: {str(e)}'
        # Log do erro completo para debug
        print(f"Erro ao aprovar requisição: {traceback.format_exc()}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': error_msg
            }, status=500)
        messages.error(request, error_msg)
    
    # Se chegou aqui e não retornou JSON, redirecionar
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('admin_game_request_detail', pk=pk)
    else:
        # Fallback para AJAX - retornar erro genérico
        return JsonResponse({
            'error': 'Erro ao processar requisição'
        }, status=500)


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["POST"])
def admin_reject_request(request, pk):
    """
    Rejeita uma requisição de jogo.
    """
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    if game_request.status == 'rejected':
        messages.warning(request, 'Esta requisição já foi rejeitada.')
        return redirect('admin_game_request_detail', pk=pk)
    
    game_request.status = 'rejected'
    game_request.save()
    
    messages.success(request, 'Requisição rejeitada com sucesso.')
    return redirect('admin_game_request_detail', pk=pk)


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["GET"])
def admin_check_api_status(request, pk):
    """
    View AJAX para verificar o status da execução na API externa.
    """
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    if not game_request.kickoff_id:
        return JsonResponse({
            'error': 'Nenhum kickoff_id encontrado para esta requisição.'
        }, status=400)
    
    try:
        status_url = f"{API_BASE_URL}/status/{game_request.kickoff_id}"
        
        # Debug: Print da URL de status
        print("=" * 80)
        print("DEBUG - Verificando status da API")
        print("=" * 80)
        print(f"URL: {status_url}")
        print(f"Kickoff ID: {game_request.kickoff_id}")
        print("-" * 80)
        
        # Obter headers de autenticação
        api_headers = get_api_headers()
        
        status_response = requests.get(status_url, headers=api_headers, timeout=10)
        
        # Debug: Print da resposta de status
        print(f"Status Code: {status_response.status_code}")
        print(f"Response Headers:")
        for key, value in status_response.headers.items():
            print(f"  {key}: {value}")
        print(f"Response Text (primeiros 1000 caracteres):")
        print(status_response.text[:1000])
        
        if not status_response.ok:
            print(f"ERRO: Status {status_response.status_code}")
            try:
                error_json = status_response.json()
                print(f"Erro JSON:")
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except:
                print(f"Erro como texto: {status_response.text}")
        
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Debug: Print dos dados de status
        print("Dados de status recebidos:")
        print(json.dumps(status_data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # Atualizar status da execução
        # A API retorna 'state' (SUCCESS, RUNNING, etc.) em vez de 'status'
        execution_state = status_data.get('state', status_data.get('status', 'unknown'))
        
        # Normalizar o estado para salvar no banco
        if execution_state == 'SUCCESS':
            game_request.execution_status = 'completed'
        elif execution_state == 'RUNNING' or execution_state == 'PENDING':
            game_request.execution_status = 'running'
        elif execution_state == 'ERROR' or execution_state == 'FAILED':
            game_request.execution_status = 'failed'
        else:
            game_request.execution_status = execution_state.lower() if isinstance(execution_state, str) else str(execution_state)
        
        # Se concluído, salvar os dados retornados e buscar jogos no retrogames.cc
        if execution_state == 'SUCCESS':
            # Salvar toda a resposta da API
            game_request.ai_response_data = status_data
            
            # Processar o resultado que vem como string com nomes separados por \n
            retrogames_results = []
            game_names = []
            
            # Extrair nomes de jogos do campo 'result'
            if 'result' in status_data and status_data['result']:
                result_text = str(status_data['result']).strip()
                
                # Dividir por quebras de linha e limpar cada nome
                if result_text:
                    game_names = [
                        name.strip() 
                        for name in result_text.split('\n') 
                        if name.strip()  # Remover linhas vazias
                    ]
                    
                    # Remover duplicatas mantendo a ordem
                    seen = set()
                    game_names = [
                        name for name in game_names 
                        if name and (name.lower() not in seen or seen.add(name.lower()))
                    ]
            
            # Se também há resultado em last_executed_task/output
            if not game_names and 'last_executed_task' in status_data:
                task_output = status_data['last_executed_task'].get('output', '')
                if task_output:
                    result_text = str(task_output).strip()
                    if result_text:
                        game_names = [
                            name.strip() 
                            for name in result_text.split('\n') 
                            if name.strip()
                        ]
                        # Remover duplicatas
                        seen = set()
                        game_names = [
                            name for name in game_names 
                            if name and (name.lower() not in seen or seen.add(name.lower()))
                        ]
            
            # Se não encontrou nomes, usar o título da requisição
            if not game_names:
                game_names = [game_request.title]
            
            # Buscar jogos no retrogames.cc
            try:
                print(f"Buscando jogos no retrogames.cc para: {game_names}")
                retrogames_results = search_multiple_games(game_names, max_results_per_game=5)
                
                # Adicionar resultados ao ai_response_data
                if isinstance(game_request.ai_response_data, dict):
                    game_request.ai_response_data['game_names'] = game_names
                    game_request.ai_response_data['retrogames_results'] = retrogames_results
                else:
                    # Se não for dict, converter
                    game_request.ai_response_data = {
                        'ai_data': game_request.ai_response_data,
                        'game_names': game_names,
                        'retrogames_results': retrogames_results
                    }
                print(f"Encontrados {len(retrogames_results)} jogos no retrogames.cc")
            except Exception as e:
                print(f"Erro ao buscar jogos no retrogames.cc: {str(e)}")
                import traceback
                traceback.print_exc()
        
        game_request.save()
        
        # Preparar dados de resposta
        response_data = {
            'status': game_request.execution_status,
            'state': execution_state,  # Estado original da API (SUCCESS, RUNNING, etc.)
            'data': game_request.ai_response_data,
            'kickoff_id': game_request.kickoff_id
        }
        
        # Incluir nomes de jogos extraídos e resultados do retrogames.cc se disponíveis
        if game_request.ai_response_data and isinstance(game_request.ai_response_data, dict):
            if 'game_names' in game_request.ai_response_data:
                response_data['game_names'] = game_request.ai_response_data['game_names']
            if 'retrogames_results' in game_request.ai_response_data:
                response_data['retrogames_results'] = game_request.ai_response_data['retrogames_results']
        
        return JsonResponse(response_data)
        
    except requests.exceptions.HTTPError as e:
        print("=" * 80)
        print("ERRO HTTP ao verificar status")
        print("=" * 80)
        if hasattr(e, 'response'):
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Headers:")
            for key, value in e.response.headers.items():
                print(f"  {key}: {value}")
            print(f"Response Text:")
            print(e.response.text)
            try:
                error_json = e.response.json()
                print(f"Erro JSON:")
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except:
                pass
        print("=" * 80)
        return JsonResponse({
            'error': f'Erro HTTP {e.response.status_code if hasattr(e, "response") else "desconhecido"} ao verificar status: {e.response.text[:200] if hasattr(e, "response") else str(e)}',
            'status_code': e.response.status_code if hasattr(e, 'response') else None
        }, status=500)
    except requests.exceptions.RequestException as e:
        print("=" * 80)
        print("ERRO ao verificar status")
        print("=" * 80)
        print(f"Tipo de exceção: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text[:500]}")
        print("=" * 80)
        return JsonResponse({
            'error': f'Erro ao verificar status: {str(e)}'
        }, status=500)
    except Exception as e:
        import traceback
        print("=" * 80)
        print("ERRO INESPERADO ao verificar status")
        print("=" * 80)
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"Traceback:")
        print(traceback.format_exc())
        print("=" * 80)
        return JsonResponse({
            'error': f'Erro inesperado: {str(e)}'
        }, status=500)


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["GET", "POST"])
def admin_search_retrogames(request, pk):
    """
    View para buscar jogos no retrogames.cc manualmente ou via AJAX.
    Aceita POST ou GET com parâmetro 'query' para buscar um jogo específico.
    """
    import traceback
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    # Obter query da requisição (POST, GET ou usar valores padrão)
    query = request.POST.get('query') or request.GET.get('query')
    
    if not query:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Parâmetro "query" é obrigatório'
            }, status=400)
        messages.error(request, 'Parâmetro de busca não fornecido.')
        return redirect('admin_game_request_detail', pk=pk)
    
    try:
        results = search_games_on_retrogames(query, max_results=5)
        
        # Salvar resultados no banco de dados (tanto para AJAX quanto para requisições normais)
        if not game_request.ai_response_data:
            game_request.ai_response_data = {}
        if not isinstance(game_request.ai_response_data, dict):
            game_request.ai_response_data = {'ai_data': game_request.ai_response_data}
        
        game_request.ai_response_data['retrogames_results'] = results
        game_request.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'results': results,
                'count': len(results),
                'query': query
            })
        
        # Se não for AJAX, redirecionar
        messages.success(request, f'Encontrados {len(results)} jogos no retrogames.cc')
        return redirect('admin_game_request_detail', pk=pk)
        
    except Exception as e:
        error_msg = f'Erro ao buscar jogos: {str(e)}'
        print(f"Erro ao buscar jogos: {traceback.format_exc()}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': error_msg
            }, status=500)
        
        messages.error(request, error_msg)
        return redirect('admin_game_request_detail', pk=pk)


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["GET"])
def admin_extract_embed_link(request, pk):
    """
    View para extrair o link do embed de uma página do retrogames.cc.
    Busca o textarea readonly na página embed e extrai a URL do jogo.
    """
    from .utils import _extract_embed_url
    
    # Garantir que sempre retorna JSON
    embed_url = request.GET.get('embed_url')
    if not embed_url:
        return JsonResponse({
            'error': 'Parâmetro "embed_url" é obrigatório',
            'success': False
        }, status=400, content_type='application/json')
    
    try:
        logger.info(f"DEBUG - View admin_extract_embed_link chamada com embed_url: {embed_url}")
        print(f"DEBUG - View admin_extract_embed_link chamada com embed_url: {embed_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # A função _extract_embed_url busca o textarea readonly e extrai o link
        logger.info(f"DEBUG - Chamando _extract_embed_url com URL: {embed_url}")
        print(f"DEBUG - Chamando _extract_embed_url com URL: {embed_url}")
        
        extracted_url = _extract_embed_url(embed_url, headers)
        
        logger.info(f"DEBUG - Resultado de _extract_embed_url: {extracted_url}")
        print(f"DEBUG - Resultado de _extract_embed_url: {extracted_url}")
        
        if extracted_url:
            logger.info(f"DEBUG - Sucesso! URL extraída: {extracted_url}")
            print(f"DEBUG - Sucesso! URL extraída: {extracted_url}")
            return JsonResponse({
                'success': True,
                'url': extracted_url
            }, content_type='application/json')
        else:
            logger.warning(f"DEBUG - Falha: Não foi possível extrair URL do embed")
            print("DEBUG - Falha: Não foi possível extrair URL do embed")
            return JsonResponse({
                'success': False,
                'error': 'Não foi possível extrair o link do embed. Textarea readonly não encontrado ou sem URL válida.',
                'debug_info': {
                    'embed_url_requested': embed_url,
                    'message': 'Verifique os logs do servidor para mais detalhes'
                }
            }, status=404, content_type='application/json')
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"DEBUG - Exceção na view admin_extract_embed_link: {str(e)}")
        logger.error(f"DEBUG - Traceback completo:\n{error_trace}")
        print(f"DEBUG - Exceção na view admin_extract_embed_link: {str(e)}")
        print(f"DEBUG - Traceback completo:\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao extrair link: {str(e)}',
            'debug_info': {
                'traceback': error_trace[:500]  # Limitar tamanho do traceback
            }
        }, status=500, content_type='application/json')


@user_passes_test(staff_required, login_url='home')
@require_http_methods(["POST"])
def admin_create_game_from_request(request, pk):
    """
    Cria um jogo no catálogo a partir dos dados coletados pela API.
    """
    game_request = get_object_or_404(GameRequest, pk=pk)
    
    if not game_request.ai_response_data:
        messages.error(request, 'Nenhum dado da API disponível para criar o jogo.')
        return redirect('admin_game_request_detail', pk=pk)
    
    try:
        # Obter dados do jogo
        game_kwargs = game_request.to_game_kwargs()
        
        # Criar o jogo
        game = Game.objects.create(**game_kwargs)
        
        messages.success(
            request,
            f'Jogo "{game.title}" criado com sucesso no catálogo!'
        )
        
        return redirect('admin_game_requests_list')
        
    except Exception as e:
        messages.error(request, f'Erro ao criar jogo: {str(e)}')
        return redirect('admin_game_request_detail', pk=pk)
