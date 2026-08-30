# JPEG-Verkleinerer

Ein kleines Python-Tool mit grafischer Benutzeroberfläche zum automatischen Verkleinern von JPEG-Bildern.

Das Programm durchsucht den Ordner, in dem sich das Python-Skript bzw. die erzeugte EXE befindet, nach `.jpg`- und `.jpeg`-Dateien. Bilder, deren längste Kante größer als der eingestellte Grenzwert ist, werden proportional verkleinert.

Das Seitenverhältnis bleibt dabei vollständig erhalten.

## Funktionen

* Verarbeitung aller `.jpg`- und `.jpeg`-Dateien im Programmordner
* Unterstützung von Groß- und Kleinschreibung bei Dateiendungen
* frei einstellbare maximale Kantenlänge
* Standardwert: `1000 px`
* Einstellung über eine Spinbox
* JPEG-Qualität über einen Schieberegler einstellbar
* Standardqualität: `90`
* Seitenverhältnis bleibt erhalten
* Hoch- und Querformat werden automatisch erkannt
* bereits ausreichend kleine Bilder werden übersprungen
* EXIF-Bildausrichtung wird berücksichtigt
* hochwertige Skalierung mit Lanczos-Resampling
* Sicherheitsabfrage vor dem Überschreiben
* Originaldatei wird erst nach erfolgreichem Speichern ersetzt
* Anzeige des aktuellen Bearbeitungsfortschritts
* Abschlussdialog mit Statistik
* Berechnung des eingesparten Speicherplatzes
* für die Erstellung einer eigenständigen Windows-EXE mit PyInstaller geeignet

---

## Beispiel

Bei einer eingestellten maximalen Kantenlänge von `1000 px` ergeben sich beispielsweise folgende Größen:

| Original       | Ergebnis      |
| -------------- | ------------- |
| 6000 × 4000 px | 1000 × 667 px |
| 4000 × 6000 px | 667 × 1000 px |
| 2500 × 1000 px | 1000 × 400 px |
| 1920 × 1080 px | 1000 × 563 px |
| 800 × 600 px   | unverändert   |
| 1000 × 667 px  | unverändert   |

Es wird immer nur die längere Kante auf den eingestellten Maximalwert reduziert.

Die andere Kante wird automatisch proportional angepasst.

---

## Funktionsweise

Das Programm arbeitet ausschließlich mit Bildern, die sich im selben Ordner wie das Programm befinden.

Beispiel:

```text
Fotos/
├── JPEG-Verkleinerer.exe
├── DSC_001.jpg
├── DSC_002.jpg
├── urlaub.jpeg
└── landschaft.JPG
```

Nach dem Start der EXE werden diese Bilder automatisch gefunden und überprüft.

Unterordner werden nicht durchsucht.

---

## Grafische Benutzeroberfläche

Beim Programmstart erscheint eine kleine Benutzeroberfläche.

Dort können zwei wesentliche Einstellungen vorgenommen werden.

### Maximale Kantenlänge

Die maximale Länge der längeren Bildkante wird über eine Spinbox eingestellt.

Standard:

```text
1000 px
```

Der Wert kann entweder direkt eingegeben oder über die Pfeiltasten verändert werden.

Die zweite Bildkante wird automatisch so angepasst, dass das ursprüngliche Seitenverhältnis erhalten bleibt.

### JPEG-Qualität

Die JPEG-Kompressionsqualität wird über einen Schieberegler festgelegt.

Standard:

```text
90
```

Für Bilder, die hauptsächlich für Webseiten verwendet werden, ist ein Wert zwischen etwa `85` und `90` meist ein guter Kompromiss zwischen Bildqualität und Dateigröße.

Die Qualitätsangabe entspricht dem JPEG-Qualitätsparameter von Pillow und ist technisch keine Prozentangabe.

---

## Sicherheitsabfrage

Vor der eigentlichen Verarbeitung zeigt das Programm eine Zusammenfassung an.

Beispielsweise:

```text
Gefundene JPEG-Dateien: 120

Zu verkleinern: 95
Bereits klein genug: 24
Nicht lesbar: 1

Maximale längere Kante: 1000 Pixel
JPEG-Qualität: 90
```

Erst nach einer ausdrücklichen Bestätigung beginnt die Verarbeitung.

---

## Achtung: Originaldateien werden überschrieben

Die verkleinerten Bilder ersetzen die ursprünglichen Dateien.

Das Programm erstellt derzeit keine dauerhaften Sicherungskopien.

Vor der Verarbeitung wichtiger oder nicht reproduzierbarer Bilder sollte daher gegebenenfalls ein Backup erstellt werden.

Das Programm verwendet allerdings intern eine temporäre Datei:

1. Das verkleinerte Bild wird zunächst separat gespeichert.
2. Erst wenn dieser Vorgang erfolgreich abgeschlossen wurde, wird die Originaldatei ersetzt.
3. Schlägt das Speichern fehl, bleibt die ursprüngliche Datei bestehen.

