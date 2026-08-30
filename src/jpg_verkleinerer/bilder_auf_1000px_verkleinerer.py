import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps
import tkinter as tk
from tkinter import messagebox


# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

MAX_KANTE = 1000
JPEG_QUALITAET = 90


# ------------------------------------------------------------
# Arbeitsordner bestimmen
# ------------------------------------------------------------

if getattr(sys, "frozen", False):
    # Als PyInstaller-EXE gestartet:
    # Ordner, in dem die EXE liegt
    ORDNER = Path(sys.executable).resolve().parent
else:
    # Als normales Python-Skript gestartet:
    # Ordner, in dem die PY-Datei liegt
    ORDNER = Path(__file__).resolve().parent


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------

def format_speicherplatz(bytes_wert):
    """Formatiert Bytes lesbar als KB, MB oder GB."""

    if bytes_wert < 1024:
        return f"{bytes_wert} Byte"

    elif bytes_wert < 1024 ** 2:
        return f"{bytes_wert / 1024:.1f} KB"

    elif bytes_wert < 1024 ** 3:
        return f"{bytes_wert / 1024 ** 2:.2f} MB"

    else:
        return f"{bytes_wert / 1024 ** 3:.2f} GB"


def bild_verkleinern(dateipfad):
    """
    Verkleinert ein JPEG, falls seine längste Kante größer
    als MAX_KANTE ist.

    Rückgabe:
        ("bearbeitet", eingesparte_bytes)
        ("geskippt", 0)
    """

    alte_dateigroesse = dateipfad.stat().st_size

    with Image.open(dateipfad) as img:

        # EXIF-Drehung berücksichtigen
        # Wichtig insbesondere bei Smartphone-Fotos
        img = ImageOps.exif_transpose(img)

        breite, hoehe = img.size
        laengste_kante = max(breite, hoehe)

        # Bereits klein genug
        if laengste_kante <= MAX_KANTE:
            return "geskippt", 0

        # Skalierungsfaktor
        faktor = MAX_KANTE / laengste_kante

        neue_breite = round(breite * faktor)
        neue_hoehe = round(hoehe * faktor)

        # Hochwertiges Verkleinern
        img = img.resize(
            (neue_breite, neue_hoehe),
            Image.Resampling.LANCZOS
        )

        # JPEG unterstützt kein RGBA
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Metadaten möglichst erhalten
        exif = img.getexif()
        icc_profile = img.info.get("icc_profile")

        # Erst temporär speichern.
        # Das Original wird erst ersetzt, wenn das Speichern
        # erfolgreich abgeschlossen wurde.
        fd, temp_name = tempfile.mkstemp(
            suffix=".jpg",
            dir=dateipfad.parent
        )

        os.close(fd)

        temp_pfad = Path(temp_name)

        try:

            save_kwargs = {
                "format": "JPEG",
                "quality": JPEG_QUALITAET,
                "optimize": True,
            }

            if exif:
                save_kwargs["exif"] = exif.tobytes()

            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile

            img.save(temp_pfad, **save_kwargs)

            # Original ersetzen
            os.replace(temp_pfad, dateipfad)

        finally:

            # Falls beim Speichern etwas schiefging
            if temp_pfad.exists():
                temp_pfad.unlink()

    neue_dateigroesse = dateipfad.stat().st_size

    eingespart = max(
        0,
        alte_dateigroesse - neue_dateigroesse
    )

    return "bearbeitet", eingespart


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():

    # Unsichtbares tkinter-Hauptfenster
    root = tk.Tk()
    root.withdraw()

    # Alle JPG/JPEG-Dateien im selben Ordner suchen
    bilder = sorted(
        datei
        for datei in ORDNER.iterdir()
        if datei.is_file()
        and datei.suffix.lower() in (".jpg", ".jpeg")
    )

    # --------------------------------------------------------
    # Keine Bilder gefunden
    # --------------------------------------------------------

    if not bilder:

        messagebox.showinfo(
            "JPEG-Verkleinerung",
            "In diesem Ordner wurden keine JPEG-Dateien gefunden."
        )

        root.destroy()
        return


    # --------------------------------------------------------
    # Vorab prüfen, wie viele Bilder tatsächlich zu groß sind
    # --------------------------------------------------------

    zu_gross = 0
    bereits_klein = 0
    nicht_lesbar = 0

    for datei in bilder:

        try:

            with Image.open(datei) as img:

                img = ImageOps.exif_transpose(img)

                breite, hoehe = img.size

                if max(breite, hoehe) > MAX_KANTE:
                    zu_gross += 1
                else:
                    bereits_klein += 1

        except Exception:
            nicht_lesbar += 1


    # --------------------------------------------------------
    # Sicherheitsabfrage
    # --------------------------------------------------------

    frage = (
        f"Gefundene JPEG-Dateien: {len(bilder)}\n\n"
        f"Zu verkleinern: {zu_gross}\n"
        f"Bereits maximal {MAX_KANTE} px: {bereits_klein}\n"
    )

    if nicht_lesbar:
        frage += f"Nicht lesbar / möglicherweise fehlerhaft: {nicht_lesbar}\n"

    frage += (
        f"\nAlle Bilder mit einer längeren Kante von mehr als "
        f"{MAX_KANTE} Pixeln werden proportional verkleinert.\n\n"
        "ACHTUNG:\n"
        "Die verkleinerten Dateien ersetzen die Originaldateien.\n\n"
        "Möchtest du fortfahren?"
    )

    fortfahren = messagebox.askyesno(
        "JPEGs verkleinern?",
        frage,
        icon="warning"
    )


    # --------------------------------------------------------
    # Benutzer hat abgebrochen
    # --------------------------------------------------------

    if not fortfahren:

        root.destroy()
        return


    # --------------------------------------------------------
    # Verarbeitung
    # --------------------------------------------------------

    bearbeitet = 0
    geskippt = 0
    fehler = 0
    eingespart_gesamt = 0

    fehler_dateien = []

    for datei in bilder:

        try:

            status, eingespart = bild_verkleinern(datei)

            if status == "bearbeitet":

                bearbeitet += 1
                eingespart_gesamt += eingespart

            elif status == "geskippt":

                geskippt += 1

        except Exception as e:

            fehler += 1

            fehler_dateien.append(
                f"{datei.name}: {e}"
            )


    # --------------------------------------------------------
    # Ergebnis
    # --------------------------------------------------------

    text = (
        "JPEG-Verkleinerung abgeschlossen.\n\n"
        f"Gefundene Bilder: {len(bilder)}\n"
        f"Bearbeitet: {bearbeitet}\n"
        f"Übersprungen: {geskippt}\n"
        f"Fehler: {fehler}\n\n"
        "Eingesparter Speicherplatz:\n"
        f"{format_speicherplatz(eingespart_gesamt)}"
    )

    if fehler_dateien:

        text += "\n\nFehlerhafte Dateien:\n"

        text += "\n".join(
            fehler_dateien[:10]
        )

        if len(fehler_dateien) > 10:

            text += (
                f"\n... und "
                f"{len(fehler_dateien) - 10} weitere."
            )

    messagebox.showinfo(
        "JPEG-Verkleinerung",
        text
    )

    root.destroy()


# ------------------------------------------------------------
# Programmstart
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
