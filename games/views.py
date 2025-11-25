from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.core.management import call_command
from django.core.management.base import CommandError
from datetime import timedelta
import uuid
import json
import io
import sys
from contextlib import redirect_stdout

from .models import Game, Plan, Purchase, Subscription, Entitlement, PaymentSession, GameToken


def home(request):
    """Página inicial com catálogo público de jogos e planos"""
    games = Game.objects.filter(is_active=True)
    plans = Plan.objects.filter(is_active=True)
    
    # Filtrar por console se especificado
    console_filter = request.GET.get('console')
    if console_filter and console_filter != 'Todos':
        games = games.filter(console=console_filter)
    
    # Obter consoles únicos para filtros (excluindo PC)
    consoles = Game.objects.filter(is_active=True).exclude(console='PC').values_list('console', flat=True).distinct().order_by('console')
    
    context = {
        'games': games,
        'plans': plans,
        'consoles': consoles,
        'current_filter': console_filter or 'Todos'
    }
    
    return render(request, 'games/home.html', context)


def game_detail(request, game_id):
    """Página de detalhes do jogo"""
    game = get_object_or_404(Game, id=game_id, is_active=True)
    
    # Verificar se o usuário já tem acesso ao jogo
    user_has_access = False
    if request.user.is_authenticated:
        user_has_access = Entitlement.objects.filter(
            user=request.user, 
            game=game
        ).exists()
    
    # Buscar planos que contêm este jogo
    plans_with_game = Plan.objects.filter(
        games=game,
        is_active=True
    ).distinct()
    
    # Verificar se o usuário já tem assinaturas ativas para estes planos
    user_active_subscriptions = []
    if request.user.is_authenticated:
        user_active_subscriptions = Subscription.objects.filter(
            user=request.user,
            plan__in=plans_with_game,
            status='active',
            current_period_end__gt=timezone.now()
        ).values_list('plan_id', flat=True)
    
    context = {
        'game': game,
        'user_has_access': user_has_access,
        'plans_with_game': plans_with_game,
        'user_active_subscriptions': user_active_subscriptions
    }
    
    return render(request, 'games/game_detail.html', context)


def plan_detail(request, plan_id):
    """Página de detalhes do plano"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    
    # Verificar se o usuário já tem assinatura ativa
    user_has_subscription = False
    if request.user.is_authenticated:
        user_has_subscription = Subscription.objects.filter(
            user=request.user,
            plan=plan,
            status='active',
            current_period_end__gt=timezone.now()
        ).exists()
    
    context = {
        'plan': plan,
        'user_has_subscription': user_has_subscription
    }
    
    return render(request, 'games/plan_detail.html', context)


def user_login(request):
    """Página de login"""
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
    """Página de registro"""
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


@login_required
def library(request):
    """Biblioteca do usuário"""
    # Jogos comprados individualmente
    purchased_games = Entitlement.objects.filter(
        user=request.user,
        purchase__isnull=False,
        is_perpetual=True
    ).select_related('game')
    
    # Jogos de assinaturas ativas
    active_subscriptions = Subscription.objects.filter(
        user=request.user,
        status='active',
        current_period_end__gt=timezone.now()
    ).select_related('plan')
    
    subscription_games = []
    for subscription in active_subscriptions:
        for game in subscription.plan.games.filter(is_active=True):
            subscription_games.append({
                'game': game,
                'subscription': subscription,
                'plan': subscription.plan
            })
    
    # Tokens de acesso aos jogos
    game_tokens = GameToken.objects.filter(
        user=request.user,
        status='active'
    ).select_related('game', 'entitlement')
    
    context = {
        'purchased_games': purchased_games,
        'subscription_games': subscription_games,
        'active_subscriptions': active_subscriptions,
        'game_tokens': game_tokens
    }
    
    return render(request, 'games/library.html', context)


@login_required
def library_game_detail(request, game_id):
    """Página de detalhes do jogo na biblioteca do usuário"""
    game = get_object_or_404(Game, id=game_id, is_active=True)
    
    # Verificar se o usuário tem acesso ao jogo
    entitlement = Entitlement.objects.filter(
        user=request.user, 
        game=game
    ).first()
    
    if not entitlement:
        messages.error(request, 'Você não possui acesso a este jogo.')
        return redirect('library')
    
    # Obter token ativo para o jogo
    game_token = None
    if entitlement:
        game_token = entitlement.get_active_token()
    
    # Verificar se é compra individual ou assinatura
    is_purchased = entitlement.purchase is not None
    is_subscription = entitlement.subscription is not None
    
    # Informações adicionais
    purchase_info = None
    subscription_info = None
    
    if is_purchased and entitlement.purchase:
        purchase_info = entitlement.purchase
    elif is_subscription and entitlement.subscription:
        subscription_info = entitlement.subscription
    
    context = {
        'game': game,
        'entitlement': entitlement,
        'game_token': game_token,
        'is_purchased': is_purchased,
        'is_subscription': is_subscription,
        'purchase_info': purchase_info,
        'subscription_info': subscription_info,
        'has_valid_token': game_token is not None
    }
    
    return render(request, 'games/library_game_detail.html', context)


@login_required
def checkout_game(request, game_id):
    """Iniciar checkout para compra de jogo"""
    game = get_object_or_404(Game, id=game_id, is_active=True)
    
    # Verificar se já tem o jogo
    if Entitlement.objects.filter(user=request.user, game=game).exists():
        messages.warning(request, 'Você já possui este jogo!')
        return redirect('game_detail', game_id=game_id)
    
    # Criar sessão de pagamento
    session = PaymentSession.objects.create(
        user=request.user,
        game=game,
        amount=game.price
    )
    
    return redirect('payment_session', session_id=session.session_id)


@login_required
def checkout_plan(request, plan_id):
    """Iniciar checkout para assinatura de plano"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    
    # Verificar se já tem assinatura ativa
    if Subscription.objects.filter(
        user=request.user,
        plan=plan,
        status='active',
        current_period_end__gt=timezone.now()
    ).exists():
        messages.warning(request, 'Você já possui uma assinatura ativa para este plano!')
        return redirect('plan_detail', plan_id=plan_id)
    
    # Criar sessão de pagamento
    session = PaymentSession.objects.create(
        user=request.user,
        plan=plan,
        amount=plan.price
    )
    
    return redirect('payment_session', session_id=session.session_id)


