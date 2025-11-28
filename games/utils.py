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
        logger.info(f"DEBUG - Iniciando extração de embed URL de: {game_url}")
        print(f"DEBUG - Iniciando extração de embed URL de: {game_url}")
        
        response = requests.get(game_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        logger.info(f"DEBUG - Status da resposta: {response.status_code}")
        logger.info(f"DEBUG - Content-Type: {response.headers.get('content-type', 'N/A')}")
        logger.info(f"DEBUG - Tamanho do HTML: {len(response.text)} caracteres")
        logger.info(f"DEBUG - Primeiros 200 caracteres da resposta: {response.text[:200]}")
        print(f"DEBUG - Status da resposta: {response.status_code}")
        print(f"DEBUG - Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"DEBUG - Tamanho do HTML: {len(response.text)} caracteres")
        print(f"DEBUG - Primeiros 200 caracteres da resposta: {response.text[:200]}")
        
        # Verificar se a página está offline ou retornou erro
        if 'offline' in response.text.lower() or 'Offline' in response.text:
            logger.warning(f"DEBUG - Página parece estar offline ou retornou mensagem de erro")
            print("DEBUG - Página parece estar offline ou retornou mensagem de erro")
            raise Exception("A página do embed está offline ou inacessível")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar textarea readonly
        textarea = soup.find('textarea', {'readonly': True})
        
        if textarea:
            textarea_content = textarea.get_text(strip=True)
            
            logger.info(f"DEBUG - Textarea readonly encontrado!")
            logger.info(f"DEBUG - Conteúdo do textarea (primeiros 500 caracteres): {textarea_content[:500]}")
            logger.info(f"DEBUG - Conteúdo completo do textarea: {textarea_content}")
            print("DEBUG - Textarea readonly encontrado!")
            print(f"DEBUG - Conteúdo do textarea (primeiros 500 caracteres): {textarea_content[:500]}")
            print(f"DEBUG - Conteúdo completo do textarea: {textarea_content}")
            
            # Extrair URL do conteúdo do textarea
            import re
            # Procurar por URLs no formato http:// ou https://
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls = re.findall(url_pattern, textarea_content)
            
            logger.info(f"DEBUG - URLs encontradas no textarea: {urls}")
            print(f"DEBUG - URLs encontradas no textarea: {urls}")
            
            if urls:
                # Retornar a primeira URL encontrada (geralmente é a do embed)
                embed_url = urls[0]
                # Limpar a URL se tiver caracteres extras
                embed_url = embed_url.rstrip('.,;!?')
                logger.info(f"DEBUG - URL do embed extraída e limpa: {embed_url}")
                print(f"DEBUG - URL do embed extraída e limpa: {embed_url}")
                return embed_url
            else:
                logger.warning(f"DEBUG - Nenhuma URL encontrada no conteúdo do textarea")
                print("DEBUG - Nenhuma URL encontrada no conteúdo do textarea")
        else:
            logger.warning(f"DEBUG - Textarea readonly NÃO encontrado na página")
            print("DEBUG - Textarea readonly NÃO encontrado na página")
            
            # Debug: mostrar todos os textareas encontrados
            all_textareas = soup.find_all('textarea')
            logger.info(f"DEBUG - Total de textareas encontrados na página: {len(all_textareas)}")
            print(f"DEBUG - Total de textareas encontrados na página: {len(all_textareas)}")
            
            for idx, ta in enumerate(all_textareas):
                readonly_attr = ta.get('readonly')
                ta_id = ta.get('id', 'sem id')
                ta_class = ta.get('class', [])
                logger.info(f"DEBUG - Textarea {idx + 1}: id={ta_id}, readonly={readonly_attr}, class={ta_class}")
                print(f"DEBUG - Textarea {idx + 1}: id={ta_id}, readonly={readonly_attr}, class={ta_class}")
        
        # Fallback: tentar construir URL de embed baseado na URL do jogo
        logger.info(f"DEBUG - Tentando fallback baseado na URL")
        print("DEBUG - Tentando fallback baseado na URL")
        if '/play/' in game_url:
            fallback_url = game_url.replace('/play/', '/embed/')
            logger.info(f"DEBUG - Fallback URL (play->embed): {fallback_url}")
            print(f"DEBUG - Fallback URL (play->embed): {fallback_url}")
            return fallback_url
        elif '/embed/' in game_url:
            logger.info(f"DEBUG - Fallback URL (já é embed): {game_url}")
            print(f"DEBUG - Fallback URL (já é embed): {game_url}")
            return game_url
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"DEBUG - Erro ao extrair URL do embed de {game_url}: {str(e)}")
        logger.error(f"DEBUG - Traceback completo:\n{error_trace}")
        print(f"DEBUG - Erro ao extrair URL do embed de {game_url}: {str(e)}")
        print(f"DEBUG - Traceback completo:\n{error_trace}")
    
    logger.warning(f"DEBUG - Retornando None - não foi possível extrair URL")
    print("DEBUG - Retornando None - não foi possível extrair URL")
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
            
            # Buscar URL do embed na página do jogo
            embed_url = _extract_embed_url(game_url, headers)
            
            game_data = {
                'title': title[:100],  # Limitar tamanho do título
                'image_url': image_url,
                'game_url': game_url,
                'embed_url': embed_url or game_url,
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
                        
                        # Buscar URL do embed na página do jogo
                        embed_url = _extract_embed_url(game_url, headers)
                        
                        game_data = {
                            'title': title[:100],
                            'image_url': image_url,
                            'game_url': game_url,
                            'embed_url': embed_url or game_url,
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

