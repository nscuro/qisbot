[![Build Status](https://travis-ci.org/scuroworks/qisbot.svg?branch=develop)](https://travis-ci.org/scuroworks/qisbot)

# qisbot

## Features
* Fetching of exam results / grades from your university's QIS server
* Local storage of those results, always accessible
* Notifications for new or updated exam results / grades
 * qisbot comes with support for notifications to stdout and e-mail
 * You can easily extend qisbot with your own notifications

## Installation

### The Python way
* Install Python **3**, any version *>= 3.4* will do
 * Installers and ZIP packages can be downloaded from [here](https://www.python.org/downloads/)
 * It is Pre-installed on many recent GNU/Linux distributions or can be installed using *apt*, *pacman*, *[homebrew](http://brew.sh/)* or similar package managers
* Download or clone this repository and install the dependencies via pip:
 * `pip3 install -r requirements.txt`
 * You may want to use a [virtual environment](https://virtualenv.pypa.io/en/stable/) for this
* You're all set! qisbot can now be startet with `python3 runqisbot.py`

### The *other* way
* I'm trying to provide standalone binaries for every release of qisbot
* The binaries are created using [PyInstaller](http://www.pyinstaller.org/), see their website for further details
* You can find them in the project's [releases section](https://github.com/scuroworks/qisbot/releases) when they're available

## Usage
* Get an overview of qisbot's functionality: `python3 runqisbot.py -h`
* Print all locally available exam results: `python3 runqisboty.py -p`
* Force a refresh of all exam results from QIS: `python3 runqisbot.py -f`
 * This will trigger notifies (if configured)
* So the typical use-case would be: `python3 runqisbot.py -f -p`
 1. Fetch results from QIS, compare with locally stored ones
 2. When reasonable & configured, execute notifications
 3. Print a table of the current data

## Configuration
qisbot lives from its configurability.
Per default, it will look for a file named `qisbot.ini` its root directory. 
You can specify a custom location via the `--config` argument.

This is how a qisbot configuration file should look like (see `sample_config.ini`)
```ini
[QIS]
# Your login credentials
username = <YOUR_USERNAME>
password = <YOUR_PASSWORD>

# URL to the login page of your QIS instance
baseUrl = https://<QIS_DOMAIN>/qisserver/rds?state=user&type=0

[NOTIFICATIONS]
# Notify on new exam results?
on_new = true

# Notify on updated exam results?
on_changed = true

# Notify via standard output (console / terminal)?
stdout = true

# Notify via E-Mail?
# As of v0.9, an E-Mail for each exam that is new or has been updated is sent.
# Depending on your semester, this can add up to a lot of mails flooding your inbox,
# so you may want to keep this disabled for your first run
email = false

[EMAIL NOTIFY]
# This is only required when 'email' in the [NOTIFICATIONS] section is true!

# Connection data of your SMTP server
# You may be able to use the E-Mail account provided by your university here...
host = <SMTP_SERVER_DOMAIN>
port = <SMTP_PORT>
ssl = false

# Your login credentials
username = <YOUR_SMTP_USERNAME>
password = <YOUR_SMTP_PASSWORD>

# You can test the information provided above by executing qisbot with the '--test-email' flag
# qisbot will then attempt a login on using the information provided and output the result

# The E-Mail address to send notifications to
destination = <YOUR_DESTINATION_EMAIL_ADDRESS>
```
