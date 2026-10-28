# 🪙 Spite Saver

> **Turn petty defiance into financial freedom.**  
> Built by **The Argonauts** for the college coding hackathon.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Design System](https://img.shields.io/badge/Theme-Warm_Editorial-284B3D?style=flat-square)](app/static/styles/main.css)

---

## 💡 The Premise

Traditional budgeting apps fail because they rely on guilt, cold spreadsheets, and delayed gratification. 

**Spite Saver** flips psychology on its head by gamifying **emotional resistance**. Every time you skip an overpriced cab surge, resist an impulse midnight Zomato order, or refuse to pay an unfair convenience fee, you log that money into your personal vault purely out of spite. 

Every saved rupee fills a real-time, skeuomorphic 3D glass piggy bank until your savings goal is smashed.

---

## ✨ Key Features

- **🏺 3D Skeuomorphic Glass Piggy Bank**
  - Custom layered SVG with volumetric shading, refraction highlights, and an ambient base platform.
  - Dynamically calculates liquid gold fill height based on real-time percentage (`₹ current / ₹ target`).
  - Adapts visually with goal progression—unlocking cool sunglasses at 75% and a gold crown at 100%.

- **⚡ 1-Tap "Quick Spite" Action Bar**
  - Instant micro-actions tailored for Indian college & urban daily life:
    - `+₹150` *Skipped Zomato / Swiggy Surge* (`#FoodDelivery`)
    - `+₹60` *Took Metro instead of Auto* (`#Commute`)
    - `+₹220` *Made Filter Coffee at Home* (`#DailyWin`)
    - `+₹499` *Closed Late-Night Shopping Cart* (`#Impulse`)

- **📜 Scrollytelling History Ledger**
  - Dynamic transaction timeline with interactive viewport observers.
  - Visual coin physics: scrolling past saves drops coins into the vault (`+1 🪙`), while spends drain the vault (`-1 🪙`).
  - One-click entry undo support with automatic goal balance recalculation.

- **🎉 Goal Smashed Ceremony & Surplus Rollover**
  - Reaching 100% locks the active ledger to prevent accidental over-logging.
  - Multi-stage confetti celebration burst powered by `canvas-confetti`.
  - "Claim Goal" ceremony modal allows archiving the completed milestone and rolling surplus funds into the next target.

- **🏆 Past Goals Trophy Room (`/past-goals`)**
  - Permanent card-based trophy wall showing every conquered milestone.
  - Features labeled, gold-filled trophy pigs for each completed target.
  - Displays analytics: days taken to conquer, total spite entries, and the user's **Top Resisted Habit**.

- **🔐 Robust Auth & Verification Flow**
  - Secure signup/login with Werkzeug password hashing.
  - 6-digit email OTP verification via SMTP with dev-friendly fallbacks.
  - Session-resilient route guards.

---

## 🎨 Color Palette & Design System

Spite Saver uses a custom warm editorial palette designed to feel grounded and intentional:

| Role | Color | Hex Code |
| :--- | :--- | :--- |
| **Background Canvas** | Warm Cream | `#F8F5EE` |
| **Card Surface** | Pure White | `#FFFFFF` |
| **Surface Soft** | Soft Alabaster | `#F0EBE1` |
| **Primary Brand** | Forest Green | `#284B3D` |
| **Accent / Gold** | Amber Gold | `#D49B35` |
| **Spend / Spite** | Brick Red | `#C84B31` |
| **Typography** | Outfit (Headings) & Inter (Body) | Google Fonts |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.12, Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Jinja2 Templates, Vanilla CSS3 (Custom Design System), Canvas Confetti
- **Tooling & Environment:** `python-dotenv`, Flask-Migrate

---

## 📁 Project Structure

```text
argonauts-decacode/
├── app/
│   ├── static/
│   │   ├── assets/
│   │   │   └── icon.png
│   │   └── styles/
│   │       └── main.css             # Unified design system & responsive styling
│   ├── templates/
│   │   ├── index.html               # Main dashboard & interactive scrollytelling feed
│   │   ├── no_goal.html             # Empty piggy state for creating first goal
│   │   ├── past_goals.html          # Card-based trophy room for achieved targets
│   │   ├── login.html               # User login
│   │   ├── signup.html              # User registration
│   │   ├── verification.html        # OTP verification form
│   │   └── verification_email.html  # Branded transactional email template
│   ├── __init__.py                  # App factory & auto DB creation
│   ├── auth.py                      # Authentication & OTP verification routes
│   ├── exts.py                      # SQLAlchemy, LoginManager extensions
│   ├── forms.py                     # WTForms definitions
│   ├── main.py                      # Core dashboard, transactions & goal routes
│   └── models.py                    # User, Goal, and Transaction schemas
├── config.py                        # App configuration & mail settings
├── requirements.txt                 # Dependencies
├── run.py                           # App entry point
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/SujaySimha2/argonauts-decacode.git
cd argonauts-decacode
```

### 2. Create & Activate a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root directory:

```env
SECRET_KEY=your_super_secret_hackathon_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_char_google_app_password
```

> **Note for Testing / Development:** If running without SMTP credentials, check your server terminal output during signup to view the printed 6-digit OTP directly.

### 5. Launch the Application
```bash
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 👥 The Argonauts
- **Sujay Simha** ([@SujaySimha2](https://github.com/SujaySimha2))
- **rgo75** ([Rahul G](https://github.com/Rahul-Gonal))
- **Saket Viraj**([Saket Viraj](https://github.com/saket703))

Built with defiance for **DECACODE 2026**.
