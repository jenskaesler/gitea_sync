# Changelog

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.0.0] – 2024-06-15

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