@login_required
def payment_session(request, session_id):
    """Página de simulação de pagamento"""
    session = get_object_or_404(PaymentSession, session_id=session_id, user=request.user)
    
    if session.status != 'pending':
        messages.warning(request, 'Esta sessão de pagamento já foi processada.')
        return redirect('home')
    
    context = {
        'session': session,
        'item': session.game or session.plan
    }
    
    return render(request, 'games/payment_session.html', context)


@login_required
@require_http_methods(["POST"])
def simulate_payment_success(request, session_id):
    """Simular pagamento bem-sucedido"""
    session = get_object_or_404(PaymentSession, session_id=session_id, user=request.user)
    
    if session.status != 'pending':
        messages.error(request, 'Esta sessão já foi processada.')
        return redirect('home')
    
    with transaction.atomic():
        # Atualizar status da sessão
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        
        if session.game:
            # Compra de jogo individual
            purchase = Purchase.objects.create(
                user=request.user,
                game=session.game,
                amount=session.amount,
                status='completed'
            )
            
            # Criar entitlement perpétuo
            entitlement = Entitlement.objects.create(
                user=request.user,
                game=session.game,
                purchase=purchase,
                is_perpetual=True
            )
            
            # Gerar token de acesso para o jogo automaticamente
            game_token = entitlement.create_game_token()
            if game_token:
                print(f"Token gerado automaticamente: {game_token.token[:8]}... para {session.game.title}")
            else:
                print(f"Erro ao gerar token para {session.game.title}")
            
            messages.success(request, f'Jogo {session.game.title} comprado com sucesso!')
            
            # Redirecionar para página de confirmação com token
            return redirect('purchase_confirmation', session_id=session.session_id)
            
        elif session.plan:
            # Assinatura de plano
            subscription = Subscription.objects.create(
                user=request.user,
                plan=session.plan,
                current_period_end=timezone.now() + timedelta(days=30)
            )
            
            # Criar entitlements para todos os jogos do plano
            for game in session.plan.games.filter(is_active=True):
                entitlement, created = Entitlement.objects.get_or_create(
                    user=request.user,
                    game=game,
                    subscription=subscription,
                    is_perpetual=False
                )
                
                # Gerar token automaticamente (método verifica se já existe)
                game_token = entitlement.create_game_token()
                if game_token and created:
                    print(f"Token gerado automaticamente: {game_token.token[:8]}... para {game.title}")
                elif not game_token:
                    print(f"Erro ao gerar token para {game.title}")
            
            messages.success(request, f'Assinatura do plano {session.plan.name} ativada com sucesso!')
            
            # Redirecionar para página de confirmação com tokens
            return redirect('purchase_confirmation', session_id=session.session_id)
    
    return redirect('library')


