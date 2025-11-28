# Configuração do PWA - Jogos Retro TDE

Este documento descreve a configuração do Progressive Web App (PWA) e como garantir que ele funcione corretamente.

## ✅ Configurações Implementadas

### 1. Manifest.json
- ✅ Arquivo localizado em `static/manifest.json`
- ✅ Configurado com nome, descrição, cores e ícones
- ✅ Linkado no template base (`games/templates/games/base.html`)

### 2. Service Worker
- ✅ Arquivo localizado em `static/service-worker.js`
- ✅ Registrado no template base
- ✅ Configurado para cache offline (Network First strategy)
- ✅ Versão de cache implementada para atualizações

### 3. Botão de Instalação
- ✅ Botão sempre visível quando usuário está logado
- ✅ Script `pwa-install.js` gerencia o evento `beforeinstallprompt`
- ✅ Funciona mesmo sem o evento `beforeinstallprompt` (botão permanece visível)

### 4. Meta Tags
- ✅ Meta tags PWA adicionadas no `<head>`
- ✅ Suporte para iOS (apple-mobile-web-app)
- ✅ Theme color configurado

## 📋 Checklist de Verificação

### Para o PWA funcionar corretamente, verifique:

1. **Ícones do PWA**
   - [ ] Os ícones devem existir em `static/games/images/`
   - [ ] Tamanhos necessários: 192x192 e 512x512 (mínimo)
   - [ ] Use o script `create_pwa_icons.py` para gerar ícones básicos

2. **HTTPS ou localhost**
   - [ ] PWA só funciona em HTTPS ou localhost
   - [ ] Em produção, certifique-se de usar HTTPS

3. **Service Worker**
   - [ ] Verifique no DevTools > Application > Service Workers
   - [ ] Deve estar registrado e ativo
   - [ ] Verifique se há erros no console

4. **Manifest**
   - [ ] Verifique no DevTools > Application > Manifest
   - [ ] Deve estar carregado sem erros
   - [ ] Ícones devem estar acessíveis

## 🚀 Como Criar os Ícones

### Opção 1: Usar o Script Python

```bash
# Instalar dependência
pip install Pillow

# Executar script
python create_pwa_icons.py
```

Isso criará ícones básicos em `static/games/images/`.

### Opção 2: Criar Ícones Manualmente

1. Crie ícones nos tamanhos:
   - 192x192 pixels (mínimo obrigatório)
   - 512x512 pixels (mínimo obrigatório)
   - Opcional: 72x72, 96x96, 128x128, 144x144, 152x152, 384x384

2. Salve em `static/games/images/` com os nomes:
   - `icon-192x192.png`
   - `icon-512x512.png`
   - etc.

3. Use ferramentas online como:
   - [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
   - [RealFaviconGenerator](https://realfavicongenerator.net/)

## 🧪 Como Testar o PWA

### 1. Verificar no Chrome DevTools

1. Abra o DevTools (F12)
2. Vá para a aba **Application**
3. Verifique:
   - **Manifest**: Deve mostrar o manifest.json carregado
   - **Service Workers**: Deve estar registrado e ativo
   - **Storage**: Deve mostrar os caches criados

### 2. Testar Instalação

1. No Chrome, verifique se aparece o ícone de instalação na barra de endereços
2. Ou use o botão "Instalar App" no menu de navegação (quando logado)
3. O prompt de instalação deve aparecer

### 3. Testar Offline

1. No DevTools, vá para **Network**
2. Marque **Offline**
3. Recarregue a página
4. A página deve carregar do cache

### 4. Verificar Critérios de Instalabilidade

O Chrome mostra o PWA como instalável se:
- ✅ Tem um manifest.json válido
- ✅ Tem um service worker registrado
- ✅ Está servido via HTTPS (ou localhost)
- ✅ Tem pelo menos um ícone de 192x192 e 512x512
- ✅ O manifest tem `start_url` e `display` configurados

## 🔧 Solução de Problemas

### Botão de Instalação Não Aparece

1. **Verifique se está logado**: O botão só aparece para usuários autenticados
2. **Verifique o console**: Procure por erros do service worker ou manifest
3. **Verifique se já está instalado**: Se o PWA já estiver instalado, o botão não aparece
4. **Limpe o cache**: Tente limpar o cache do navegador e recarregar

### Service Worker Não Registra

1. **Verifique o caminho**: O service worker deve estar em `static/service-worker.js`
2. **Verifique HTTPS**: Service workers só funcionam em HTTPS ou localhost
3. **Verifique erros no console**: Pode haver erros de sintaxe no service worker

### Manifest Não Carrega

1. **Verifique o caminho**: O manifest deve estar em `static/manifest.json`
2. **Verifique os ícones**: Se os ícones não existirem, o manifest pode falhar
3. **Verifique JSON válido**: Use um validador JSON para verificar sintaxe

### PWA Não Funciona Offline

1. **Verifique o service worker**: Deve estar ativo
2. **Verifique o cache**: Veja se os arquivos estão sendo cacheados
3. **Teste em modo offline**: Use o DevTools para simular offline

## 📝 Notas Importantes

1. **Ícones são obrigatórios**: Sem ícones válidos, o PWA pode não ser instalável
2. **HTTPS é obrigatório**: Em produção, use sempre HTTPS
3. **Service Worker atualiza**: O service worker verifica atualizações automaticamente
4. **Cache versionado**: O cache usa versões para facilitar atualizações

## 🎯 Próximos Passos

1. Execute `python create_pwa_icons.py` para criar os ícones
2. Teste o PWA em localhost
3. Verifique no DevTools se tudo está funcionando
4. Em produção, certifique-se de usar HTTPS
5. Teste a instalação em diferentes navegadores

## 📚 Recursos Adicionais

- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev - PWA](https://web.dev/progressive-web-apps/)
- [Chrome - Add to Home Screen](https://developer.chrome.com/docs/lighthouse/pwa/add-to-home-screen/)

