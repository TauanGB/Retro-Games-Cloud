#!/usr/bin/env python
"""
Comando Django para popular o banco de dados com jogos retro
"""

import json
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from games.models import Game, Plan

# Dados dos jogos integrados diretamente no comando
GAMES_DATA = [
    {
        "nome": "Super Mario Bros. 3 (NES)",
        "descricao": "Plataforma 2D com power-ups e mapas de mundo.",
        "link_imagem": "https://cdn.mobygames.com/covers/4041316-super-mario-bros-3-nes-front-cover.jpg"
    },
    {
        "nome": "The Legend of Zelda: A Link to the Past (SNES)",
        "descricao": "Aventura top-down com dois mundos paralelos e dungeons memoráveis.",
        "link_imagem": "https://cdn.mobygames.com/covers/4046275-the-legend-of-zelda-a-link-to-the-past-snes-back-cover.jpg"
    },
    {
        "nome": "Super Metroid (SNES)",
        "descricao": "Ação/ exploração não linear em Zebes com upgrades e backtracking.",
        "link_imagem": "https://cdn.mobygames.com/covers/4525515-super-metroid-snes-front-cover.jpg"
    },
    {
        "nome": "Sonic the Hedgehog 2 (Mega Drive/Genesis)",
        "descricao": "Plataforma veloz com Tails e fases icônicas.",
        "link_imagem": "https://cdn.mobygames.com/covers/4128226-sonic-the-hedgehog-2-genesis-front-cover.jpg"
    },
    {
        "nome": "Streets of Rage 2 (Genesis)",
        "descricao": "Beat em up cooperativo clássico com trilha marcante.",
        "link_imagem": "https://cdn.mobygames.com/covers/4035172-streets-of-rage-2-genesis-front-cover.jpg"
    },
    {
        "nome": "Mega Man 2 (NES)",
        "descricao": "Ação/plataforma com chefes temáticos e armas absorvidas.",
        "link_imagem": "https://cdn.mobygames.com/covers/4189509-mega-man-2-nes-front-cover.jpg"
    },
    {
        "nome": "Castlevania: Symphony of the Night (PS1)",
        "descricao": "Ação/exploração com elementos de RPG no castelo de Drácula.",
        "link_imagem": "https://cdn.mobygames.com/covers/5973147-castlevania-symphony-of-the-night-playstation-front-cover.png"
    },
    {
        "nome": "Chrono Trigger (SNES)",
        "descricao": "RPG com viagens no tempo e múltiplos finais.",
        "link_imagem": "https://cdn.mobygames.com/covers/3933436-chrono-trigger-snes-front-cover.jpg"
    },
    {
        "nome": "Final Fantasy VII (PS1)",
        "descricao": "RPG cinematográfico com sistema Materia.",
        "link_imagem": "https://cdn.mobygames.com/covers/4306305-final-fantasy-vii-playstation-front-cover.jpg"
    },
    {
        "nome": "DOOM (PC-DOS)",
        "descricao": "FPS pioneiro com ação frenética em labirintos cheios de demônios.",
        "link_imagem": "https://cdn.mobygames.com/covers/3947919-doom-dos-front-cover.jpg"
    },
    {
        "nome": "Metal Slug (Neo Geo)",
        "descricao": "Run n gun com animação detalhada e humor.",
        "link_imagem": "https://cdn.mobygames.com/covers/6866945-metal-slug-super-vehicle-001-neo-geo-cd-front-cover.jpg"
    },
    {
        "nome": "Super Street Fighter II (SNES)",
        "descricao": "Luta 2D com elenco ampliado e golpes icônicos.",
        "link_imagem": "https://cdn.mobygames.com/covers/4180952-super-street-fighter-ii-snes-front-cover.jpg"
    },
    {
        "nome": "Pac-Man (Arcade/ports)",
        "descricao": "Arcade de labirinto: coma pílulas e evite os fantasmas.",
        "link_imagem": "https://cdn.mobygames.com/d81cffd0-abd1-11ed-8d2b-02420a00019e.webp"
    },
    {
        "nome": "Tetris (Game Boy)",
        "descricao": "Puzzle de encaixe de peças simples e viciante.",
        "link_imagem": "https://cdn.mobygames.com/covers/5453704-tetris-game-boy-front-cover.jpg"
    },
    {
        "nome": "Donkey Kong Country 2: Diddy's Kong Quest (SNES)",
        "descricao": "Plataforma 2D com Diddy e Dixie, muitos segredos.",
        "link_imagem": "https://cdn.mobygames.com/covers/3946277-donkey-kong-country-2-diddys-kong-quest-snes-front-cover.jpg"
    },
    {
        "nome": "Tony Hawks Pro Skater 2 (PS1)",
        "descricao": "Skate com combos longos e objetivos por fase.",
        "link_imagem": "https://cdn.mobygames.com/covers/5557286-tony-hawks-pro-skater-2-playstation-front-cover.png"
    },
    {
        "nome": "Tekken 3 (PS1)",
        "descricao": "Luta 3D fluida com elenco marcante.",
        "link_imagem": "https://cdn.mobygames.com/covers/3987061-tekken-3-playstation-front-cover.jpg"
    },
    {
        "nome": "The Legend of Zelda: Links Awakening (GB)",
        "descricao": "Aventura portátil na Ilha Koholint com dungeons criativas.",
        "link_imagem": "https://cdn.mobygames.com/covers/3983327-the-legend-of-zelda-links-awakening-game-boy-front-cover.jpg"
    },
    {
        "nome": "Metroid Fusion (GBA)",
        "descricao": "Ação/exploração mais linear e atmosfera de suspense.",
        "link_imagem": "https://cdn.mobygames.com/covers/3989003-metroid-fusion-game-boy-advance-front-cover.jpg"
    },
    {
        "nome": "Advance Wars (GBA)",
        "descricao": "Estratégia em turnos com unidades variadas e mapas táticos.",
        "link_imagem": "https://cdn.mobygames.com/covers/4111970-advance-wars-game-boy-advance-front-cover.jpg"
    }
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com jogos retro integrados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Caminho para arquivo JSON externo (opcional, usa dados integrados por padrão)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar recriação mesmo se já existir jogos',
        )
        parser.add_argument(
            '--no-plans',
            action='store_true',
            help='Não criar planos, apenas jogos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== POPULANDO BANCO DE DADOS ==='))
        
        try:
            with transaction.atomic():
                # Usar dados integrados por padrão ou arquivo JSON se especificado
                if options['json_file']:
                    self.populate_games_from_file(options['json_file'], options['force'])
                else:
                    self.populate_games_from_data(GAMES_DATA, options['force'])
                
                if not options['no_plans']:
                    self.create_plans(options['force'])
                
                self.show_stats()
                
                self.stdout.write(self.style.SUCCESS('\n=== CONCLUÍDO ==='))
                self.stdout.write('Banco de dados populado com sucesso!')
                self.stdout.write('Execute "python manage.py runserver" para iniciar o servidor.')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO: {e}'))
            raise

    def extract_console_from_name(self, game_name):
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

    def clean_image_url(self, url):
        """Limpa a URL da imagem removendo markdown"""
        if url.startswith('[') and url.endswith(']'):
            # Remove os colchetes
            url = url[1:-1]
            # Remove o texto entre parênteses se existir
            if '(' in url and ')' in url:
                url = url.split('(')[0]
        return url.strip()

    def populate_games_from_data(self, games_data, force=False):
        """Popula o banco com jogos dos dados integrados"""
        # Verificar se já existem jogos
        if Game.objects.exists() and not force:
            self.stdout.write(self.style.WARNING('Jogos já existem no banco. Use --force para recriar.'))
            return
        
        # Limpar jogos existentes se force=True
        if force:
            Game.objects.all().delete()
            Plan.objects.all().delete()
            self.stdout.write('Jogos e planos existentes removidos.')
        
        self.stdout.write(f'Usando dados integrados. {len(games_data)} jogos encontrados.')
        
        # Criar jogos
        created_games = []
        for game_data in games_data:
            try:
                # Extrair console do nome
                console = self.extract_console_from_name(game_data['nome'])
                
                # Limpar URL da imagem
                image_url = self.clean_image_url(game_data['link_imagem'])
                
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
                self.stdout.write(f'[OK] Jogo criado: {game.title} ({console}) - R$ {game.price}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[ERRO] Falha ao criar jogo {game_data["nome"]}: {e}'))
        
        self.stdout.write(f'\nTotal de jogos criados: {len(created_games)}')

    def populate_games_from_file(self, json_file, force=False):
        """Popula o banco com jogos de arquivo JSON externo"""
        # Verificar se já existem jogos
        if Game.objects.exists() and not force:
            self.stdout.write(self.style.WARNING('Jogos já existem no banco. Use --force para recriar.'))
            return
        
        # Limpar jogos existentes se force=True
        if force:
            Game.objects.all().delete()
            Plan.objects.all().delete()
            self.stdout.write('Jogos e planos existentes removidos.')
        
        # Ler arquivo JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                games_data = json.load(f)
            self.stdout.write(f'Arquivo JSON lido com sucesso. {len(games_data)} jogos encontrados.')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'ERRO: Arquivo {json_file} não encontrado!'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'ERRO: Erro ao decodificar JSON: {e}'))
            return
        
        # Criar jogos
        created_games = []
        for game_data in games_data:
            try:
                # Extrair console do nome
                console = self.extract_console_from_name(game_data['nome'])
                
                # Limpar URL da imagem
                image_url = self.clean_image_url(game_data['link_imagem'])
                
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
                self.stdout.write(f'[OK] Jogo criado: {game.title} ({console}) - R$ {game.price}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[ERRO] Falha ao criar jogo {game_data["nome"]}: {e}'))
        
        self.stdout.write(f'\nTotal de jogos criados: {len(created_games)}')

    def create_plans(self, force=False):
        """Cria planos"""
        self.stdout.write('\n=== CRIANDO PLANOS ===')
        
        # Plano Básico - NES, Game Boy, GBA, Mega Drive
        basic_consoles = ['NES', 'Game Boy', 'GBA', 'Mega Drive']
        basic_games = Game.objects.filter(console__in=basic_consoles)
        
        basic_plan, created = Plan.objects.get_or_create(
            name="Plano Básico",
            defaults={
                'description': "Acesso a jogos clássicos dos consoles dos anos 80 e 90. Inclui jogos do NES, Game Boy, GBA e Mega Drive.",
                'price': Decimal('19.90')
            }
        )
        
        if created or force:
            basic_plan.games.set(basic_games)
            self.stdout.write(f'[OK] Plano Básico criado: {basic_plan.name} - R$ {basic_plan.price} ({basic_games.count()} jogos)')
        else:
            self.stdout.write(f'[EXISTS] Plano Básico já existe')
        
        # Plano Premium - Todos os jogos
        premium_plan, created = Plan.objects.get_or_create(
            name="Plano Premium",
            defaults={
                'description': "Acesso completo a todos os jogos da plataforma. Inclui jogos de todos os consoles disponíveis.",
                'price': Decimal('39.90')
            }
        )
        
        if created or force:
            premium_plan.games.set(Game.objects.all())
            self.stdout.write(f'[OK] Plano Premium criado: {premium_plan.name} - R$ {premium_plan.price} ({Game.objects.count()} jogos)')
        else:
            self.stdout.write(f'[EXISTS] Plano Premium já existe')
        
        self.stdout.write(f'\nTotal de planos: {Plan.objects.count()}')

    def show_stats(self):
        """Mostra estatísticas do banco"""
        total_games = Game.objects.count()
        total_plans = Plan.objects.count()
        
        # Usar distinct() para evitar duplicatas
        consoles = Game.objects.values_list('console', flat=True).distinct().order_by('console')
        
        self.stdout.write(f'\n=== ESTATÍSTICAS ===')
        self.stdout.write(f'Total de jogos: {total_games}')
        self.stdout.write(f'Total de planos: {total_plans}')
        self.stdout.write(f'Consoles disponíveis: {", ".join(consoles)}')
        
        self.stdout.write(f'\n=== JOGOS POR CONSOLE ===')
        for console in consoles:
            count = Game.objects.filter(console=console).count()
            self.stdout.write(f'{console}: {count} jogos')
        
        self.stdout.write(f'\n=== PLANOS ===')
        for plan in Plan.objects.all():
            self.stdout.write(f'{plan.name}: R$ {plan.price} - {plan.games.count()} jogos')
