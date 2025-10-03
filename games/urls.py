from django.urls import path
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.home, name='home'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('plan/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    
    # Autenticação
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Páginas autenticadas
    path('library/', views.library, name='library'),
    
    # Checkout
    path('checkout/game/<int:game_id>/', views.checkout_game, name='checkout_game'),
    path('checkout/plan/<int:plan_id>/', views.checkout_plan, name='checkout_plan'),
    
    # Pagamento
    path('payment/<str:session_id>/', views.payment_session, name='payment_session'),
    path('payment/<str:session_id>/success/', views.simulate_payment_success, name='payment_success'),
    path('payment/<str:session_id>/failure/', views.simulate_payment_failure, name='payment_failure'),
    path('purchase/<str:session_id>/confirmation/', views.purchase_confirmation, name='purchase_confirmation'),
    
    # Gerenciamento de assinatura
    path('subscription/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # API Endpoints
    path('api/validate-token/', views.api_validate_token, name='api_validate_token'),
    path('api/game/<int:game_id>/', views.api_get_game_info, name='api_get_game_info'),
    path('api/revoke-token/', views.api_revoke_token, name='api_revoke_token'),
    path('api/user/tokens/', views.api_user_tokens, name='api_user_tokens'),
    
    # Admin/Setup Endpoints
    path('api/setup-data/', views.setup_initial_data, name='setup_initial_data'),
]