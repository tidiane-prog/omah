#!/usr/bin/env python3
"""
Script pour générer les assets de l'application.
Crée l'icône et le splash screen si PIL est installé.
"""

import os

def create_assets():
    """Crée les assets de l'application."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer le dossier assets
        os.makedirs('assets', exist_ok=True)
        
        # === ICÔNE (512x512) ===
        print("Création de l'icône...")
        icon_size = 512
        icon = Image.new('RGBA', (icon_size, icon_size), (26, 95, 122, 255))
        draw = ImageDraw.Draw(icon)
        
        # Fond circulaire
        margin = 20
        draw.ellipse(
            [margin, margin, icon_size - margin, icon_size - margin],
            fill=(45, 106, 79, 255)
        )
        
        # Bouclier
        center = icon_size // 2
        shield_points = [
            (center, center - 120),
            (center - 80, center - 60),
            (center - 80, center + 40),
            (center, center + 100),
            (center + 80, center + 40),
            (center + 80, center - 60),
        ]
        draw.polygon(shield_points, fill=(26, 95, 122, 255))
        
        # Texte
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        draw.text((center - 45, center - 50), "EN", fill=(255, 255, 255, 255), font=font)
        
        icon.save('assets/icon.png')
        print("✓ Icône créée: assets/icon.png")
        
        # === SPLASH SCREEN (1080x1920) ===
        print("Création du splash screen...")
        splash_size = (1080, 1920)
        splash = Image.new('RGBA', splash_size, (14, 17, 23, 255))
        draw = ImageDraw.Draw(splash)
        
        # Logo central
        logo_y = 700
        draw.rounded_rectangle(
            [340, logo_y, 740, logo_y + 400],
            radius=20,
            fill=(26, 95, 122, 255)
        )
        
        # Texte du logo
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        draw.text((380, logo_y + 100), "ELITE", fill=(255, 255, 255, 255), font=font_large)
        draw.text((350, logo_y + 200), "NEURAL", fill=(255, 193, 7, 255), font=font_large)
        draw.text((340, logo_y + 300), "EVOLVE v8.0", fill=(200, 200, 200, 255), font=font_small)
        
        # Bas de page
        draw.text((350, 1700), "Chargement...", fill=(150, 150, 150, 255), font=font_small)
        
        splash.save('assets/splash.png')
        print("✓ Splash screen créé: assets/splash.png")
        
        # === NOTIFICATION ICON ===
        print("Création de l'icône de notification...")
        notif_size = 96
        notif = Image.new('RGBA', (notif_size, notif_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(notif)
        
        draw.ellipse([10, 10, notif_size - 10, notif_size - 10], fill=(26, 95, 122, 255))
        draw.text((30, 30), "EN", fill=(255, 255, 255, 255))
        
        notif.save('assets/notification.png')
        print("✓ Icône notification créée: assets/notification.png")
        
        print("\n✅ Tous les assets ont été créés avec succès!")
        
    except ImportError:
        print("❌ PIL (Pillow) n'est pas installé.")
        print("Installez avec: pip install pillow")
        
        # Créer des fichiers placeholder
        os.makedirs('assets', exist_ok=True)
        
        # Créer des fichiers vides comme placeholders
        open('assets/icon.png', 'w').close()
        open('assets/splash.png', 'w').close()
        
        print("⚠️  Des fichiers placeholder ont été créés.")
        print("   Remplacez-les par de vraies images PNG.")


if __name__ == '__main__':
    create_assets()
