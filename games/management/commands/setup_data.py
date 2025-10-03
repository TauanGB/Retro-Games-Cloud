#!/usr/bin/env python
"""
Comando Django para configurar dados iniciais do sistema
Consolida todos os scripts de criação de categorias, planos e consoles
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal

from games.models import Game, Plan, Category


class Command(BaseCommand):
    help = 'Configura dados iniciais: categorias, planos por console e planos gerais'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Criar apenas as categorias',
        )
        parser.add_argument(
            '--plans-only',
            action='store_true',
            help='Criar apenas os planos',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar recriação mesmo se já existir',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== CONFIGURANDO DADOS INICIAIS ==='))
        
        try:
            with transaction.atomic():
                if not options['plans_only']:
                    self.create_categories(options['force'])
                
                if not options['categories_only']:
                    self.create_console_plans(options['force'])
                    self.create_general_plans(options['force'])
                    self.show_statistics()
                
                self.stdout.write(self.style.SUCCESS('\n=== CONFIGURAÇÃO CONCLUÍDA ==='))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO: {e}'))
            raise

    def create_categories(self, force=False):
        """Cria categorias padrão"""
        self.stdout.write('\n=== CRIANDO CATEGORIAS ===')
        
        categories_data = [
            {
                'name': 'Ação',
                'description': 'Jogos de ação com combate e aventura',
                'color': '#ff6b35',
                'icon': 'fas fa-sword'
            },
            {
                'name': 'Aventura',
                'description': 'Jogos de exploração e descoberta',
                'color': '#00d4ff',
                'icon': 'fas fa-compass'
            },
            {
                'name': 'RPG',
                'description': 'Role-playing games com progressão de personagem',
                'color': '#8b5cf6',
                'icon': 'fas fa-dice-d20'
            },
            {
                'name': 'Plataforma',
                'description': 'Jogos de pulo e movimento em plataformas',
                'color': '#00ff88',
                'icon': 'fas fa-running'
            },
            {
                'name': 'Luta',
                'description': 'Jogos de combate corpo a corpo',
                'color': '#ff0080',
                'icon': 'fas fa-fist-raised'
            },
            {
                'name': 'Estratégia',
                'description': 'Jogos de planejamento e tática',
                'color': '#ffa500',
                'icon': 'fas fa-chess'
            },
            {
                'name': 'Puzzle',
                'description': 'Jogos de quebra-cabeça e lógica',
                'color': '#9c27b0',
                'icon': 'fas fa-puzzle-piece'
            },
            {
                'name': 'Esporte',
                'description': 'Jogos esportivos e de competição',
                'color': '#4caf50',
                'icon': 'fas fa-trophy'
            },
            {
                'name': 'Corrida',
                'description': 'Jogos de velocidade e corrida',
                'color': '#f44336',
                'icon': 'fas fa-car'
            },
            {
                'name': 'Tiro',
                'description': 'Jogos de tiro e combate com armas',
                'color': '#795548',
                'icon': 'fas fa-crosshairs'
            }
        ]
        
        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            
            if created:
                self.stdout.write(f'[OK] Categoria criada: {category.name}')
                created_count += 1
            elif force:
                # Atualizar categoria existente
                for key, value in cat_data.items():
                    setattr(category, key, value)
                category.save()
                self.stdout.write(f'[UPDATED] Categoria atualizada: {category.name}')
            else:
                self.stdout.write(f'[EXISTS] Categoria já existe: {category.name}')
        
        self.stdout.write(f'Total de categorias processadas: {len(categories_data)}')
        if created_count > 0:
            self.stdout.write(f'Categorias criadas: {created_count}')
        
        # Associar categorias aos jogos
        self.assign_categories_to_games()

    def assign_categories_to_games(self):
        """Associa categorias aos jogos baseado no título e descrição"""
        self.stdout.write('\n=== ASSOCIANDO CATEGORIAS AOS JOGOS ===')
        
        # Mapeamento de palavras-chave para categorias
        category_keywords = {
            'Ação': ['mario', 'sonic', 'mega man', 'metal slug', 'streets of rage', 'doom', 'castlevania'],
            'Aventura': ['zelda', 'metroid', 'chrono trigger', 'final fantasy'],
            'RPG': ['final fantasy', 'chrono trigger', 'zelda'],
            'Plataforma': ['mario', 'sonic', 'mega man', 'donkey kong', 'metroid'],
            'Luta': ['street fighter', 'tekken'],
            'Estratégia': ['advance wars'],
            'Puzzle': ['tetris', 'pac-man'],
            'Esporte': ['tony hawk'],
            'Corrida': ['sonic'],
            'Tiro': ['doom', 'metal slug']
        }
        
        games = Game.objects.all()
        total_assigned = 0
        
        for game in games:
            game_categories = []
            game_text = f"{game.title} {game.description}".lower()
            
            for category_name, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in game_text:
                        try:
                            category = Category.objects.get(name=category_name)
                            if category not in game_categories:
                                game_categories.append(category)
                        except Category.DoesNotExist:
                            continue
            
            # Se não encontrou categorias, atribui algumas padrão baseado no console
            if not game_categories:
                if 'mario' in game_text or 'sonic' in game_text:
                    try:
                        action_cat = Category.objects.get(name='Ação')
                        platform_cat = Category.objects.get(name='Plataforma')
                        game_categories.extend([action_cat, platform_cat])
                    except Category.DoesNotExist:
                        pass
                elif 'zelda' in game_text or 'metroid' in game_text:
                    try:
                        adventure_cat = Category.objects.get(name='Aventura')
                        game_categories.append(adventure_cat)
                    except Category.DoesNotExist:
                        pass
                elif 'final fantasy' in game_text or 'chrono' in game_text:
                    try:
                        rpg_cat = Category.objects.get(name='RPG')
                        game_categories.append(rpg_cat)
                    except Category.DoesNotExist:
                        pass
                else:
                    # Categoria padrão para jogos sem classificação específica
                    try:
                        action_cat = Category.objects.get(name='Ação')
                        game_categories.append(action_cat)
                    except Category.DoesNotExist:
                        pass
            
            # Limita a 3 categorias por jogo
            game_categories = game_categories[:3]
            
            if game_categories:
                game.categories.set(game_categories)
                category_names = [cat.name for cat in game_categories]
                self.stdout.write(f'[OK] {game.title}: {", ".join(category_names)}')
                total_assigned += 1
            else:
                self.stdout.write(f'[WARNING] {game.title}: Nenhuma categoria atribuída')
        
        self.stdout.write(f'Total de jogos com categorias: {total_assigned}')

    def create_console_plans(self, force=False):
        """Cria planos específicos para cada console"""
        self.stdout.write('\n=== CRIANDO PLANOS POR CONSOLE ===')
        
        # Obter todos os consoles únicos
        consoles = Game.objects.values_list('console', flat=True).distinct().order_by('console')
        self.stdout.write(f'Consoles encontrados: {list(consoles)}')
        
        # Preços base por console (baseado na popularidade/era)
        console_prices = {
            'Arcade': Decimal('15.90'),
            'GBA': Decimal('12.90'),
            'Game Boy': Decimal('9.90'),
            'Mega Drive': Decimal('14.90'),
            'NES': Decimal('11.90'),
            'Neo Geo': Decimal('19.90'),
            'PC': Decimal('16.90'),
            'PlayStation': Decimal('18.90'),
            'SNES': Decimal('13.90')
        }
        
        created_plans = []
        
        for console in consoles:
            # Contar jogos do console
            games_count = Game.objects.filter(console=console, is_active=True).count()
            
            if games_count == 0:
                self.stdout.write(f'[SKIP] {console}: Nenhum jogo ativo encontrado')
                continue
            
            # Definir preço baseado no console ou usar preço padrão
            price = console_prices.get(console, Decimal('12.90'))
            
            # Criar nome e descrição do plano
            plan_name = f'Plano {console}'
            plan_description = f'Acesso completo a todos os jogos do console {console}. Inclui {games_count} jogos clássicos desta plataforma.'
            
            # Verificar se o plano já existe
            existing_plan = Plan.objects.filter(name=plan_name).first()
            if existing_plan:
                if force:
                    # Atualizar plano existente
                    existing_plan.description = plan_description
                    existing_plan.price = price
                    existing_plan.games.set(Game.objects.filter(console=console, is_active=True))
                    existing_plan.save()
                    self.stdout.write(f'[UPDATED] {plan_name}: {games_count} jogos, R$ {price}/mês')
                else:
                    self.stdout.write(f'[EXISTS] {plan_name}: Plano já existe')
                created_plans.append(existing_plan)
                continue
            
            # Criar novo plano
            plan = Plan.objects.create(
                name=plan_name,
                description=plan_description,
                price=price,
                is_active=True
            )
            
            # Associar jogos do console ao plano
            console_games = Game.objects.filter(console=console, is_active=True)
            plan.games.set(console_games)
            
            self.stdout.write(f'[OK] {plan_name}: {games_count} jogos, R$ {price}/mês')
            created_plans.append(plan)
        
        return created_plans

    def create_general_plans(self, force=False):
        """Cria planos gerais (Básico e Premium)"""
        self.stdout.write('\n=== CRIANDO PLANOS GERAIS ===')
        
        # Plano Básico - Consoles clássicos (NES, Game Boy, GBA, Mega Drive)
        basic_consoles = ['NES', 'Game Boy', 'GBA', 'Mega Drive']
        basic_games = Game.objects.filter(console__in=basic_consoles, is_active=True)
        
        basic_plan = Plan.objects.filter(name='Plano Básico').first()
        if basic_plan:
            if force:
                basic_plan.games.set(basic_games)
                basic_plan.description = f'Acesso a jogos clássicos dos consoles dos anos 80 e 90. Inclui jogos do NES, Game Boy, GBA e Mega Drive. Total: {basic_games.count()} jogos.'
                basic_plan.price = Decimal('19.90')
                basic_plan.save()
                self.stdout.write(f'[UPDATED] Plano Básico: {basic_games.count()} jogos')
            else:
                self.stdout.write(f'[EXISTS] Plano Básico: Já existe')
        else:
            basic_plan = Plan.objects.create(
                name='Plano Básico',
                description=f'Acesso a jogos clássicos dos consoles dos anos 80 e 90. Inclui jogos do NES, Game Boy, GBA e Mega Drive. Total: {basic_games.count()} jogos.',
                price=Decimal('19.90'),
                is_active=True
            )
            basic_plan.games.set(basic_games)
            self.stdout.write(f'[OK] Plano Básico criado: {basic_games.count()} jogos')
        
        # Plano Premium - Todos os jogos
        all_games = Game.objects.filter(is_active=True)
        
        premium_plan = Plan.objects.filter(name='Plano Premium').first()
        if premium_plan:
            if force:
                premium_plan.games.set(all_games)
                premium_plan.description = f'Acesso completo a todos os jogos da plataforma. Inclui jogos de todos os consoles disponíveis. Total: {all_games.count()} jogos.'
                premium_plan.price = Decimal('39.90')
                premium_plan.save()
                self.stdout.write(f'[UPDATED] Plano Premium: {all_games.count()} jogos')
            else:
                self.stdout.write(f'[EXISTS] Plano Premium: Já existe')
        else:
            premium_plan = Plan.objects.create(
                name='Plano Premium',
                description=f'Acesso completo a todos os jogos da plataforma. Inclui jogos de todos os consoles disponíveis. Total: {all_games.count()} jogos.',
                price=Decimal('39.90'),
                is_active=True
            )
            premium_plan.games.set(all_games)
            self.stdout.write(f'[OK] Plano Premium criado: {all_games.count()} jogos')
        
        return [basic_plan, premium_plan]

    def show_statistics(self):
        """Mostra estatísticas dos planos e categorias"""
        self.stdout.write('\n=== ESTATÍSTICAS DOS PLANOS ===')
        
        plans = Plan.objects.filter(is_active=True).order_by('price')
        self.stdout.write(f'Total de planos ativos: {plans.count()}')
        
        self.stdout.write('\n=== DETALHES DOS PLANOS ===')
        for plan in plans:
            games_count = plan.games.count()
            consoles = plan.games.values_list('console', flat=True).distinct()
            console_list = ', '.join(sorted(consoles))
            
            self.stdout.write(f'\n{plan.name}:')
            self.stdout.write(f'  Preço: R$ {plan.price}/mês')
            self.stdout.write(f'  Jogos: {games_count}')
            self.stdout.write(f'  Consoles: {console_list}')
            self.stdout.write(f'  Descrição: {plan.description[:100]}...')
        
        self.stdout.write('\n=== ESTATÍSTICAS DE CATEGORIAS ===')
        categories = Category.objects.all()
        self.stdout.write(f'Total de categorias: {categories.count()}')
        
        self.stdout.write('\n=== JOGOS POR CATEGORIA ===')
        for category in categories:
            game_count = Game.objects.filter(categories=category).count()
            self.stdout.write(f'{category.name}: {game_count} jogos')
        
        games_without_categories = Game.objects.filter(categories__isnull=True).count()
        self.stdout.write(f'\nJogos sem categoria: {games_without_categories}')
        
        self.stdout.write('\n=== BREAKDOWN POR CONSOLE ===')
        consoles = Game.objects.values_list('console', flat=True).distinct().order_by('console')
        
        for console in consoles:
            games_count = Game.objects.filter(console=console, is_active=True).count()
            plan = Plan.objects.filter(name=f'Plano {console}').first()
            plan_price = plan.price if plan else "N/A"
            
            self.stdout.write(f'{console}: {games_count} jogos - Plano: R$ {plan_price}/mês')
