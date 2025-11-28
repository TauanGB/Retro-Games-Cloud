"""
URL configuration for retro_games_cloud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from games import views as games_views

urlpatterns = [
    # Rotas administrativas personalizadas (devem vir antes do admin padrão)
    path('admin/game-requests/', games_views.admin_game_requests_list, name='admin_game_requests_list'),
    path('admin/game-requests/<int:pk>/', games_views.admin_game_request_detail, name='admin_game_request_detail'),
    path('admin/game-requests/<int:pk>/approve/', games_views.admin_approve_request, name='admin_approve_request'),
    path('admin/game-requests/<int:pk>/reject/', games_views.admin_reject_request, name='admin_reject_request'),
    path('admin/game-requests/<int:pk>/check-status/', games_views.admin_check_api_status, name='admin_check_api_status'),
    path('admin/game-requests/<int:pk>/search-retrogames/', games_views.admin_search_retrogames, name='admin_search_retrogames'),
    path('admin/game-requests/<int:pk>/create-game/', games_views.admin_create_game_from_request, name='admin_create_game_from_request'),
    
    # Django Admin padrão
    path('admin/', admin.site.urls),
    
    # URLs do app games
    path('', include('games.urls')),
]

# Servir arquivos estáticos e mídia quando DEBUG=True ou usando WhiteNoise
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
