"""
Utilitários para busca e processamento de jogos no retrogames.cc
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import logging

logger = logging.getLogger(__name__)


def _extract_embed_url(game_url, headers):
    """
    Extrai a URL do embed da página do jogo buscando o textarea readonly.
    
    Args:
        game_url (str): URL da página do jogo
        headers (dict): Headers HTTP para a requisição
    
    Returns:
        str: URL do embed ou None se não encontrado
    """
    try:
        response = requests.get(game_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        if 'offline' in response.text.lower() or 'Offline' in response.text:
            raise Exception("A página do embed está offline ou inacessível")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar textarea readonly
        all_textareas = soup.find_all('textarea')
        textarea = None
        
        # Tentar diferentes formas de buscar o textarea readonly
        textarea = soup.find('textarea', {'readonly': True})
        if not textarea:
            textarea = soup.find('textarea', {'readonly': ''})
        if not textarea:
            for ta in all_textareas:
                if 'readonly' in ta.attrs:
                    textarea = ta
                    break
        if not textarea:
            try:
                textarea = soup.select_one('textarea[readonly]')
            except:
                pass
        
        if textarea:
            # Obter o texto completo do textarea (conteúdo interno HTML)
            textarea_content = textarea.decode_contents() if hasattr(textarea, 'decode_contents') else ''
            
            if not textarea_content or not textarea_content.strip():
                textarea_content = ''.join(str(child) for child in textarea.children) if hasattr(textarea, 'children') else ''
            
            if not textarea_content or not textarea_content.strip():
                textarea_content = textarea.string or ''
            
            if textarea_content and textarea_content.strip():
                return textarea_content.strip()
        
        # Fallback: tentar construir URL de embed baseado na URL do jogo
        if '/play/' in game_url:
            return game_url.replace('/play/', '/embed/')
        elif '/embed/' in game_url:
            return game_url
        
    except Exception as e:
        logger.warning(f"Erro ao extrair conteúdo do embed de {game_url}: {str(e)}")
    
    return None


def search_games_on_retrogames(query, max_results=5):
    """
    Busca jogos no site retrogames.cc e retorna os primeiros resultados.
    
    Args:
        query (str): Termo de busca (nome do jogo)
        max_results (int): Número máximo de resultados a retornar (padrão: 5)
    
    Returns:
        list: Lista de dicionários contendo:
            - title: Título do jogo
            - image_url: URL da imagem do jogo
            - game_url: URL completa da página do jogo no retrogames.cc
            - embed_url: URL do embed do jogo (se disponível)
    """
    results = []
    
    try:
        # URL de busca no retrogames.cc
        # Formato correto: https://www.retrogames.cc/search?q={termo}
        encoded_query = quote_plus(query)
        search_url = f"https://www.retrogames.cc/search?q={encoded_query}"
        
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info(f"Buscando jogos no retrogames.cc com query: {query}")
        
        # Fazer requisição GET
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estratégias para encontrar os resultados de jogos
        # Estratégia 1: Buscar por links que contenham imagens de jogos
        game_links = soup.find_all('a', href=True)
        
        for link in game_links:
            if len(results) >= max_results:
                break
            
            # Ignorar elementos com title="Retro Games"
            link_title = link.get('title', '')
            img = link.find('img')
            img_title = img.get('title', '') if img else ''
            
            if link_title == 'Retro Games' or img_title == 'Retro Games':
                continue
            
            # Verificar se o link contém uma imagem
            if not img:
                continue
            
            # Obter URL da imagem
            img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not img_src:
                continue
            
            # Obter URL do jogo
            game_href = link.get('href', '')
            if not game_href:
                continue
            
            # Construir URL completa se for relativa
            if game_href.startswith('/'):
                game_url = urljoin('https://www.retrogames.cc', game_href)
            elif game_href.startswith('http'):
                game_url = game_href
            else:
                continue
            
            # Obter título do jogo
            title = img.get('alt') or img.get('title') or link.get('title') or ''
            if not title:
                # Tentar extrair do texto do link
                title = link.get_text(strip=True)
            
            # Se ainda não tiver título, usar parte da URL
            if not title:
                parsed_url = urlparse(game_url)
                title = parsed_url.path.split('/')[-1].replace('-', ' ').title()
            
            # Verificar se já não adicionamos este jogo (evitar duplicatas)
            if any(r['game_url'] == game_url for r in results):
                continue
            
            # Construir URL da imagem completa se for relativa
            if img_src.startswith('/'):
                image_url = urljoin('https://www.retrogames.cc', img_src)
            elif img_src.startswith('http'):
                image_url = img_src
            else:
                image_url = urljoin('https://www.retrogames.cc', img_src)
            
            # Construir URL do embed baseado na URL do jogo
            # Não buscar o conteúdo do textarea aqui, apenas a URL
            if '/play/' in game_url:
                embed_url = game_url.replace('/play/', '/embed/')
            elif '/embed/' in game_url:
                embed_url = game_url
            else:
                # Tentar construir URL de embed
                embed_url = game_url.replace('/game/', '/embed/').replace('/play/', '/embed/')
                if '/embed/' not in embed_url:
                    embed_url = game_url
            
            game_data = {
                'title': title[:100],  # Limitar tamanho do título
                'image_url': image_url,
                'game_url': game_url,
                'embed_url': embed_url,
            }
            
            results.append(game_data)
            logger.info(f"Jogo encontrado: {title} - {game_url}")
        
        # Se não encontrou resultados suficientes, tentar estratégia alternativa
        if len(results) < max_results:
            # Estratégia 2: Buscar por divs com classes comuns de cards de jogos
            game_cards = soup.find_all(['div', 'article', 'section'], class_=lambda x: x and (
                'game' in x.lower() or 
                'card' in x.lower() or 
                'item' in x.lower()
            ))
            
            for card in game_cards:
                if len(results) >= max_results:
                    break
                
                # Buscar link e imagem dentro do card
                link = card.find('a', href=True)
                img = card.find('img')
                
                if link and img:
                    # Ignorar elementos com title="Retro Games"
                    link_title = link.get('title', '')
                    img_title = img.get('title', '')
                    card_title = card.get('title', '')
                    
                    if link_title == 'Retro Games' or img_title == 'Retro Games' or card_title == 'Retro Games':
                        continue
                    img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    game_href = link.get('href', '')
                    
                    if img_src and game_href:
                        # Construir URLs completas
                        if game_href.startswith('/'):
                            game_url = urljoin('https://www.retrogames.cc', game_href)
                        elif game_href.startswith('http'):
                            game_url = game_href
                        else:
                            continue
                        
                        if img_src.startswith('/'):
                            image_url = urljoin('https://www.retrogames.cc', img_src)
                        elif img_src.startswith('http'):
                            image_url = img_src
                        else:
                            image_url = urljoin('https://www.retrogames.cc', img_src)
                        
                        title = img.get('alt') or img.get('title') or link.get('title') or link.get_text(strip=True)
                        if not title:
                            parsed_url = urlparse(game_url)
                            title = parsed_url.path.split('/')[-1].replace('-', ' ').title()
                        
                        # Verificar duplicatas
                        if any(r['game_url'] == game_url for r in results):
                            continue
                        
                        # Construir URL do embed baseado na URL do jogo
                        if '/play/' in game_url:
                            embed_url = game_url.replace('/play/', '/embed/')
                        elif '/embed/' in game_url:
                            embed_url = game_url
                        else:
                            embed_url = game_url.replace('/game/', '/embed/').replace('/play/', '/embed/')
                            if '/embed/' not in embed_url:
                                embed_url = game_url
                        
                        game_data = {
                            'title': title[:100],
                            'image_url': image_url,
                            'game_url': game_url,
                            'embed_url': embed_url,
                        }
                        
                        results.append(game_data)
                        logger.info(f"Jogo encontrado (estratégia 2): {title} - {game_url}")
        
        logger.info(f"Total de jogos encontrados: {len(results)}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao fazer requisição para retrogames.cc: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro ao processar resultados do retrogames.cc: {str(e)}")
        raise
    
    return results[:max_results]


def search_multiple_games(game_names, max_results_per_game=5):
    """
    Busca múltiplos jogos e retorna todos os resultados.
    
    Args:
        game_names (list): Lista de nomes de jogos para buscar
        max_results_per_game (int): Número máximo de resultados por jogo
    
    Returns:
        list: Lista de todos os resultados encontrados
    """
    all_results = []
    
    for game_name in game_names:
        try:
            results = search_games_on_retrogames(game_name, max_results_per_game)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Erro ao buscar jogo '{game_name}': {str(e)}")
            continue
    
    # Remover duplicatas baseado na URL do jogo
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result['game_url'] not in seen_urls:
            seen_urls.add(result['game_url'])
            unique_results.append(result)
    
    return unique_results

