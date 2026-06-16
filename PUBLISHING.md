# Publishing & Contributing Guide

## Repository

- **GitHub:** https://github.com/jenskaesler/gitea_sync
- **HACS Custom Repo URL:** `https://github.com/jenskaesler/gitea_sync`

---

## Neuen Release erstellen

1. `custom_components/gitea_sync/manifest.json` — `version` aktualisieren
2. `CHANGELOG.md` — neue Version dokumentieren
3. Commit & Push auf `main`
4. Tag erstellen und pushen:

```bash
git tag v1.2.0
git push origin v1.2.0
```

Der GitHub Actions Workflow `release.yml` erstellt automatisch den Release mit ZIP-Anhang.

---

## HACS Default Listing

Für das offizielle HACS-Listing:

1. https://github.com/home-assistant/brands forken
2. Ordner `custom_integrations/gitea_sync/` mit `icon.png` (256×256 px) anlegen
3. Pull Request an `home-assistant/brands` stellen
4. https://github.com/hacs/default forken
5. In der Datei `integration` alphabetisch einfügen: `jenskaesler/gitea_sync`
6. Pull Request stellen

> ⚠️ HACS-Backlog ist lang — mit 1–6 Monaten Wartezeit rechnen.

---

## GitHub Actions

| Workflow | Trigger | Zweck |
|---------|---------|-------|
| `hassfest.yml` | Push auf main, wöchentlich | HA Manifest-Validierung |
| `hacs.yml` | Push auf main, wöchentlich | HACS-Validierung |
| `release.yml` | Tag `v*.*.*` | Automatischer Release mit ZIP |

---

## Lokale Entwicklung

```bash
# Integration in HA-Testinstanz einbinden
cp -r custom_components/gitea_sync /config/custom_components/

# HA neu starten und testen
```
