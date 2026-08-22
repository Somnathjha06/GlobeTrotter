<div align="center">
  <img src="app/static/img/hero-banner.jpg" alt="GlobeTrotter Banner" width="100%" style="border-radius: 12px; margin-bottom: 20px;">
  
  # GlobeTrotter 🌍
  **Your Personalized Premium Travel Planning Platform**

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
  [![Flask](https://img.shields.io/badge/Flask-Framework-black.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
  [![Hackathon](https://img.shields.io/badge/Odoo_×_LDCE-Hackathon-FF5722.svg?style=for-the-badge)](https://odoo.com)
  [![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](#)
</div>

---

## 📖 Overview & Problem Solved

**GlobeTrotter** is a modern, high-end SaaS platform built for the **Odoo × LDCE Hackathon**. It simplifies the chaotic and fragmented process of modern travel planning. 

Currently, travelers juggle between dozens of browser tabs, spreadsheets, and calendar apps to manage their itineraries and budgets. GlobeTrotter unifies this experience by providing an intuitive, centralized dashboard where users can design multi-city itineraries, estimate real-time budgets, visualize their travel timelines, and share their dream trips with friends or the community. 

Whether you are planning a luxurious getaway to the Swiss Alps or a budget backpacking trip through Tokyo, GlobeTrotter brings clarity, aesthetics, and organization to your adventure.

---

## ✨ Key Features

GlobeTrotter tackles the core requirements of the hackathon with a focus on usability and premium design:

*   🗺️ **Multi-City Itinerary Builder & Interactive Timeline**
    Easily add multiple stops to your trip. View a day-by-day, visually structured timeline showing exactly what activities and transit events happen on which day.
*   💰 **Automated Budget Tracker & Cost Breakdown**
    Assign estimated budgets per section and track granular expenses (Transport, Stay, Activities, Meals) across your entire trip.
*   🔍 **City & Activity Discovery**
    Discover trending destinations and top-rated activities using a dynamic search and filter engine. Pre-load your trip builder with rich city data directly from search.
*   🔗 **Public / Sharable Itineraries**
    Share your meticulously crafted itineraries with the world, or duplicate community trips using our fast "Copy Trip" cloning functionality.
*   🔐 **Secure User Profile & Authentication**
    Session-based secure authentication allowing users to manage their personal dashboard, track upcoming and past trips, and save their favorite destinations.

---

## 🛠️ Tech Stack Breakdown

GlobeTrotter is engineered with a scalable, modular architecture prioritizing performance and maintainability.

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, Flask | Core logic, routing, and RESTful API endpoints via Modular Blueprints. |
| **Database** | SQLite, SQLAlchemy | Relational data management using the Flask-SQLAlchemy ORM. |
| **Migrations** | Flask-Migrate (Alembic) | Robust database schema versioning and seamless migrations. |
| **Frontend** | Jinja2, HTML5, CSS3, JS | Server-side rendered templates with a bespoke, glassmorphic dark theme and Vanilla JS interactivity. |
| **Authentication** | Flask-Login | Secure, session-based user authentication and route protection. |

---

## 📂 Project Architecture

The application strictly adheres to the Flask Application Factory and Blueprint patterns to separate concerns effectively.

```text
GlobeTrotter/
├── app/
│   ├── __init__.py          # App Factory & Extension Initialization
│   ├── models/              # SQLAlchemy Database Models (User, Trip, City, etc.)
│   ├── routes/              # Flask Blueprints (auth, main, trips, itinerary, search)
│   ├── static/              # Static Assets
│   │   ├── css/             # Modular CSS (base, dashboard, trips, etc.)
│   │   ├── img/             # Images and Icons
│   │   └── js/              # Vanilla JavaScript Modules
│   └── templates/           # Jinja2 HTML Templates
│       ├── auth/            # Login / Registration views
│       ├── macros/          # Reusable UI components (e.g., toolbar)
│       ├── main/            # Dashboard view
│       └── trips/           # Trip Builder & Itinerary views
├── migrations/              # Alembic Database Migration Scripts
├── config.py                # Environment Configuration (Dev, Prod, Test)
├── requirements.txt         # Python Package Dependencies
└── run.py                   # Application Entry Point
```

---

## 🚀 Local Setup & Installation Guide

Follow these steps to run GlobeTrotter locally on your machine.

**1. Clone the repository**
```bash
git clone https://github.com/mothesandeep/GlobeTrotter.git
cd GlobeTrotter
```

**2. Create and activate a virtual environment**
```bash
# On Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Initialize the Database & Run Migrations**
```bash
# Set Flask environment variables
export FLASK_APP=run.py
export FLASK_DEBUG=1       # (Optional) For development mode

# Apply database migrations to create tables
flask db upgrade

# (Optional) Seed the database with initial mock data
# python seed.py
```

**5. Start the Application**
```bash
flask run
```
*The app will now be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).*

---

## 🏅 Evaluation & Judging Highlights

*   **Modular Architecture**: Utilizing Flask Blueprints, separating concerns into discrete `routes/` and `models/` for seamless scalability.
*   **Coding Standards**: Strictly adheres to PEP 8 standards, utilizing docstrings, type hinting (where applicable), and self-documenting clean code practices.
*   **Security Measures**: 
    * Secure password hashing via `werkzeug.security`.
    * Protection against SQL Injection via SQLAlchemy ORM parameterized queries.
    * Protection against XSS through Jinja2 auto-escaping.
*   **Premium UI/UX**: Custom-built CSS (no heavy frontend frameworks) featuring a modern deep-slate palette, glassmorphism, responsive grids, and subtle micro-animations.

---

## 👥 Team & Collaborators

Designed and engineered with passion for the Odoo × LDCE Hackathon.

*   **[Your Name]** - *Lead Developer & UI/UX Designer* - [@GitHubHandle](https://github.com/yourhandle)
*   **[Collaborator 2 Name]** - *Backend Engineer* - [@GitHubHandle](https://github.com/yourhandle)
*   **[Collaborator 3 Name]** - *Database Architect* - [@GitHubHandle](https://github.com/yourhandle)

---

<div align="center">
  <sub>Built with ❤️ for the Odoo × LDCE Hackathon 2026.</sub>
</div>
