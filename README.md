# CSVCom

CSVCom ist ein benutzerfreundliches Python-Tool mit grafischer Oberfläche (Tkinter), um zwei CSV-Dateien komfortabel zu vergleichen und die Unterschiede sowie Gemeinsamkeiten zu analysieren und zu exportieren.

## Features

- **CSV-Vergleich mit GUI:** Wähle zwei CSV-Dateien, Trennzeichen und Encoding individuell aus.
- **Spaltenauswahl:** Bestimme, welche Spalte(n) als Vergleichskriterium dienen.
- **Ergebnis-Tabs:** Zeigt Datensätze, die nur in Datei 1, nur in Datei 2 oder in beiden vorhanden sind, übersichtlich in Tabs an.
- **Sortierbare Tabellen:** Spalten lassen sich per Klick auf die Überschrift sortieren.
- **Export:** Ergebnisse können gezielt (inkl. Spaltenauswahl, Encoding, Trennzeichen) als neue CSV exportiert werden.
- **Fortschrittsbalken:** Zeigt den Fortschritt beim Vergleich an.
- **Datei-Infos:** Zeigt Infos zu geladenen CSVs (Größe, Zeilen, Spalten).

## Voraussetzungen

- Python 3.8+
- Die Pakete aus `requirements.txt`:
  - pandas
  - tk

Installiere die Abhängigkeiten mit:

```sh
pip install -r requirements.txt
```

## Starten

```sh
python csvcom.py
```

## Hinweise

- Das Programm läuft unter Windows, Linux und macOS.
- Große CSV-Dateien werden unterstützt, aber der Vergleich kann je nach Dateigröße etwas dauern.
- Exportierte CSVs landen standardmäßig im gleichen Ordner wie die geladene Datei (anpassbar im Export-Dialog).

## Lizenz

MIT License