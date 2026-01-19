# City Voice

City Voice is a modular complaint management system built using **Python**, **Streamlit**, and a relational **SQL database**.  
It includes an admin dashboard, status management logic, and action logging for traceability.

## Features
- Structured complaint submission workflow
- Admin panel for updating complaint status (`Pending`, `In Progress`, `Resolved`)
- Real-time Streamlit interface with dynamic table rendering
- Presentation-ready UI theme (global styling via `.streamlit/config.toml` + `core/ui_theme.py`)
- Database-backed CRUD operations
- Automatic logging of all admin actions for auditability

## Tech Stack
- **Python** — core backend logic
- **Streamlit** — UI layer for real-time interaction
- **SQLite / MySQL** — persistent data storage (configurable in `db.py`)
- **Git + GitHub** — version control and collaboration

---


