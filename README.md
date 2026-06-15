# Gitea Config Sync

[![HACS Badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/jenskaesler/gitea_sync.svg)](https://github.com/jenskaesler/gitea_sync/releases)
[![License](https://img.shields.io/github/license/jenskaesler/gitea_sync.svg)](LICENSE)
[![Hassfest](https://github.com/jenskaesler/gitea_sync/actions/workflows/hassfest.yml/badge.svg)](https://github.com/jenskaesler/gitea_sync/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/jenskaesler/gitea_sync/actions/workflows/hacs.yml/badge.svg)](https://github.com/jenskaesler/gitea_sync/actions/workflows/hacs.yml)

Home Assistant Custom Integration, die deine `/config`-Dateien automatisch mit einem Gitea-Repository synchronisiert — manuell, zeitgesteuert oder bei Dateiänderungen.

---

## Features

- 🔄 **Automatischer Sync** bei Dateiänderungen (File-Watcher mit Debounce)
- ⏱️ **Zeitgesteuerter Sync** in konfigurierbarem Intervall
- 🚀 **Sync beim HA-Start**
- 🖱️ **Manueller Sync** per Button-Entity oder Service
- 🎯 **Einzeldatei-Sync** per Service-Aufruf
- 🔒 **Secrets werden standardmäßig ausgeschlossen**
- ⚡ **Nur geänderte Dateien werden gepusht** (Inhaltsvergleich)
- 📊 **Sensor-Entity** mit Status, Commit-SHA und Zeitstempel
- 🔧 **Frei konfigurierbare Pfade** via Glob-Muster

---

## Installation

### Via HACS (empfohlen)

[![Zu HACS hinzufügen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jenskaesler&repository=gitea_sync&category=integration)

1. HACS öffnen → **Integrationen** → Suche nach **Gitea Config Sync**
2. **Herunterladen** klicken
3. Home Assistant neu starten

### Manuell

1. Dieses Repository herunterladen
2. Den Ordner `custom_components/gitea_sync/` nach `/config/custom_components/gitea_sync/` kopieren
3. Home Assistant neu starten

### Optionale Abhängigkeit (File-Watcher)

Für die automatische Erkennung von Dateiänderungen wird `watchdog` benötigt:

```bash
# In der HA-Shell (Advanced SSH Addon):
pip install watchdog
```

Ohne `watchdog` funktionieren alle anderen Sync-Methoden weiterhin.

---

## Einrichtung

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Gitea Config Sync**

### Schritt 1: Verbindung

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| Gitea URL | URL deiner Gitea-Instanz | `https://gitea.example.com` |
| Access Token | Gitea Personal Access Token | `abc123...` |
| Repository-Besitzer | GitHub/Gitea Username oder Organisation | `jens` |
| Repository-Name | Name des Ziel-Repositories | `ha-config` |
| Branch | Ziel-Branch | `main` |

> **Token erstellen:** Gitea → Einstellungen → Anwendungen → Token generieren
> Benötigter Scope: `repository` (Lesen & Schreiben)

### Schritt 2: Pfade

| Feld | Standard | Beschreibung |
|------|---------|-------------|
| Einschließen | `*.yaml,*.json` | Glob-Muster, kommagetrennt |
| Ausschließen | `secrets.yaml,.storage/,*.log,home-assistant_v2.db` | Glob-Muster, kommagetrennt |
| Commit-Präfix | `HA Auto-Sync` | Prefix für Commit-Nachrichten |

### Schritt 3: Zeitplan

| Feld | Standard | Beschreibung |
|------|---------|-------------|
| Intervall (Minuten) | `0` | `0` = deaktiviert, sonst 1–1440 |
| Beim Start synchronisieren | `true` | Sync bei jedem HA-Neustart |
| Dateiänderungen überwachen | `true` | File-Watcher (benötigt `watchdog`) |

---

## Entitäten

| Entität | Typ | Beschreibung |
|---------|-----|-------------|
| `sensor.gitea_sync_status` | Sensor | Aktueller Status |
| `button.gitea_sync_jetzt_synchronisieren` | Button | Manueller Sync-Trigger |

### Sensor-Zustände

| Zustand | Bedeutung |
|---------|----------|
| `idle` | Wartet auf nächsten Trigger |
| `running` | Synchronisation läuft |
| `success` | Letzter Sync erfolgreich |
| `failed` | Letzter Sync fehlgeschlagen |

### Sensor-Attribute

| Attribut | Beschreibung |
|----------|-------------|
| `last_sync` | ISO-Zeitstempel der letzten Synchronisation |
| `last_commit` | SHA des letzten Commits (7 Zeichen) |
| `files_synced` | Anzahl tatsächlich geänderter Dateien |

---

## Dienste

### `gitea_sync.sync_now`

Startet sofort eine vollständige Synchronisation aller konfigurierten Dateien.

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

## Beispiel-Automationen

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

### Einzelne Datei nach Änderung synchronisieren

```yaml
alias: automations.yaml sofort nach Gitea
trigger:
  - platform: event
    event_type: automation_reloaded
action:
  - service: gitea_sync.sync_file
    data:
      file_path: "automations.yaml"
```

---

## Fehlerbehebung

### Debug-Logging aktivieren

In `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.gitea_sync: debug
```

### Häufige Probleme

**„Verbindung zu Gitea fehlgeschlagen"**
- Gitea-URL prüfen (mit `https://`, ohne abschließenden `/`)
- Token-Berechtigungen prüfen (Scope `repository` erforderlich)
- Netzwerkverbindung von HA zu Gitea prüfen

**„Repository nicht gefunden"**
- Besitzer und Repository-Name exakt prüfen (Groß-/Kleinschreibung beachten)
- Repository muss auf Gitea existieren und öffentlich oder für den Token zugänglich sein

**File-Watcher funktioniert nicht**
- `pip install watchdog` in der HA-Shell ausführen
- HA danach neu starten

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md)

---

## Lizenz

MIT License – siehe [LICENSE](LICENSE)
