# 🍽️ Pantry to Plate

> AI-Powered Family Kitchen Management Platform
>
> Smart pantry tracking, AI recipe generation, grocery planning, and collaborative home cooking — all in one place.

<p align="center">
  <a href="https://pantry-to-plate-dolen.vercel.app" target="_blank">
    <img src="https://img.shields.io/badge/Demo-Live%20on%20Vercel-black?style=for-the-badge&logo=vercel" alt="Live Demo" />
  </a>
  <a href="https://github.com/dolendx7/Pantry_To_Plate" target="_blank">
    <img src="https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge&logo=github" alt="Status" />
  </a>
  <img src="https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-blue?style=for-the-badge&logo=react" alt="Frontend" />
  <img src="https://img.shields.io/badge/Backend-Django%205%20%2B%20DRF-green?style=for-the-badge&logo=django" alt="Backend" />
  <img src="https://img.shields.io/badge/Database-MongoDB%20%2B%20MongoEngine-brightgreen?style=for-the-badge&logo=mongodb" alt="Database" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="MIT License" />
</p>

<p align="center">
  <strong>Reduce food waste. Simplify meal planning. Make family cooking smarter.</strong>
</p>

---

## 🌟 Overview

Pantry to Plate is a modern kitchen management platform built for families who want to eat better, waste less, and make meal decisions quickly. It combines pantry tracking, AI-powered recipe recommendations, shopping coordination, and household communication into one cohesive experience.

Instead of wondering what to cook from a half-empty fridge, families can:

- track groceries and pantry inventory in real time
- see what is running low or close to expiring
- generate recipes based on what they already have
- share meal plans and shopping lists across the household
- collaborate through a shared kitchen workspace and alerts

This project blends a fast React frontend with a Django REST API and MongoDB-powered data layer to create a scalable, modern home-kitchen system.

---

## ✨ Features

### 🛒 Smart Pantry Tracking
- Add, edit, and remove pantry items
- Categorize food by type and location
- Track stock levels, expiry dates, and consumption patterns
- Highlight low-stock and expiring items
- Maintain a shared family inventory for better planning

### 🤖 AI Recipe Generation
- Suggest recipes using available ingredients
- Filter by cuisine, diet, calories, and prep time
- Recommend smart substitutions for missing items
- Estimate nutrition values and ingredient fit
- Prioritize recipes based on household inventory and preferences

### 👨‍👩‍👧‍👦 Family Collaboration
- Shared kitchen workspace for households
- Role-based permissions and ownership controls
- Shared to-buy list and task assignment
- Alerts for low stock, expiry, and grocery updates
- Group communication around meals and planning

### 💬 Daily Kitchen Communication
- Family chat and daily meal coordination
- Notification center for kitchen events
- Polls and meal suggestions for collective decision-making
- Better communication around what is available and what needs to be bought

### 🎨 Premium Experience
- Responsive, modern interface
- Glassmorphism-inspired styling and polished UX
- Smooth navigation and adaptable dashboard layout
- Built to feel clean, useful, and family-friendly

---

## 🧰 Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite, Tailwind CSS, Zustand, React Router, Framer Motion, Lucide React |
| Backend | Django 5, Django REST Framework, JWT Authentication |
| Database | MongoDB + MongoEngine |
| Background Tasks | Celery |
| Caching / Messaging | Redis |
| AI | Google Gemini API |
| Deployment | Vercel (Frontend), Django hosting setup (Backend) |

---

## 🏗️ Project Structure

```text
Pantry_To_Plate/
├── backend/                          # Django API backend
│   ├── apps/                         # Modular Django apps
│   │   ├── auth_app/                 # Authentication and user management
│   │   ├── kitchen/                  # Household/workspace configuration
│   │   ├── pantry/                   # Inventory and pantry logic
│   │   ├── recipes/                  # Recipe generation and matching logic
│   │   ├── buylist/                  # Grocery and to-buy list features
│   │   ├── mealplans/                # Plan-based meal coordination
│   │   ├── chat/                     # Family communication system
│   │   ├── alerts/                   # Expiry and stock alerts
│   │   ├── dietary/                  # Diet and allergy preferences
│   │   └── analytics/                # Usage insights and reporting
│   ├── pantrytoplate/                # Django project configuration
│   ├── requirements.txt             # Python dependencies
│   ├── manage.py                    # Django CLI entry point
│   ├── seed_data.py                 # Seed default pantry / item data
│   └── .env.example                 # Example backend environment file
│
├── frontend/                         # Vite + React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── services/
│   │   └── Router.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── README.md
├── LICENSE
├── .gitignore
└── .github/                         # Optional automation / workflow files
```

---

## 🚀 Getting Started

### Prerequisites

Make sure the following are installed before you begin:

- Python 3.11+
- Node.js 18+
- MongoDB running locally or through MongoDB Atlas
- Redis for Celery/background task support (recommended)

### 1) Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python seed_data.py
python manage.py runserver
```

The backend API should run at:

- `http://127.0.0.1:8000`

### 2) Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The frontend app will typically be available at:

- `http://localhost:5173`

> If your project uses a different environment variable structure, update the values to match your local configuration.

---

## 🔌 API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Create a new user account |
| POST | `/api/v1/auth/login` | Authenticate and receive JWT tokens |
| GET | `/api/v1/pantry` | Get pantry inventory |
| POST | `/api/v1/pantry` | Add a pantry item |
| POST | `/api/v1/recipes/ai-generate` | Generate AI recipe suggestions |
| GET | `/api/v1/buylist` | Retrieve shopping list |
| GET | `/api/v1/chat/messages` | View kitchen chat messages |
| GET | `/api/v1/alerts` | Get active kitchen alerts |

---

## 🗺️ Roadmap

- [x] Project architecture and core setup
- [x] Authentication and pantry CRUD features
- [x] Shared kitchen and shopping list basics
- [ ] Improved AI recipe matching and meal scoring
- [ ] Live chat and shared household sync
- [ ] Analytics and consumption insights
- [ ] Barcode / receipt scanning
- [ ] Mobile-friendly PWA enhancements

---

## 🤝 Contributing

Contributions are welcome and encouraged.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

Be sure to keep the project clean, documented, and consistent with the existing architecture.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Maintainer

- GitHub: [@dolendx7](https://github.com/dolendx7)
- Repository: [Pantry_To_Plate](https://github.com/dolendx7/Pantry_To_Plate)

Made with ❤️ for smarter kitchens and less food waste.

---

## 📌 Recommended GitHub Repository Description

Use this as your repository description on GitHub:

`AI-Powered Family Kitchen Management Platform - Smart Pantry Tracking & AI Recipe Engine`

This is concise, clear, and aligned with the project brand.