Damit wird das Risiko beschädigter Dateien bei einem Fehler während des Speichervorgangs reduziert.

---

## Abschlussstatistik

Nach der Verarbeitung erscheint ein Dialogfenster mit einer Zusammenfassung.

Beispiel:

```text
JPEG-Verkleinerung abgeschlossen.

Gefundene Bilder: 137
Bearbeitet: 112
Übersprungen: 24
Fehler: 1

Maximale längere Kante: 1000 Pixel
JPEG-Qualität: 90

Eingesparter Speicherplatz:
486.37 MB
```

Damit lässt sich unmittelbar erkennen, wie viele Dateien verändert wurden und wie viel Speicherplatz durch die Verkleinerung eingespart wurde.

---

# Installation

## Voraussetzungen

Benötigt wird:

* Python 3
* Pillow
* Tkinter

Tkinter ist bei normalen Windows-Python-Installationen üblicherweise bereits enthalten.

Pillow kann über `pip` installiert werden:

```bash
pip install pillow
```

---

## Repository klonen

Das Repository kann beispielsweise über Git geklont werden:

```bash
git clone <REPOSITORY-URL>
```

Anschließend:

```bash
cd <REPOSITORY-ORDNER>
```

Danach kann das Python-Skript direkt gestartet werden:

```bash
python jpeg_verkleinern.py
```

Unter Windows funktioniert je nach Installation auch:

```powershell
py jpeg_verkleinern.py
```

---

# Verwendung

1. `jpeg_verkleinern.py` in den gewünschten Bilderordner kopieren.
2. Das Skript starten.
3. Maximale Kantenlänge einstellen.
4. JPEG-Qualität auswählen.
5. Auf `Bilder verkleinern` klicken.
6. Sicherheitsabfrage kontrollieren.
7. Verarbeitung bestätigen.
8. Abschlussstatistik prüfen.

---

# Unterstützte Dateiformate

Aktuell verarbeitet das Programm ausschließlich JPEG-Dateien:

```text
.jpg
.jpeg
```

Die Groß- und Kleinschreibung der Dateiendung spielt keine Rolle.

Folgende Dateien werden beispielsweise erkannt:

```text
foto.jpg
foto.JPG
foto.jpeg
foto.JPEG
Foto.JpG
```

Andere Bildformate wie PNG, WebP, TIFF oder HEIC werden nicht verarbeitet.

---

# Bildqualität

Für die Verkleinerung wird Pillow verwendet.

Das Downsampling erfolgt über:

```python
Image.Resampling.LANCZOS
```

Lanczos ist ein hochwertiger Resampling-Algorithmus und eignet sich besonders gut zum Herunterskalieren von Fotografien.

Für die JPEG-Kompression wird standardmäßig verwendet:

```python
quality=90
optimize=True
```

Die Option `optimize=True` versucht zusätzlich, die JPEG-Datei effizienter zu speichern.

---

# EXIF-Ausrichtung

Viele Smartphones und Digitalkameras speichern Bilder intern nicht bereits gedreht, sondern hinterlegen die gewünschte Darstellung lediglich in den EXIF-Metadaten.

Das Programm berücksichtigt diese Orientierung mit:

```python
ImageOps.exif_transpose()
```

Dadurch werden insbesondere Hochformatbilder korrekt behandelt.

---

# Speicherplatzberechnung

Für jedes tatsächlich bearbeitete Bild wird die Dateigröße vor und nach der Verarbeitung verglichen.

Die Differenzen werden addiert und am Ende beispielsweise als:

```text
KB
MB
GB
```

ausgegeben.

Dadurch lässt sich unmittelbar abschätzen, welchen Effekt die Bildoptimierung hatte.

---

# Windows-EXE erstellen

Das Programm ist so aufgebaut, dass es auch als eigenständige Windows-EXE verwendet werden kann.

Hierfür eignet sich PyInstaller.

## PyInstaller installieren

```bash
pip install pyinstaller
```

Oder gemeinsam mit Pillow:

```bash
pip install pillow pyinstaller
```

---

## EXE erzeugen

Im Verzeichnis des Python-Skripts:

```bash
pyinstaller --onefile --windowed --name JPEG-Verkleinerer jpeg_verkleinern.py
```

### Parameter

`--onefile`

Erzeugt eine einzelne ausführbare `.exe`-Datei.

`--windowed`

Unterdrückt das zusätzliche Konsolenfenster. Dadurch erscheint beim Start ausschließlich die grafische Oberfläche.

`--name JPEG-Verkleinerer`

Legt den Namen der erzeugten EXE fest.

---

## Ergebnis

Nach erfolgreichem Build entsteht unter anderem:

```text
dist/
└── JPEG-Verkleinerer.exe
```

Diese Datei kann anschließend unabhängig vom Python-Skript verwendet werden.

Eine lokale Python-Installation ist auf dem Zielrechner dann nicht mehr erforderlich.

---

# Portable Verwendung

Die fertige EXE kann einfach in einen beliebigen Bilderordner kopiert werden.

Beispiel:

