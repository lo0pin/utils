import os
import sys
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageOps


# ============================================================
# Grundeinstellungen
# ============================================================

STANDARD_MAX_KANTE = 1000
STANDARD_QUALITAET = 90

MIN_KANTE = 100
MAX_KANTE = 10000

MIN_QUALITAET = 50
MAX_QUALITAET = 100


# ============================================================
# Ordner bestimmen
# ============================================================

def ermittle_programmordner():
    """
    Gibt den Ordner zurück, in dem sich die Python-Datei bzw.
    die erzeugte EXE befindet.

    Funktioniert sowohl als normales Python-Skript als auch
    als PyInstaller-EXE.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    else:
        return Path(__file__).resolve().parent


ORDNER = ermittle_programmordner()


# ============================================================
# Hilfsfunktionen
# ============================================================

def format_speicherplatz(bytes_wert):
    """Bytes menschenlesbar formatieren."""

    if bytes_wert < 1024:
        return f"{bytes_wert} Byte"

    elif bytes_wert < 1024 ** 2:
        return f"{bytes_wert / 1024:.1f} KB"

    elif bytes_wert < 1024 ** 3:
        return f"{bytes_wert / (1024 ** 2):.2f} MB"

    else:
        return f"{bytes_wert / (1024 ** 3):.2f} GB"


def finde_bilder():
    """
    Findet alle JPG- und JPEG-Dateien im selben Ordner
    wie das Skript bzw. die EXE.
    """

    return sorted(
        datei
        for datei in ORDNER.iterdir()
        if datei.is_file()
        and datei.suffix.lower() in (".jpg", ".jpeg")
    )


def bild_verkleinern(dateipfad, max_kante, qualitaet):
    """
    Verkleinert ein JPEG proportional, falls seine längste
    Kante größer als max_kante ist.

    Rückgabe:
        ("bearbeitet", eingesparte_bytes)
        ("geskippt", 0)
    """

    alte_dateigroesse = dateipfad.stat().st_size

    with Image.open(dateipfad) as original:

        # EXIF-Rotation korrekt anwenden.
        # Besonders wichtig bei Smartphone-/Kamerafotos.
        bild = ImageOps.exif_transpose(original)

        breite, hoehe = bild.size
        laengste_kante = max(breite, hoehe)

        # Bereits klein genug:
        # Das Bild wird vollständig unangetastet gelassen.
        if laengste_kante <= max_kante:
            return "geskippt", 0

        # ----------------------------------------------------
        # Neue Größe proportional berechnen
        # ----------------------------------------------------

        faktor = max_kante / laengste_kante

        neue_breite = max(1, round(breite * faktor))
        neue_hoehe = max(1, round(hoehe * faktor))

        # Hochwertiges Downsampling
        bild = bild.resize(
            (neue_breite, neue_hoehe),
            Image.Resampling.LANCZOS
        )

        # JPEG unterstützt kein RGBA etc.
        if bild.mode not in ("RGB", "L"):
            bild = bild.convert("RGB")

        # ----------------------------------------------------
        # Metadaten möglichst erhalten
        # ----------------------------------------------------

        exif = bild.getexif()
        icc_profile = original.info.get("icc_profile")

        # ----------------------------------------------------
        # Erst temporär speichern
        # ----------------------------------------------------

        fd, temp_name = tempfile.mkstemp(
            suffix=".jpg",
            dir=dateipfad.parent
        )

        os.close(fd)

        temp_pfad = Path(temp_name)

        try:

            save_kwargs = {
                "format": "JPEG",
                "quality": qualitaet,
                "optimize": True,
            }

            if exif:
                save_kwargs["exif"] = exif.tobytes()

            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile

            bild.save(
                temp_pfad,
                **save_kwargs
            )

            # Erst nach erfolgreichem Speichern
            # das Original ersetzen.
            os.replace(
                temp_pfad,
                dateipfad
            )

        finally:

            # Falls vorher ein Fehler auftrat:
            if temp_pfad.exists():
                try:
                    temp_pfad.unlink()
                except Exception:
                    pass

    neue_dateigroesse = dateipfad.stat().st_size

    eingespart = alte_dateigroesse - neue_dateigroesse

    return "bearbeitet", eingespart


# ============================================================
# GUI
# ============================================================

class JPEGVerkleinererApp:

    def __init__(self, root):

        self.root = root

        root.title("JPEG-Verkleinerer")

        root.resizable(False, False)

        # ----------------------------------------------------
        # Variablen
        # ----------------------------------------------------

        self.max_kante_var = tk.IntVar(
            value=STANDARD_MAX_KANTE
        )

        self.qualitaet_var = tk.IntVar(
            value=STANDARD_QUALITAET
        )

        self.qualitaet_text_var = tk.StringVar(
            value=str(STANDARD_QUALITAET)
        )

        # ----------------------------------------------------
        # Hauptbereich
        # ----------------------------------------------------

        mainframe = ttk.Frame(
            root,
            padding=20
        )

        mainframe.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # ----------------------------------------------------
        # Titel
        # ----------------------------------------------------

        titel = ttk.Label(
            mainframe,
            text="JPEG-Bilder verkleinern",
            font=("Segoe UI", 14, "bold")
        )

        titel.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # Erklärung
        # ----------------------------------------------------

        beschreibung = ttk.Label(
            mainframe,
            text=(
                "Alle JPG- und JPEG-Dateien im selben Ordner wie "
                "dieses Programm werden geprüft.\n"
                "Nur Bilder, deren längste Kante größer als der "
                "eingestellte Wert ist, werden verkleinert."
            ),
            justify="left"
        )

        beschreibung.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # Kantenlänge
        # ----------------------------------------------------

        ttk.Label(
            mainframe,
            text="Maximale längere Kante:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        spinbox = ttk.Spinbox(
            mainframe,
            from_=MIN_KANTE,
            to=MAX_KANTE,
            increment=50,
            textvariable=self.max_kante_var,
            width=10
        )

        spinbox.grid(
            row=2,
            column=1,
            sticky="w",
            padx=(15, 5)
        )

        ttk.Label(
            mainframe,
            text="Pixel"
        ).grid(
            row=2,
            column=2,
            sticky="w"
        )

        # ----------------------------------------------------
        # Qualitäts-Slider
        # ----------------------------------------------------

        ttk.Label(
            mainframe,
            text="JPEG-Qualität:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=(15, 5)
        )

        slider_frame = ttk.Frame(mainframe)

        slider_frame.grid(
            row=3,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(15, 0),
            pady=(15, 5)
        )

        slider = ttk.Scale(
            slider_frame,
            from_=MIN_QUALITAET,
            to=MAX_QUALITAET,
            orient="horizontal",
            variable=self.qualitaet_var,
            command=self.slider_geaendert,
            length=220
        )

        slider.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.qualitaet_label = ttk.Label(
            slider_frame,
            textvariable=self.qualitaet_text_var,
            width=4
        )

        self.qualitaet_label.grid(
            row=0,
            column=1,
            padx=(10, 0)
        )

        # ----------------------------------------------------
        # Hinweise
        # ----------------------------------------------------

        hinweis = ttk.Label(
            mainframe,
            text=(
                "Empfehlung für Webbilder: 85–90\n"
                "Die Originaldateien werden überschrieben."
            ),
            foreground="#555555"
        )

        hinweis.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(15, 20)
        )

        # ----------------------------------------------------
        # Ordneranzeige
        # ----------------------------------------------------

        ttk.Label(
            mainframe,
            text="Ordner:",
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=5,
            column=0,
            sticky="nw"
        )

        ordner_label = ttk.Label(
            mainframe,
            text=str(ORDNER),
            wraplength=350
        )

        ordner_label.grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="w",
            padx=(15, 0)
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_var = tk.StringVar(
            value=""
        )

        self.status_label = ttk.Label(
            mainframe,
            textvariable=self.status_var
        )

        self.status_label.grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(20, 10)
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        button_frame = ttk.Frame(mainframe)

        button_frame.grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="e",
            pady=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=root.destroy
        ).grid(
            row=0,
            column=0,
            padx=(0, 10)
        )

        self.start_button = ttk.Button(
            button_frame,
            text="Bilder verkleinern",
            command=self.start
        )

        self.start_button.grid(
            row=0,
            column=1
        )

        # Enter startet
        root.bind(
            "<Return>",
            lambda event: self.start()
        )

        # Escape beendet
        root.bind(
            "<Escape>",
            lambda event: root.destroy()
        )

        # Fenster zentrieren
        self.fenster_zentrieren()


    def slider_geaendert(self, wert):
        """Slider-Wert auf ganze Zahl runden."""

        qualitaet = round(float(wert))

        self.qualitaet_var.set(qualitaet)
        self.qualitaet_text_var.set(str(qualitaet))


    def fenster_zentrieren(self):
        """Fenster auf dem Bildschirm zentrieren."""

        self.root.update_idletasks()

        breite = self.root.winfo_width()
        hoehe = self.root.winfo_height()

        bildschirm_breite = self.root.winfo_screenwidth()
        bildschirm_hoehe = self.root.winfo_screenheight()

        x = (bildschirm_breite - breite) // 2
        y = (bildschirm_hoehe - hoehe) // 2

        self.root.geometry(
            f"+{x}+{y}"
        )


    def start(self):

        # ----------------------------------------------------
        # Eingaben prüfen
        # ----------------------------------------------------

        try:
            max_kante = int(
                self.max_kante_var.get()
            )
        except (ValueError, tk.TclError):

            messagebox.showerror(
                "Ungültige Eingabe",
                "Bitte eine gültige maximale Kantenlänge eingeben."
            )

            return

        if max_kante < MIN_KANTE or max_kante > MAX_KANTE:

            messagebox.showerror(
                "Ungültige Eingabe",
                f"Die Kantenlänge muss zwischen "
                f"{MIN_KANTE} und {MAX_KANTE} Pixel liegen."
            )

            return

        qualitaet = round(
            self.qualitaet_var.get()
        )

        # ----------------------------------------------------
        # Bilder suchen
        # ----------------------------------------------------

        bilder = finde_bilder()

        if not bilder:

            messagebox.showinfo(
                "Keine Bilder gefunden",
                "Im Programmordner wurden keine JPG- oder "
                "JPEG-Dateien gefunden."
            )

            return

        # ----------------------------------------------------
        # Vorab bestimmen, wie viele überhaupt größer sind
        # ----------------------------------------------------

        zu_bearbeiten = 0
        bereits_klein = 0
        nicht_lesbar = 0

        for datei in bilder:

            try:

                with Image.open(datei) as bild:

                    bild = ImageOps.exif_transpose(bild)

                    if max(bild.size) > max_kante:
                        zu_bearbeiten += 1
                    else:
                        bereits_klein += 1

            except Exception:
                nicht_lesbar += 1

        # ----------------------------------------------------
        # Nichts zu tun
        # ----------------------------------------------------

        if zu_bearbeiten == 0:

            messagebox.showinfo(
                "Keine Bearbeitung notwendig",
                (
                    f"{len(bilder)} JPEG-Dateien gefunden.\n\n"
                    f"Alle lesbaren Bilder haben bereits eine "
                    f"maximale Kantenlänge von {max_kante} Pixel "
                    f"oder weniger."
                )
            )

            return

        # ----------------------------------------------------
        # Sicherheitsabfrage
        # ----------------------------------------------------

        antwort = messagebox.askyesno(
            "Originaldateien überschreiben?",
            (
                f"Gefundene JPEG-Dateien: {len(bilder)}\n\n"
                f"Zu verkleinern: {zu_bearbeiten}\n"
                f"Bereits klein genug: {bereits_klein}\n"
                f"Nicht lesbar: {nicht_lesbar}\n\n"
                f"Maximale längere Kante: {max_kante} Pixel\n"
                f"JPEG-Qualität: {qualitaet}\n\n"
                f"ACHTUNG:\n"
                f"Die bearbeiteten Originaldateien werden "
                f"durch die verkleinerten Versionen ersetzt.\n\n"
                f"Fortfahren?"
            ),
            icon="warning"
        )

        if not antwort:
            return

        # ----------------------------------------------------
        # Verarbeitung
        # ----------------------------------------------------

        self.start_button.config(
            state="disabled"
        )

        self.root.update_idletasks()

        bearbeitet = 0
        geskippt = 0
        fehler = 0

        eingespart_gesamt = 0

        fehler_dateien = []

        for nummer, datei in enumerate(
            bilder,
            start=1
        ):

            self.status_var.set(
                f"Bearbeite {nummer} von {len(bilder)}: "
                f"{datei.name}"
            )

            self.root.update()

            try:

                status, eingespart = bild_verkleinern(
                    datei,
                    max_kante,
                    qualitaet
                )

                if status == "bearbeitet":

                    bearbeitet += 1

                    eingespart_gesamt += (
                        eingespart
                    )

                else:
                    geskippt += 1

            except Exception as e:

                fehler += 1

                fehler_dateien.append(
                    f"{datei.name}: {e}"
                )

        # ----------------------------------------------------
        # Fertig
        # ----------------------------------------------------

        self.status_var.set(
            "Bearbeitung abgeschlossen."
        )

        self.start_button.config(
            state="normal"
        )

        # Negative Einsparung theoretisch möglich,
        # z.B. bei exotisch komprimierten Quelldateien.
        if eingespart_gesamt >= 0:
            speichertext = format_speicherplatz(eingespart_gesamt)
        else:
            speichertext = (
                f"keine Einsparung "
                f"(Dateien wurden insgesamt "
                f"{format_speicherplatz(abs(eingespart_gesamt))} größer)"
            )

        # ----------------------------------------------------
        # Ergebnistext
        # ----------------------------------------------------

        text = (
            f"JPEG-Verkleinerung abgeschlossen.\n\n"
            f"Gefundene Bilder: {len(bilder)}\n"
            f"Bearbeitet: {bearbeitet}\n"
            f"Übersprungen: {geskippt}\n"
            f"Fehler: {fehler}\n\n"
            f"Maximale längere Kante: "
            f"{max_kante} Pixel\n"
            f"JPEG-Qualität: {qualitaet}\n\n"
            f"Eingesparter Speicherplatz:\n"
            f"{speichertext}"
        )

        if fehler_dateien:

            text += (
                "\n\nFehlerhafte Dateien:\n"
            )

            text += "\n".join(
                fehler_dateien[:10]
            )

            if len(fehler_dateien) > 10:

                text += (
                    f"\n... und "
                    f"{len(fehler_dateien) - 10} "
                    f"weitere."
                )

        messagebox.showinfo(
            "Fertig",
            text
        )


# ============================================================
# Programmstart
# ============================================================

def main():

    root = tk.Tk()

    app = JPEGVerkleinererApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
