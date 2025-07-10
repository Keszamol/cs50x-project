# Mindful Me – Abendtagebuch

Dieses Repository enthält mein Abschlussprojekt für den CS50x-Kurs: **„Mindful Me“**, eine Web-App zur täglichen Reflexion.

---

## 📄 Beschreibung

„Mindful Me“ ist ein Abendtagebuch, mit dem Nutzer:innen:
- Den vergangenen Tag reflektieren und Einträge speichern können
- Alle bisherigen Einträge chronologisch einsehen können
- Eine Auswertung der Stimmung in einem bestimmten Zeitraum einsehen können
---

## 🚀 Features

- 🔒 **Benutzerregistrierung & Login** mittels Flask-Sessions
- 📔 **Tagebuch-Einträge** erstellen und bearbeiten
- 🕘 **Historie**: Übersicht aller Einträge mit Zeitstempel
- 🌐 **Mobile-freundliches** Layout (responsive)
- 🛠️ **Datenbankinitialisierung** via `db/create_db.py`
---

## 🟠 Updates / Pläne

- Projekt optimieren (Start: 30.06.2025)
---

## 🏗️ Architektur

```
Client (HTML/CSS/JS)  ↔  Flask Server (app.py)  ↔  SQLite (db/database.db)
```

- **Backend:** Python 3 + Flask
- **Datenbank:** SQLite (`db/database.db`)
- **Templates:** Jinja2 (`templates/`)
- **Static Assets:** CSS (`static/style.css`)

---

## ▶️ Anwendung starten

```bash
python run.py
```

Öffne im Browser: `http://127.0.0.1:5000`

---

## ✉️ Kontakt
 
- 🔗 [LinkedIn](https://www.linkedin.com/in/celine-maloszek-458a64359/)

---

*Viel Spaß beim Ausprobieren von Mindful Me!*

