// PWA Install Manager - Mostra prompt de instalação apenas quando usuário está logado
// Este script gerencia o evento beforeinstallprompt e permite instalar o PWA

let deferredPrompt;
let installButton = null;

// Verificar se o usuário está logado (via variável global definida no template)
function isUserLoggedIn() {
    // Verificar variável global definida no template Django
    if (typeof window.USER_IS_AUTHENTICATED !== 'undefined') {
        return window.USER_IS_AUTHENTICATED === true;
    }
    
    // Fallback: verificar cookie de sessão do Django
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name] = cookie.trim().split('=');
        if (name === 'sessionid') {
            return true;
        }
    }
    return false;
}

// Função para mostrar o botão de instalação
function showInstallButton() {
    if (installButton) {
        installButton.style.display = 'block';
    }
}

// Função para esconder o botão de instalação
function hideInstallButton() {
    if (installButton) {
        installButton.style.display = 'none';
    }
}

// Função para verificar se o PWA já está instalado
function isPWAInstalled() {
    // Verificar se está rodando em modo standalone (instalado)
    if (window.matchMedia('(display-mode: standalone)').matches) {
        return true;
    }
    
    // Verificar se está em modo standalone no iOS
    if (window.navigator.standalone === true) {
        return true;
    }
    
    return false;
}

// Evento beforeinstallprompt - disparado quando o navegador pode mostrar o prompt de instalação
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA Install] beforeinstallprompt disparado');
    
    // Só processar se o usuário estiver logado
    if (!isUserLoggedIn()) {
        console.log('[PWA Install] Usuário não está logado, ignorando prompt');
        return;
    }
    
    // Prevenir o prompt padrão do navegador
    e.preventDefault();
    
    // Salvar o evento para usar depois
    deferredPrompt = e;
    
    // Mostrar o botão de instalação
    showInstallButton();
    
    // Mostrar notificação toast se disponível
    showInstallNotification();
});

// Função para mostrar notificação de instalação disponível
function showInstallNotification() {
    // Verificar se já existe uma notificação
    if (document.getElementById('pwa-install-notification')) {
        return;
    }
    
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.id = 'pwa-install-notification';
    notification.className = 'pwa-install-notification';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-download me-2"></i>
            <span>Instale o app para uma experiência melhor!</span>
        </div>
        <button class="btn btn-sm btn-primary ms-3" onclick="installPWA()">
            Instalar
        </button>
        <button type="button" class="btn-close ms-2" onclick="dismissInstallNotification()"></button>
    `;
    
    // Adicionar estilos inline se necessário
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        max-width: 400px;
        animation: slideInUp 0.3s ease-out;
    `;
    
    // Adicionar ao body
    document.body.appendChild(notification);
    
    // Auto-dismiss após 10 segundos
    setTimeout(() => {
        dismissInstallNotification();
    }, 10000);
}

// Função para fechar a notificação
function dismissInstallNotification() {
    const notification = document.getElementById('pwa-install-notification');
    if (notification) {
        notification.style.animation = 'slideOutDown 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}

// Função principal para instalar o PWA
async function installPWA() {
    if (!deferredPrompt) {
        console.log('[PWA Install] Nenhum prompt de instalação disponível');
        
        // Se não houver prompt, pode ser que o PWA já esteja instalado
        if (isPWAInstalled()) {
            alert('O app já está instalado!');
        } else {
            alert('Instalação não disponível no momento. Tente novamente mais tarde.');
        }
        return;
    }
    
    // Mostrar o prompt de instalação
    deferredPrompt.prompt();
    
    // Aguardar a resposta do usuário
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log('[PWA Install] Resultado da instalação:', outcome);
    
    if (outcome === 'accepted') {
        console.log('[PWA Install] Usuário aceitou a instalação');
        showInstallSuccessMessage();
    } else {
        console.log('[PWA Install] Usuário rejeitou a instalação');
    }
    
    // Limpar o prompt
    deferredPrompt = null;
    
    // Esconder o botão de instalação
    hideInstallButton();
    
    // Fechar a notificação
    dismissInstallNotification();
}

// Função para mostrar mensagem de sucesso
function showInstallSuccessMessage() {
    // Criar mensagem de sucesso
    const message = document.createElement('div');
    message.className = 'pwa-install-success';
    message.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-check-circle me-2"></i>
            <span>App instalado com sucesso!</span>
        </div>
    `;
    
    message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(message);
    
    // Remover após 3 segundos
    setTimeout(() => {
        message.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            message.remove();
        }, 300);
    }, 3000);
}

// Evento quando o PWA é instalado (appinstalled)
window.addEventListener('appinstalled', () => {
    console.log('[PWA Install] PWA foi instalado');
    deferredPrompt = null;
    hideInstallButton();
    dismissInstallNotification();
});

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Verificar se o usuário está logado
    if (!isUserLoggedIn()) {
        console.log('[PWA Install] Usuário não está logado, funcionalidade de instalação desabilitada');
        return;
    }
    
    // Verificar se já está instalado
    if (isPWAInstalled()) {
        console.log('[PWA Install] PWA já está instalado');
        hideInstallButton();
        return;
    }
    
    // Procurar botão de instalação no DOM
    installButton = document.getElementById('pwa-install-button');
    
    if (installButton) {
        installButton.addEventListener('click', installPWA);
        // Inicialmente escondido, será mostrado quando beforeinstallprompt disparar
        hideInstallButton();
    }
    
    console.log('[PWA Install] Sistema de instalação PWA inicializado');
});

// Adicionar estilos CSS para animações (se não existirem)
if (!document.getElementById('pwa-install-styles')) {
    const style = document.createElement('style');
    style.id = 'pwa-install-styles';
    style.textContent = `
        @keyframes slideInUp {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutDown {
            from {
                transform: translateY(0);
                opacity: 1;
            }
            to {
                transform: translateY(100%);
                opacity: 0;
            }
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

