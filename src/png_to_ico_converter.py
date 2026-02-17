"""
PNG → ICO Konverter für Windows-Icons
=====================================
Zweck:
Dieses Skript erzeugt aus einer vorhandenen PNG-Datei (icon.png)
eine Windows-kompatible .ico-Datei mit mehreren eingebetteten Auflösungen.

Funktionsweise:
- Öffnet das PNG-Bild mit Pillow (PIL).
- Konvertiert es nach RGBA, um Transparenz sicherzustellen.
- Speichert es als .ico-Datei mit mehreren Größenstufen.

Warum mehrere Größen?
Windows verwendet je nach Kontext unterschiedliche Icon-Größen
(z. B. Explorer, Taskleiste, Desktop, hohe DPI-Skalierung).
Durch die Angabe mehrerer Auflösungen bleibt das Icon scharf
und wird nicht unsauber hoch- oder herunterskaliert.

Ziel:
Erstellung eines skalierbaren, professionellen Windows-Icons
für Anwendungen oder ausführbare Dateien.



PNG → ICO Converter for Windows Icons
=====================================
Purpose:
This script converts an existing PNG file (icon.png)
into a Windows-compatible .ico file containing multiple embedded resolutions.

How it works:
- Opens the PNG image using Pillow (PIL).
- Converts it to RGBA to preserve transparency.
- Saves it as an .ico file with multiple size variants.

Why multiple sizes?
Windows selects different icon sizes depending on context
(e.g., file explorer, taskbar, desktop, high DPI scaling).
Providing multiple resolutions ensures sharp rendering
without blurry scaling artifacts.

Goal:
Generate a scalable, professional Windows icon
for applications or executable files.
"""





from PIL import Image

img = Image.open("icon.png").convert("RGBA")

img.save(
    "icon.ico",
    sizes=[
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ]
)