@login_required
def purchase_confirmation(request, session_id):
    """Página de confirmação de compra com token de acesso"""
    session = get_object_or_404(PaymentSession, session_id=session_id, user=request.user)
    
    if session.status != 'completed':
        messages.error(request, 'Esta sessão de pagamento não foi concluída.')
        return redirect('home')
    
    # Obter tokens gerados para esta sessão
    tokens = []
    
    if session.game:
        # Compra individual
        entitlement = Entitlement.objects.filter(
            user=request.user,
            game=session.game,
            purchase__isnull=False
        ).first()
        
        if entitlement:
            game_token = entitlement.get_active_token()
            if game_token:
                tokens.append({
                    'game': session.game,
                    'token': game_token,
                    'entitlement': entitlement
                })
    
    elif session.plan:
        # Assinatura de plano
        subscription = Subscription.objects.filter(
            user=request.user,
            plan=session.plan,
            status='active'
        ).first()
        
        if subscription:
            entitlements = Entitlement.objects.filter(
                user=request.user,
                subscription=subscription
            ).select_related('game')
            
            for entitlement in entitlements:
                game_token = entitlement.get_active_token()
                if game_token:
                    tokens.append({
                        'game': entitlement.game,
                        'token': game_token,
                        'entitlement': entitlement
                    })
    
    context = {
        'session': session,
        'tokens': tokens,
        'item': session.game or session.plan,
        'is_plan': bool(session.plan)
    }
    
    return render(request, 'games/purchase_confirmation.html', context)


@login_required
@require_http_methods(["POST"])
def simulate_payment_failure(request, session_id):
    """Simular falha no pagamento"""
    session = get_object_or_404(PaymentSession, session_id=session_id, user=request.user)
    
    if session.status != 'pending':
        messages.error(request, 'Esta sessão já foi processada.')
        return redirect('home')
    
    session.status = 'failed'
    session.completed_at = timezone.now()
    session.save()
    
    messages.error(request, 'Pagamento falhou. Tente novamente.')
    
    if session.game:
        return redirect('game_detail', game_id=session.game.id)
    else:
        return redirect('plan_detail', plan_id=session.plan.id)


@login_required
@require_http_methods(["POST"])
def cancel_subscription(request, subscription_id):
    """Cancelar assinatura"""
    subscription = get_object_or_404(
        Subscription, 
        id=subscription_id, 
        user=request.user,
        status='active'
    )
    
    subscription.status = 'cancelled'
    subscription.cancelled_at = timezone.now()
    subscription.save()
    
    messages.success(request, f'Assinatura do plano {subscription.plan.name} cancelada. Você manterá acesso até {subscription.current_period_end.strftime("%d/%m/%Y")}.')
    
    return redirect('library')


# API Endpoints para validação de tokens

