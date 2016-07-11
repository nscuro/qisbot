[![Build Status](https://travis-ci.com/scuroworks/qisbot.svg?token=24qz67tadxUHqtNZeoJu&branch=develop)](https://travis-ci.com/scuroworks/qisbot)

# qisbot
Schnelles und einfaches Auslesen des Notenspiegels von QIS Systemen.

## Wichtiger Hinweis
***qisbot*** wurde mit meinem (*scuroworks*) Studentenzugang zum QIS System der *Fachhochschule Kiel* entwickelt.
Ich kann nicht dafür garantieren, dass die Anwendung für das System jeder Universität bzw. für jeden Studiengang funktioniert. Sollten Sie ***qisbot*** für ihre Universität anpassen oder optimieren wollen, forken Sie dieses Projekt und entwickeln Sie ihre eigene Version (bitte Lizenz beachten) oder stellen Sie einen Pull-Request mit Ihren Anpassungen.

## Systemvoraussetzungen
- Python >= 3.4
- requests >= 2.10.0
- lxml >= 3.6.0

Benötigte Pakete können mit `pip install -r requirements.txt` installiert werden.

## Funktionen
***qisbot*** kann sich eigenständig auf QIS Servern anmelden und den Notenspiegel abrufen.
Gefundene Noten können als JSON Datei exportiert werden (`python3 qisbot.py --export <Dateipfad>`).
Zwischenspeicherung und Aufbereitung der Daten sowie eine Funktionalität zum Erkennen neuer Noten sollen noch folgen.

## Nutzung
Anzeige aller möglichen Funktionen: `python3 qisbot.py -h`

Das Wichtigste ist die Bereitstellung Ihrer Zugangsdaten. Dies kann auf 3 verschiedenen Wegen erreicht werden:

1. Nutzen Sie die `--username` und `--password` Optionen beim Aufruf des Skripts
2. Hinterlegen Sie Ihre Zugangsdaten beim Start in den Umgebungsvariablen `QIS_USER` und `QIS_PASS`
3. Ändern Sie die Zeile `QIS_USERNAME = os.environ.get('QIS_USER') or None` in `qisbot.py`, indem Sie `None` durch Ihren Nutzernamen in Anführungszeichen ersetzen. Verfahren Sie genauso auch für die `QIS_PASSWORD` Zeile direkt darunter
