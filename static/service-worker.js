// Service Worker para PWA - Jogos Retro TDE
// Cache básico para funcionamento offline da interface

const CACHE_VERSION = 'v2';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`;

// Arquivos estáticos para cache (app shell)
const STATIC_FILES = [
    '/',
    '/catalog/',
    '/static/css/modern-retro.css',
    '/static/manifest.json',
    '/static/games/js/pwa-install.js',
    // Adicionar outros arquivos estáticos conforme necessário
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Instalando versão', CACHE_VERSION);
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[Service Worker] Cacheando arquivos estáticos');
                // Cache apenas arquivos críticos na instalação
                return cache.addAll(STATIC_FILES).catch((error) => {
                    console.log('[Service Worker] Erro ao cachear arquivos:', error);
                    // Continuar mesmo se alguns arquivos falharem
                });
            })
            .then(() => {
                // Forçar ativação imediata
                return self.skipWaiting();
            })
    );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Ativando versão', CACHE_VERSION);
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    // Remover caches antigos
                    if (!cacheName.includes(CACHE_VERSION)) {
                        console.log('[Service Worker] Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            // Assumir controle imediato de todas as páginas
            return self.clients.claim();
        })
    );
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
                    const acceptHeader = request.headers.get('accept') || '';
                    if (acceptHeader.includes('text/html')) {
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





