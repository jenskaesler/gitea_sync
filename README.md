# Gitea Config Sync

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/jenskaesler/gitea_sync.svg)](https://github.com/jenskaesler/gitea_sync/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/jenskaesler/gitea_sync/blob/main/LICENSE)
[![Hassfest](https://github.com/jenskaesler/gitea_sync/actions/workflows/hassfest.yml/badge.svg)](https://github.com/jenskaesler/gitea_sync/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/jenskaesler/gitea_sync/actions/workflows/hacs.yml/badge.svg)](https://github.com/jenskaesler/gitea_sync/actions/workflows/hacs.yml)

> **Automatische Versionskontrolle für deine Home Assistant Konfiguration.**
> Gitea Config Sync pusht deine `/config`-Dateien zuverlässig in ein Gitea-Repository —
> bei jeder Änderung, nach Zeitplan oder auf Knopfdruck.

---

## ✨ Features

- 🔄 **File-Watcher** — erkennt Änderungen sofort und synchronisiert automatisch (5s Debounce)
- ⏱️ **Zeitgesteuerter Sync** — konfigurierbares Intervall von 1 bis 1440 Minuten
- 🚀 **Startup-Sync** — synchronisiert automatisch bei jedem HA-Neustart
- 🖱️ **Manueller Sync** — per Button-Entity direkt im Dashboard oder per Service
- 🎯 **Einzeldatei-Sync** — gezieltes Pushen einzelner Dateien per Service-Aufruf
- 🔒 **Secrets-Schutz** — `secrets.yaml` und `.storage/` sind standardmäßig ausgeschlossen
- ⚡ **Intelligenter Vergleich** — nur tatsächlich geänderte Dateien werden gepusht
- 📊 **Status-Sensor** — zeigt `idle`, `running`, `success` oder `failed` mit Commit-SHA
- 🔧 **Flexible Pfadkonfiguration** — Include/Exclude per Glob-Muster frei konfigurierbar
- ⚙️ **Options-Flow** — alle Einstellungen nachträglich änderbar, kein Neustart nötig

---

## 📦 Installation

### Via HACS — empfohlen

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jenskaesler&repository=gitea_sync&category=integration)

1. Den Button oben klicken oder in HACS manuell als Custom Repository hinzufügen:
   `https://github.com/jenskaesler/gitea_sync` → Kategorie: **Integration**
2. **Gitea Config Sync** suchen und **Herunterladen** klicken
3. Home Assistant neu starten
4. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Gitea Config Sync**

### Manuell

1. Das [neueste Release](https://github.com/jenskaesler/gitea_sync/releases/latest) herunterladen
2. `gitea_sync.zip` entpacken
3. Den Ordner `custom_components/gitea_sync/` nach `/config/custom_components/gitea_sync/` kopieren
4. Home Assistant neu starten

### Optionale Abhängigkeit: File-Watcher

Für die automatische Erkennung von Dateiänderungen wird `watchdog` benötigt.
Ohne `watchdog` sind alle anderen Sync-Methoden weiterhin voll funktionsfähig.

```bash
# In der HA-Shell (Advanced SSH Addon):
pip install watchdog
```

---

## 🔧 Einrichtung

Die Einrichtung erfolgt in drei Schritten über den integrierten Config-Flow.

### Schritt 1 — Verbindung

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Gitea Config Sync**

- **Gitea URL** — URL deiner Gitea-Instanz, z.B. `https://gitea.example.com`
- **Access Token** — Gitea Personal Access Token (Scope: `repository`)
- **Repository-Besitzer** — dein Gitea-Username oder eine Organisation
- **Repository-Name** — Name des Ziel-Repositories, z.B. `ha-config`
- **Branch** — Ziel-Branch, Standard: `main`

> **Token erstellen:** Gitea → Einstellungen → Anwendungen → Token generieren → Scope `repository` aktivieren

### Schritt 2 — Pfade

- **Einschließen** — Glob-Muster für zu synchronisierende Dateien, kommagetrennt
  Standard: `*.yaml,*.json`
- **Ausschließen** — Glob-Muster für ausgeschlossene Dateien, kommagetrennt
  Standard: `secrets.yaml,.storage/,*.log,home-assistant_v2.db`
- **Commit-Präfix** — Präfix für automatische Commit-Nachrichten
  Standard: `HA Auto-Sync`

### Schritt 3 — Zeitplan

- **Intervall** — Automatischer Sync alle X Minuten (`0` = deaktiviert, max. 1440)
- **Beim Start synchronisieren** — Sync bei jedem HA-Neustart (Standard: `true`)
- **Dateiänderungen überwachen** — File-Watcher aktivieren (benötigt `watchdog`)

---

## 📡 Entitäten

Nach der Einrichtung stehen zwei Entitäten zur Verfügung:

### `sensor.gitea_sync_status`

Zeigt den aktuellen Synchronisationsstatus:

- `idle` — wartet auf den nächsten Trigger
- `running` — Synchronisation läuft gerade
- `success` — letzter Sync erfolgreich abgeschlossen
- `failed` — letzter Sync fehlgeschlagen

**Attribute des Sensors:**

- `last_sync` — Zeitstempel der letzten Synchronisation (ISO 8601)
- `last_commit` — SHA des letzten Commits (7 Zeichen)
- `files_synced` — Anzahl der tatsächlich geänderten Dateien

### `button.gitea_sync_jetzt_synchronisieren`

Löst sofort eine vollständige Synchronisation aus — ideal für das Dashboard.

---

## ⚙️ Dienste

### `gitea_sync.sync_now`

Startet eine vollständige Synchronisation aller konfigurierten Dateien.

```yaml
service: gitea_sync.sync_now
```

### `gitea_sync.sync_file`

Synchronisiert eine einzelne Datei aus `/config` nach Gitea.

```yaml
service: gitea_sync.sync_file
data:
  file_path: "automations.yaml"
```

---

## 🤖 Beispiel-Automationen

### Tägliche Sicherung um 02:00 Uhr

```yaml
alias: Tägliche HA-Config Sicherung nach Gitea
trigger:
  - platform: time
    at: "02:00:00"
action:
  - service: gitea_sync.sync_now
```

### Benachrichtigung bei fehlgeschlagenem Sync

```yaml
alias: Gitea Sync Fehler-Benachrichtigung
trigger:
  - platform: state
    entity_id: sensor.gitea_sync_status
    to: failed
action:
  - service: notify.mobile_app_mein_telefon
    data:
      title: "⚠️ Gitea Sync fehlgeschlagen"
      message: "Die HA-Config konnte nicht nach Gitea synchronisiert werden."
```

### Automationen-Datei sofort nach Reload synchronisieren

```yaml
alias: automations.yaml sofort nach Gitea pushen
trigger:
  - platform: event
    event_type: automation_reloaded
action:
  - service: gitea_sync.sync_file
    data:
      file_path: "automations.yaml"
```

---

## 🛠️ Fehlerbehebung

### Debug-Logging aktivieren

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.gitea_sync: debug
```

Logs sind danach unter **Einstellungen → System → Protokolle** sichtbar.

### „Verbindung zu Gitea fehlgeschlagen"

- Gitea-URL prüfen — muss mit `https://` beginnen, kein abschließendes `/`
- Token-Berechtigungen prüfen — Scope `repository` (Lesen & Schreiben) erforderlich
- Netzwerkverbindung von HA zur Gitea-Instanz prüfen

### „Repository nicht gefunden"

- Besitzer und Repository-Name exakt prüfen (Groß-/Kleinschreibung beachten)
- Repository muss existieren und für den Token zugänglich sein

### File-Watcher funktioniert nicht

```bash
pip install watchdog
# Danach HA neu starten
```

### Secrets werden versehentlich synchronisiert

Prüfen ob `secrets.yaml` im Exclude-Feld eingetragen ist.
Standard-Exclude: `secrets.yaml,.storage/,*.log,home-assistant_v2.db`

---

## 📋 Changelog

Alle Änderungen sind in der [CHANGELOG.md](https://github.com/jenskaesler/gitea_sync/blob/main/CHANGELOG.md) dokumentiert.

---

## 🤝 Mitwirken

Pull Requests und Issues sind willkommen!
Bitte lies die [PUBLISHING.md](https://github.com/jenskaesler/gitea_sync/blob/main/PUBLISHING.md) für Hinweise zur lokalen Entwicklung und zum Release-Prozess.

---

## 📄 Lizenz

MIT License — © 2026 [jenskaesler](https://github.com/jenskaesler)
Siehe [LICENSE](https://github.com/jenskaesler/gitea_sync/blob/main/LICENSE) für Details.
