// Service Worker para PWA - Jogos Retro TDE
// Cache básico para funcionamento offline da interface

const CACHE_NAME = 'jogos-retro-tde-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

// Arquivos estáticos para cache (app shell)
const STATIC_FILES = [
    '/',
    '/catalog/',
    '/static/css/modern-retro.css',
    '/static/manifest.json',
    // Adicionar outros arquivos estáticos conforme necessário
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Instalando...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[Service Worker] Cacheando arquivos estáticos');
                // Cache apenas arquivos críticos na instalação
                return cache.addAll([
                    '/',
                    '/static/css/modern-retro.css',
                ]).catch((error) => {
                    console.log('[Service Worker] Erro ao cachear arquivos:', error);
                });
            })
    );
    
    // Forçar ativação imediata
    self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Ativando...');
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    // Remover caches antigos
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('[Service Worker] Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    // Assumir controle imediato de todas as páginas
    return self.clients.claim();
});

// Interceptação de requisições (estrategia: Network First, fallback para Cache)
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignorar requisições para o emulador (retrogames.cc) - não pode ser cacheado
    if (url.hostname.includes('retrogames.cc')) {
        // Sempre buscar da rede para o emulador
        return;
    }
    
    // Ignorar requisições não-GET
    if (request.method !== 'GET') {
        return;
    }
    
    // Estratégia: Network First com fallback para Cache
    event.respondWith(
        fetch(request)
            .then((response) => {
                // Clonar a resposta para poder usar no cache
                const responseClone = response.clone();
                
                // Cachear respostas bem-sucedidas
                if (response.status === 200) {
                    caches.open(DYNAMIC_CACHE).then((cache) => {
                        cache.put(request, responseClone);
                    });
                }
                
                return response;
            })
            .catch(() => {
                // Se a rede falhar, tentar buscar do cache
                return caches.match(request).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    
                    // Se não estiver no cache e for uma página HTML, retornar página offline
                    if (request.headers.get('accept').includes('text/html')) {
                        return caches.match('/').then((offlinePage) => {
                            return offlinePage || new Response('Offline - Conecte-se à internet', {
                                status: 503,
                                headers: { 'Content-Type': 'text/plain' }
                            });
                        });
                    }
                    
                    // Para outros tipos de arquivo, retornar erro
                    return new Response('Recurso não disponível offline', {
                        status: 503,
                        headers: { 'Content-Type': 'text/plain' }
                    });
                });
            })
    );
});

// Mensagens do cliente (para atualização de cache, etc.)
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        caches.delete(STATIC_CACHE);
        caches.delete(DYNAMIC_CACHE);
    }
});





