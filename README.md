[![Build Status](https://travis-ci.org/scuroworks/qisbot.svg?branch=develop)](https://travis-ci.org/scuroworks/qisbot)

# qisbot
Schnelles und einfaches Auslesen des Notenspiegels von QIS Systemen.

## Wichtiger Hinweis
***qisbot*** wurde mit meinem (*scuroworks*) Studentenzugang zum QIS System der *Fachhochschule Kiel* entwickelt.
Ich kann nicht dafür garantieren, dass die Anwendung für das System jeder Universität bzw. für jeden Studiengang funktioniert. Sollten Sie ***qisbot*** für ihre Universität anpassen oder optimieren wollen, forken Sie dieses Projekt und entwickeln Sie ihre eigene Version (bitte Lizenz beachten) oder stellen Sie einen Pull-Request mit Ihren Anpassungen.

## Systemvoraussetzungen
- Python >= 3.4
- requests >= 2.10.0
- lxml >= 3.6.0
- tabulate >= 0.7.5

Benötigte Pakete können mit `pip3 install -r requirements.txt` installiert werden.

## Funktionen
***qisbot*** kann sich eigenständig auf QIS Servern anmelden und den Notenspiegel abrufen.
Die Ausgabe der Daten erfolgt standardmäßig im JSON Format. Mit der Option `--tabulate` lassen
sich die Ergebnisse in einer übersichtlichen Tabelle darstellen:
![Nutzungsbeispiel](http://i.imgur.com/seiih6v.png)

Gefundene Noten können als JSON Datei exportiert werden (`python3 qisbot.py --export <Dateipfad>`).
Zuvor exportierte Daten lassen sich später zum ermitteln neu eingestellter Noten verwenden, indem
sie mit erneut abgerufenen Daten verglichen werden: 
![Beispiel Neue Noten](http://i.imgur.com/hotZK3N.png)

## Installation
1. Laden Sie sich das Repository als ZIP Datei herunter oder klonen Sie es via `git clone`
2. Installieren Sie die Abhängigkeiten via `pip3 install -r requirements.txt`

Sie können qisbot nun direkt ausführen oder das Skript via `python3 setup.py install` installieren.
Die Installation sorgt dafür, dass das Skript im `/bin` bzw `Scripts` Verzeichnis Ihrer Python-Installation 
bzw Ihres Systems hinterlegt wird und von dort aufrufbar ist.

## Nutzung
Anzeige aller möglichen Funktionen: `python3 qisbot.py -h`

Das Wichtigste ist die Bereitstellung Ihrer Zugangsdaten. Dies kann auf 3 verschiedenen Wegen erreicht werden:

1. Nutzen Sie die `--username` und `--password` Optionen beim Aufruf des Skripts
2. Hinterlegen Sie Ihre Zugangsdaten beim Start in den Umgebungsvariablen `QIS_USER` und `QIS_PASS`
3. Ändern Sie die Zeile `QIS_USERNAME = os.environ.get('QIS_USER') or None` in `qisbot.py`, indem Sie `None` durch Ihren Nutzernamen in Anführungszeichen ersetzen. Verfahren Sie genauso auch für die `QIS_PASSWORD` Zeile direkt darunter

Weiterhin muss der Wert der Variable `QIS_URL_BASE` angepasst werden. Dabei handelt es sich um die Url zum QIS Serververzeichnis ihrer Hochschule. Im Normalfall sollten Sie lediglich die Domain anpassen müssen.

### Nutzung als Service
Wenn Sie ***qisbot*** als Service nutzen möchten (bspw. via Cronjob), empfiehlt sich folgender Aufruf:
`python3 qisbot.py --user <USER> --password <PASSWORD> --compare <FILE> --export <FILE>`
wobei beide Dateipfade zur selben Datei zeigen sollten. ***qisbot*** wird zuerst die neuen Daten mit den
"alten" vergleichen und dann den kompletten Datensatz erneut in der Datei speichern. Bei wiederholenden Aufrufen
werden Sie so erst eine Ausgabe erhalten, wenn es wirklich neue Daten gibt. Wollen Sie diese Funktionalität auch manuell
nutzen, verwenden Sie einfach die `--tabulate` Option.

**WICHTIG:** Sie sollten mindestens ein mal Daten in die Datei exportiert haben, ohne einen Vergleich
mit `--compare` anzufordern. Findet ***qisbot*** die Eingabedatei beim Vergleich nicht, wird er abbrechen.
