from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais do TDE
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('game/<slug:slug>/', views.game_detail, name='game_detail'),
    
    # Autenticação (opcional - mantida para demonstração)
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Solicitação de jogos (requer login)
    path('request-game/', views.request_game, name='request_game'),
    path('meus-pedidos/', views.my_game_requests, name='my_game_requests'),
    
    # API Endpoints
    path('api/game/<slug:slug>/', views.api_get_game_info, name='api_get_game_info'),
]

# ============================================================================
# ROTAS REMOVIDAS (domínio antigo de compras/assinaturas/tokens)
# ============================================================================
# As seguintes rotas foram removidas pois não são mais necessárias:
# - checkout_game, checkout_plan
# - payment_session, payment_success, payment_failure
# - purchase_confirmation
# - cancel_subscription
# - library, library_game_detail
# - plan_detail
# - api_validate_token, api_revoke_token, api_user_tokens
# - setup_initial_data
# ============================================================================
