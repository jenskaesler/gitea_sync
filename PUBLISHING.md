# Veröffentlichungsanleitung: GitHub & HACS

## Schritt 1 – Eigene Daten eintragen

Ersetze in diesen Dateien `jenskaesler` durch deinen GitHub-Benutzernamen:

| Datei | Zeile |
|-------|-------|
| `custom_components/gitea_sync/manifest.json` | `documentation`, `issue_tracker`, `codeowners` |
| `README.md` | alle Badge-URLs und My-HA-Link |
| `LICENSE` | Copyright-Zeile |

---

## Schritt 2 – GitHub Repository anlegen

1. https://github.com/new aufrufen
2. Repository-Name: **`gitea_sync`** (exakt so, Kleinbuchstaben)
3. **Public** wählen
4. **Keine** README, .gitignore oder Lizenz vorauswählen (kommt aus diesem Paket)
5. Beschreibung setzen:
   > Home Assistant integration to automatically sync /config files to a Gitea repository
6. Topics hinzufügen (unter „About" → ⚙️):
   `home-assistant`, `hacs`, `integration`, `gitea`, `backup`, `git-sync`

---

## Schritt 3 – Code hochladen

```bash
cd gitea_sync_pub/
git init
git add .
git commit -m "Initial release v1.0.0"
git branch -M main
git remote add origin https://github.com/jenskaesler/gitea_sync.git
git push -u origin main
```

---

## Schritt 4 – GitHub Actions prüfen

Nach dem Push unter https://github.com/jenskaesler/gitea_sync/actions prüfen:

- ✅ **Hassfest** muss grün sein
- ✅ **HACS Validation** muss grün sein

Beide müssen **ohne Fehler und ohne ignores** durchlaufen!

---

## Schritt 5 – Brands-Verzeichnis (für HACS Default-Listing)

Für das offizielle HACS-Listing muss dein Brand-Icon in `home-assistant/brands` vorhanden sein.

1. https://github.com/home-assistant/brands forken
2. Ordner `custom_integrations/gitea_sync/` anlegen
3. Diese Dateien hinzufügen:
   - `icon.png` — 256×256 px, quadratisch, PNG mit Transparenz
   - `logo.png` — optional, breiter als hoch
4. Pull Request an `home-assistant/brands` stellen

> Tipp: Ein einfaches Gitea-Logo (SVG → PNG konvertiert) reicht aus.
> Offizielles Gitea-Logo: https://gitea.io/images/gitea.png

---

## Schritt 6 – Ersten Release erstellen

```bash
git tag v1.0.0
git push origin v1.0.0
```

Der Release-Workflow erstellt automatisch einen GitHub Release mit ZIP-Anhang.
Alternativ manuell: https://github.com/jenskaesler/gitea_sync/releases/new

Release muss **published** sein (kein Draft), damit HACS ihn erkennt.

---

## Schritt 7 – Als Custom Repository testen

Bevor du den PR für HACS Default stellst, als Custom Repo testen:

1. HA → HACS → ⋮ → Benutzerdefinierte Repositories
2. URL: `https://github.com/jenskaesler/gitea_sync`
3. Kategorie: **Integration**
4. Hinzufügen → Installation testen

---

## Schritt 8 – HACS Default PR stellen

Erst wenn Schritt 4–7 erfolgreich waren:

1. https://github.com/hacs/default forken
2. Neuen Branch von `master` erstellen (z.B. `add-gitea-sync`)
3. In der Datei `integration` deinen Repo-Pfad **alphabetisch** einfügen:
   ```
   jenskaesler/gitea_sync
   ```
4. Pull Request stellen mit ausgefülltem PR-Template

> ⚠️ HACS-Backlog ist lang — mit 1–6 Monaten Wartezeit rechnen.
> In der Zwischenzeit können Nutzer das Repo als Custom Repository hinzufügen.

---

## My Home Assistant Badge (für README)

Generiere deinen persönlichen Installations-Badge:
https://my.home-assistant.io/create-link/?redirect=hacs_repository

Parameter:
- owner: `jenskaesler`
- repository: `gitea_sync`
- category: `integration`