```text
Urlaub_Kroatien/
├── JPEG-Verkleinerer.exe
├── IMG_0012.jpg
├── IMG_0013.jpg
├── IMG_0014.jpg
└── IMG_0015.jpg
```

Danach genügt ein Doppelklick auf:

```text
JPEG-Verkleinerer.exe
```

Das Programm erkennt bei einer PyInstaller-Version automatisch den Ordner, in dem sich die EXE befindet.

Dadurch funktioniert die portable Verwendung auch bei einer mit `--onefile` erzeugten Anwendung korrekt.

---

# Technischer Hintergrund

Bei einer normalen Python-Ausführung kann der Programmordner über `__file__` bestimmt werden.

Bei einer mit PyInstaller erzeugten Anwendung muss dagegen berücksichtigt werden, dass PyInstaller intern mit temporär entpackten Dateien arbeiten kann.

Das Programm unterscheidet daher zwischen normaler Python-Ausführung und einer sogenannten `frozen` Application.

Sinngemäß:

```python
if getattr(sys, "frozen", False):
    ordner = Path(sys.executable).resolve().parent
else:
    ordner = Path(__file__).resolve().parent
```

Dadurch wird bei der EXE tatsächlich der Speicherort der ausführbaren Datei verwendet und nicht ein interner temporärer PyInstaller-Ordner.

---

# Fehlerbehandlung

Kann eine Datei nicht verarbeitet werden, wird die Verarbeitung der übrigen Bilder fortgesetzt.

Am Ende wird die Anzahl der Fehler angezeigt.

Zusätzlich werden die betreffenden Dateien im Abschlussdialog aufgelistet.

Typische Ursachen können beispielsweise sein:

* beschädigte JPEG-Datei
* fehlende Schreibrechte
* Datei wird von einem anderen Programm exklusiv verwendet
* ungültige Bilddaten trotz `.jpg`-Dateiendung
* Probleme beim Speichern von Metadaten

Ein Fehler bei einer einzelnen Datei beendet somit nicht automatisch die gesamte Verarbeitung.

---

# Datenschutz

Die Bildverarbeitung erfolgt vollständig lokal auf dem Rechner.

Es werden keine Bilder:

* hochgeladen
* an externe Server übertragen
* analysiert
* an Cloud-Dienste gesendet

Eine Internetverbindung ist für die Verwendung des Programms nicht erforderlich.

---

# Geeignete Einsatzbereiche

Das Tool eignet sich insbesondere für:

* Webseiten
* GitHub Pages
* Blogs
* Fotodokumentationen
* Projektseiten
* Vorschaubilder
* Bildergalerien
* kleinere Archive
* Reduzierung großer Smartphone-Fotos
* Vorbereitung von Bildern für Webprojekte

Gerade moderne Smartphones erzeugen häufig JPEG-Dateien mit mehreren Tausend Pixeln Kantenlänge und mehreren Megabyte Dateigröße.

Für eine normale Webdarstellung ist diese Auflösung häufig unnötig.

Eine Reduktion beispielsweise von:

```text
6000 × 4000 px
```

auf:

```text
1000 × 667 px
```

kann die Dateigröße drastisch reduzieren.

---

# Was das Programm bewusst nicht macht

Das Programm:

* verändert keine Bilder, die bereits klein genug sind
* vergrößert keine Bilder
* verändert das Seitenverhältnis nicht
* durchsucht keine Unterordner
* verschiebt keine Bilder
* löscht keine zusätzlichen Dateien
* verarbeitet keine anderen Bildformate
* lädt keine Daten ins Internet

---

# Mögliche zukünftige Erweiterungen

Denkbare Erweiterungen wären beispielsweise:

* optionale Sicherung der Originaldateien
* frei wählbarer Quellordner
* frei wählbarer Zielordner
* rekursive Verarbeitung von Unterordnern
* Unterstützung für PNG und WebP
* automatische WebP-Konvertierung
* Qualitätsvorschau
* Fortschrittsbalken
* Drag-and-Drop
* Speicherung der letzten Einstellungen
* Option zum Entfernen von EXIF-Metadaten
* Option zum Beibehalten sämtlicher EXIF-Metadaten
* Protokolldatei über die Verarbeitung
* Vergleich der Dateigröße vor und nach der Verarbeitung
* Batch-Konvertierung ohne Überschreiben der Originale

---

# Abhängigkeiten

Das Projekt verwendet:

* Python
* Pillow
* Tkinter
* pathlib
* tempfile
* os
* sys

Die Python-Standardbibliotheken müssen nicht separat installiert werden.

Die einzige zusätzliche Python-Abhängigkeit ist derzeit:

```text
Pillow
```

---

# Lizenz

**MIT License**

Copyright (c) 2026 Julian Kampitsch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

# Hinweis

Das Programm überschreibt bearbeitete Originaldateien.

Auch wenn das Speichern durch eine temporäre Datei abgesichert wird, sollten von wichtigen oder nicht reproduzierbaren Bildern grundsätzlich Sicherungskopien vorhanden sein.

