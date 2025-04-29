# Mindful Me – Abendtagebuch

Dieses Repository enthält mein Abschlussprojekt für den CS50x-Kurs: **„Mindful Me“**, eine Web-App zur täglichen Reflexion und Planung.

---

## 📄 Beschreibung

„Mindful Me“ ist ein Abendtagebuch, mit dem Nutzer:innen:
- Den vergangenen Tag reflektieren und Einträge speichern
- Ziele und To-Dos für den nächsten Tag planen
- Alle bisherigen Einträge chronologisch einsehen
- Eine Auswertung der Stimmung in einem bestimmten Zeitraum einsehen
---

## 🚀 Features

- 🔒 **Benutzerregistrierung & Login** mittels Flask-Sessions
- 📔 **Tagebuch-Einträge** erstellen und bearbeiten
- ✅ **To-Do-Liste** für Tagesaufgaben verwalten
- 🕘 **Historie**: Übersicht aller Einträge mit Zeitstempel
- 🌐 **Mobile-freundliches** Layout (responsive)
- 🛠️ **Datenbankinitialisierung** via `db/create_db.py`

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

## ⚙️ Installation & Setup

1. Repository klonen:
   ```bash
   git clone https://github.com/keszamol/cs50x-project.git
   cd cs50x-project
   ```
2. Virtuelle Umgebung erstellen & aktivieren:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Datenbank initialisieren:
   ```bash
   python db/create_db.py
   ```

---

## ▶️ Anwendung starten

```bash
flask run
```

Öffne im Browser: `http://127.0.0.1:5000`

---

## ✉️ Kontakt
 
- 🔗 [LinkedIn](https://www.linkedin.com/in/celine-maloszek-458a64359/)

---

*Viel Spaß beim Ausprobieren von Mindful Me!*

