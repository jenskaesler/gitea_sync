# Changelog

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.4.0] – 2026-06-16

### 🐛 Kritischer Bugfix

- **`__init__.py`** — Blocking-Call-Fehler im File-Watcher vollständig behoben.
  `observer.start()` sowie `observer.stop()` und `observer.join()` sind blockierende
  Calls die nicht im async HA Event-Loop laufen dürfen. Alle drei werden nun korrekt
  über `await hass.async_add_executor_job()` im Executor-Thread ausgeführt.
  Zusätzlich bleibt `_setup_file_watcher` nun korrekt `async` damit der
  `await`-Aufruf im Setup möglich ist.

  Übersicht aller Thread-Regeln die nun korrekt eingehalten werden:

  - `observer.start()` → `await hass.async_add_executor_job(observer.start)`
  - `observer.stop()` → `await hass.async_add_executor_job(observer.stop)`
  - `observer.join()` → `await hass.async_add_executor_job(observer.join)`
  - Watchdog-Callbacks → `asyncio.run_coroutine_threadsafe(_debounced(), loop)`

## [1.3.0] – 2026-06-16

### 🐛 Kritischer Bugfix

- **`__init__.py`** — Schwerwiegender Threading-Fehler im File-Watcher behoben der Home
  Assistant zum Absturz bringen konnte (`RuntimeError: calls hass.async_create_task
  from a thread other than the event loop`). Der watchdog-Handler lief in einem
  separaten Thread und rief `hass.async_create_task()` direkt auf, was im HA
  Event-Loop-Thread nicht erlaubt ist. Ersetzt durch `asyncio.run_coroutine_threadsafe()`
  für thread-sicheres Scheduling. Zusätzlich werden nun auch `on_deleted`-Events
  vom File-Watcher erkannt.

## [1.2.0] – 2026-06-16

### Behoben
- `manifest.json` — Version von `1.0.0` auf `1.1.0` korrigiert (war nicht synchron mit Release-Tag)
- `translations/en.json` — Englische Übersetzung war identisch mit der deutschen; nun vollständig auf Englisch übersetzt
- `CHANGELOG.md` — Fehlenden Eintrag für `v1.1.0` ergänzt; Jahreszahl von 2024 auf 2026 korrigiert
- `LICENSE` — Jahreszahl im Copyright von 2024 auf 2026 korrigiert
- `README.md` — HACS-Badge von „Default" auf „Custom" korrigiert (Integration noch nicht im offiziellen HACS Default-Store gelistet)
- `PUBLISHING.md` — Veralteten Inhalt bereinigt und als Contributor- & Release-Anleitung neu geschrieben

## [1.1.0] – 2026-06-15

### Geändert
- Brand-Icon nach `custom_components/gitea_sync/brand/icon.png` verschoben (HACS-Anforderung)
- `strings.json` und Übersetzungen bereinigt (URL-Felder ohne Beispiel-URLs)
- `manifest.json` Key-Reihenfolge korrigiert (Hassfest-Anforderung: domain, name, dann alphabetisch)
- Englische Übersetzung (`translations/en.json`) vollständig auf Englisch übersetzt

## [1.0.0] – 2026-06-15

### Hinzugefügt
- Initiale Version der Gitea Config Sync Integration
- Config Flow mit 3-stufiger Einrichtung (Verbindung → Pfade → Zeitplan)
- Sensor-Entity mit Status (`idle`, `running`, `success`, `failed`), letztem Sync-Zeitpunkt und Commit-SHA
- Button-Entity für manuellen Sync-Trigger
- Service `gitea_sync.sync_now` für vollständige Synchronisation
- Service `gitea_sync.sync_file` für einzelne Dateien
- File-Watcher mit 5-Sekunden-Debounce (erfordert `watchdog`)
- Konfigurierbares Zeitintervall (1–1440 Minuten)
- Sync beim HA-Start (konfigurierbar)
- Include/Exclude-Filter per Glob-Muster
- Automatisches Überspringen unveränderter Dateien (Inhaltsvergleich)
- Konfigurierbarer Commit-Nachricht-Präfix
- Vollständige deutsche Übersetzung
- Options-Flow zur nachträglichen Konfigurationsänderung