@csrf_exempt
@require_http_methods(["POST"])
@never_cache
def api_validate_token(request):
    """
    API para validar token de acesso a jogo
    Endpoint: POST /api/validate-token/
    
    Body JSON:
    {
        "token": "token_string",
        "game_id": 123 (opcional)
    }
    
    Response:
    {
        "valid": true/false,
        "game": {
            "id": 123,
            "title": "Nome do Jogo",
            "console": "SNES"
        },
        "user": {
            "id": 456,
            "username": "usuario"
        },
        "entitlement": {
            "is_perpetual": true/false,
            "granted_date": "2024-01-01T00:00:00Z"
        },
        "token_info": {
            "created_at": "2024-01-01T00:00:00Z",
            "last_used_at": "2024-01-01T00:00:00Z",
            "usage_count": 5
        }
    }
    """
    try:
        data = json.loads(request.body)
        token = data.get('token')
        game_id = data.get('game_id')
        
        if not token:
            return JsonResponse({
                'valid': False,
                'error': 'Token é obrigatório'
            }, status=400)
        
        # Validar token
        validation_result = GameToken.validate_token(token, game_id)
        
        if not validation_result:
            return JsonResponse({
                'valid': False,
                'error': 'Token inválido ou expirado'
            }, status=401)
        
        game_token = validation_result['token']
        game = validation_result['game']
        user = validation_result['user']
        entitlement = validation_result['entitlement']
        
        return JsonResponse({
            'valid': True,
            'game': {
                'id': game.id,
                'title': game.title,
                'console': game.console,
                'description': game.description
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'entitlement': {
                'is_perpetual': entitlement.is_perpetual,
                'granted_date': entitlement.granted_date.isoformat()
            },
            'token_info': {
                'created_at': game_token.created_at.isoformat(),
                'last_used_at': game_token.last_used_at.isoformat() if game_token.last_used_at else None,
                'usage_count': game_token.usage_count,
                'expires_at': game_token.expires_at.isoformat() if game_token.expires_at else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'valid': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@never_cache
def api_get_game_info(request, game_id):
    """
    API para obter informações de um jogo específico
    Endpoint: GET /api/game/{game_id}/
    
    Response:
    {
        "id": 123,
        "title": "Nome do Jogo",
        "console": "SNES",
        "description": "Descrição do jogo",
        "price": "29.99",
        "cover_image": "url_da_capa",
        "categories": [
            {
                "id": 1,
                "name": "Ação",
                "color": "#ff0000"
            }
        ]
    }
    """
    try:
        game = get_object_or_404(Game, id=game_id, is_active=True)
        
        return JsonResponse({
            'id': game.id,
            'title': game.title,
            'console': game.console,
            'description': game.description,
            'price': str(game.price),
            'cover_image': game.cover_image,
            'rom_url': game.rom_url,
            'categories': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'color': cat.color,
                    'icon': cat.icon
                }
                for cat in game.categories.filter(is_active=True)
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Jogo não encontrado'
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
@never_cache
def api_revoke_token(request):
    """
    API para revogar um token
    Endpoint: POST /api/revoke-token/
    
    Body JSON:
    {
        "token": "token_string"
    }
    
    Response:
    {
        "success": true/false,
        "message": "Token revogado com sucesso"
    }
    """
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({
                'success': False,
                'error': 'Token é obrigatório'
            }, status=400)
        
        # Buscar token pelo hash
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        try:
            game_token = GameToken.objects.get(token_hash=token_hash, status='active')
            game_token.revoke()
            
            return JsonResponse({
                'success': True,
                'message': 'Token revogado com sucesso'
            })
            
        except GameToken.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Token não encontrado'
            }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_user_tokens(request):
    """
    API para listar tokens do usuário logado
    Endpoint: GET /api/user/tokens/
    
    Response:
    {
        "tokens": [
            {
                "id": 123,
                "game": {
                    "id": 456,
                    "title": "Nome do Jogo",
                    "console": "SNES"
                },
                "token": "token_string",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "last_used_at": "2024-01-01T00:00:00Z",
                "usage_count": 5
            }
        ]
    }
    """
    try:
        tokens = GameToken.objects.filter(
            user=request.user,
            status='active'
        ).select_related('game')
        
        tokens_data = []
        for token in tokens:
            tokens_data.append({
                'id': token.id,
                'game': {
                    'id': token.game.id,
                    'title': token.game.title,
                    'console': token.game.console
                },
                'token': token.token,
                'status': token.status,
                'created_at': token.created_at.isoformat(),
                'last_used_at': token.last_used_at.isoformat() if token.last_used_at else None,
                'usage_count': token.usage_count,
                'expires_at': token.expires_at.isoformat() if token.expires_at else None
            })
        
        return JsonResponse({
            'tokens': tokens_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def setup_initial_data(request):
    """
    Endpoint para configurar dados iniciais do sistema
    Executa o comando setup_data para criar categorias, planos e consoles
    
    Body JSON (opcional):
    {
        "categories_only": true/false,
        "plans_only": true/false,
        "force": true/false
    }
    
    Response:
    {
        "success": true/false,
        "message": "Mensagem de resultado",
        "output": "Saída do comando"
    }
    """
    try:
        # Capturar parâmetros do request
        data = json.loads(request.body) if request.body else {}
        categories_only = data.get('categories_only', False)
        plans_only = data.get('plans_only', False)
        force = data.get('force', False)
        
        # Capturar saída do comando
        output_buffer = io.StringIO()
        
        # Preparar argumentos do comando
        command_args = []
        if categories_only:
            command_args.append('--categories-only')
        if plans_only:
            command_args.append('--plans-only')
        if force:
            command_args.append('--force')
        
        # Executar comando
        with redirect_stdout(output_buffer):
            call_command('setup_data', *command_args, verbosity=2)
        
        output = output_buffer.getvalue()
        
        return JsonResponse({
            'success': True,
            'message': 'Dados iniciais configurados com sucesso',
            'output': output
        })
        
    except CommandError as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro no comando: {str(e)}',
            'output': ''
        }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido no corpo da requisição',
            'output': ''
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}',
            'output': ''
        }, status=500)