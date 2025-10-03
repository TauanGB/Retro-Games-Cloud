#!/usr/bin/env python
"""
Script para popular o banco de dados com jogos do arquivo Jogos_Temp1.json
"""

import os
import sys
import django
import json
import random
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retro_games_cloud.settings')
django.setup()

from games.models import Game, Plan

def extract_console_from_name(game_name):
    """Extrai o console do nome do jogo"""
    # Ordem específica para evitar conflitos (mais específico primeiro)
    if 'GBA' in game_name:
        return 'GBA'
    elif 'Game Boy' in game_name or 'GB)' in game_name:
        return 'Game Boy'
    elif 'SNES' in game_name:
        return 'SNES'
    elif 'Mega Drive' in game_name or 'Genesis' in game_name:
        return 'Mega Drive'
    elif 'PS1' in game_name:
        return 'PlayStation'
    elif 'PC-DOS' in game_name:
        return 'PC'
    elif 'Neo Geo' in game_name:
        return 'Neo Geo'
    elif 'Arcade' in game_name:
        return 'Arcade'
    elif 'NES' in game_name:
        return 'NES'
    
    return 'Outros'

def clean_image_url(url):
    """Limpa a URL da imagem removendo markdown"""
    if url.startswith('[') and url.endswith(']'):
        # Remove os colchetes
        url = url[1:-1]
        # Remove o texto entre parênteses se existir
        if '(' in url and ')' in url:
            url = url.split('(')[0]
    return url.strip()

def populate_games():
    """Popula o banco com jogos do JSON"""
    print("=== POPULANDO BANCO DE DADOS ===")
    
    # Limpar jogos existentes
    Game.objects.all().delete()
    Plan.objects.all().delete()
    print("Jogos e planos existentes removidos.")
    
    # Ler arquivo JSON
    try:
        with open('Jogos_Temp1.json', 'r', encoding='utf-8') as f:
            games_data = json.load(f)
        print(f"Arquivo JSON lido com sucesso. {len(games_data)} jogos encontrados.")
    except FileNotFoundError:
        print("ERRO: Arquivo Jogos_Temp1.json não encontrado!")
        return
    except json.JSONDecodeError as e:
        print(f"ERRO: Erro ao decodificar JSON: {e}")
        return
    
    # Criar jogos
    created_games = []
    for game_data in games_data:
        try:
            # Extrair console do nome
            console = extract_console_from_name(game_data['nome'])
            
            # Limpar URL da imagem
            image_url = clean_image_url(game_data['link_imagem'])
            
            # Gerar preço aleatório entre R$ 9,90 e R$ 49,90
            price = Decimal(str(random.uniform(9.90, 49.90))).quantize(Decimal('0.01'))
            
            # Criar jogo
            game = Game.objects.create(
                title=game_data['nome'],
                description=game_data['descricao'],
                console=console,
                cover_image=image_url,
                price=price
            )
            created_games.append(game)
            print(f"[OK] Jogo criado: {game.title} ({console}) - R$ {game.price}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao criar jogo {game_data['nome']}: {e}")
    
    print(f"\nTotal de jogos criados: {len(created_games)}")
    
    # Criar planos
    print("\n=== CRIANDO PLANOS ===")
    
    # Plano Básico - NES, Game Boy, GBA, Mega Drive
    basic_consoles = ['NES', 'Game Boy', 'GBA', 'Mega Drive']
    basic_games = Game.objects.filter(console__in=basic_consoles)
    
    basic_plan = Plan.objects.create(
        name="Plano Básico",
        description="Acesso a jogos clássicos dos consoles dos anos 80 e 90. Inclui jogos do NES, Game Boy, GBA e Mega Drive.",
        price=Decimal('19.90')
    )
    basic_plan.games.set(basic_games)
    print(f"[OK] Plano Básico criado: {basic_plan.name} - R$ {basic_plan.price} ({basic_games.count()} jogos)")
    
    # Plano Premium - Todos os jogos
    premium_plan = Plan.objects.create(
        name="Plano Premium",
        description="Acesso completo a todos os jogos da plataforma. Inclui jogos de todos os consoles disponíveis.",
        price=Decimal('39.90')
    )
    premium_plan.games.set(Game.objects.all())
    print(f"[OK] Plano Premium criado: {premium_plan.name} - R$ {premium_plan.price} ({Game.objects.count()} jogos)")
    
    print(f"\nTotal de planos criados: {Plan.objects.count()}")

def show_stats():
    """Mostra estatísticas do banco"""
    total_games = Game.objects.count()
    total_plans = Plan.objects.count()
    
    # Usar distinct() para evitar duplicatas
    consoles = Game.objects.values_list('console', flat=True).distinct().order_by('console')
    
    print(f"\n=== ESTATÍSTICAS ===")
    print(f"Total de jogos: {total_games}")
    print(f"Total de planos: {total_plans}")
    print(f"Consoles disponíveis: {', '.join(consoles)}")
    
    print(f"\n=== JOGOS POR CONSOLE ===")
    for console in consoles:
        count = Game.objects.filter(console=console).count()
        print(f"{console}: {count} jogos")
    
    print(f"\n=== PLANOS ===")
    for plan in Plan.objects.all():
        print(f"{plan.name}: R$ {plan.price} - {plan.games.count()} jogos")

if __name__ == '__main__':
    try:
        populate_games()
        show_stats()
        print(f"\n=== CONCLUÍDO ===")
        print("Banco de dados populado com sucesso!")
        print("Execute 'python manage.py runserver' para iniciar o servidor.")
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)