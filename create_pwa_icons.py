#!/usr/bin/env python3
"""
Script para criar ícones básicos do PWA.
Este script cria ícones PNG simples usando Pillow (PIL).

Requisitos:
    pip install Pillow

Uso:
    python create_pwa_icons.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Erro: Pillow não está instalado.")
    print("Instale com: pip install Pillow")
    exit(1)

# Cores do tema
BACKGROUND_COLOR = (26, 26, 46)  # #1a1a2e
TEXT_COLOR = (255, 255, 255)  # Branco
ACCENT_COLOR = (102, 126, 234)  # #667eea

# Tamanhos de ícones necessários
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_icon(size):
    """Cria um ícone do tamanho especificado."""
    # Criar imagem com fundo
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Desenhar círculo de fundo com cor de destaque
    margin = size // 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=ACCENT_COLOR,
        outline=TEXT_COLOR,
        width=max(2, size // 64)
    )
    
    # Desenhar símbolo de gamepad (simples)
    center = size // 2
    symbol_size = size // 3
    
    # Círculo central (botão)
    draw.ellipse(
        [center - symbol_size // 2, center - symbol_size // 2,
         center + symbol_size // 2, center + symbol_size // 2],
        fill=TEXT_COLOR
    )
    
    # Tentar adicionar texto "JR" (Jogos Retro) se o tamanho permitir
    if size >= 128:
        try:
            # Tentar usar fonte padrão
            font_size = size // 4
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                font = ImageFont.load_default()
        
        # Desenhar "JR" no centro
        text = "JR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center - text_width // 2
        text_y = center - text_height // 2
        
        draw.text((text_x, text_y), text, fill=ACCENT_COLOR, font=font)
    
    return img

def main():
    """Função principal."""
    # Diretório de destino
    output_dir = "static/games/images"
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    print("Criando ícones do PWA...")
    
    # Criar cada tamanho de ícone
    for size in ICON_SIZES:
        icon = create_icon(size)
        filename = f"{output_dir}/icon-{size}x{size}.png"
        icon.save(filename, "PNG")
        print(f"✓ Criado: {filename} ({size}x{size})")
    
    print("\n✓ Todos os ícones foram criados com sucesso!")
    print(f"Localização: {output_dir}/")
    print("\nNota: Se você quiser ícones personalizados, substitua os arquivos PNG criados.")

if __name__ == "__main__":
    main()

