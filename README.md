# 🍽️ Pantry to Plate

> AI-Powered Family Kitchen Management Platform  
> Smart pantry tracking, collaborative meal planning, AI recipe generation, and family kitchen coordination.

<p align="center">
  <a href="https://pantry-to-plate-dolen.vercel.app" target="_blank">
    <img src="https://img.shields.io/badge/Demo-Live%20on%20Vercel-black?style=for-the-badge&logo=vercel" alt="Live Demo" />
  </a>
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge&logo=github" alt="Status" />
  <img src="https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-blue?style=for-the-badge&logo=react" alt="Frontend" />
  <img src="https://img.shields.io/badge/Backend-Django%205%20%2B%20DRF-green?style=for-the-badge&logo=django" alt="Backend" />
  <img src="https://img.shields.io/badge/Database-MongoDB%20%2B%20MongoEngine-brightgreen?style=for-the-badge&logo=mongodb" alt="Database" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="MIT License" />
</p>

## 🌟 Overview

Pantry to Plate is a smart family kitchen management platform designed to reduce meal-planning stress, track pantry inventory in real time, and minimize food waste. It helps families collaborate on what they have, what they need, and what they should cook next.

The platform combines:

- inventory tracking for groceries and household staples
- AI-powered recipe suggestions using available ingredients
- family collaboration for shared shopping lists and alerts
- meal planning and communication tools for everyday cooking

With a modern dashboard and a lightweight, scalable architecture, Pantry to Plate turns kitchen management into a more organized and enjoyable experience.

---

## ✨ Key Features

### 🛒 Smart Pantry Tracking
- Add, edit, and remove pantry items
- Organize items by category and storage location
- Monitor stock levels and expiry dates
- Highlight low-stock and soon-to-expire items
- Manage pantry items from a family-wide shared workspace

### 🤖 AI Recipe Engine
- Generate recipe suggestions from current pantry inventory
- Apply cuisine, diet, and time-based filters
- Recommend substitutions when ingredients are missing
- Estimate calories and nutritional values
- Prioritize recipes based on ingredient matching and household preferences

### 👨‍👩‍👧‍👦 Family Collaboration
- Shared kitchen spaces for households or families
- Role-based access and ownership controls
- Shared to-buy list with task assignment
- Real-time communication and kitchen notifications

### 💬 Communication & Planning
- Family group chat and kitchen announcements
- Meal planning support for daily cooking decisions
- Polls and shared decision-making features
- Alerts for expiring food and low-stock items

### 🎨 Premium User Experience
- Responsive glassmorphism-inspired UI
- Lightweight SPA experience with smooth navigation
- Modern design optimized for desktop and mobile use

---

## 🧰 Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite, Tailwind CSS, Zustand, React Router, Framer Motion, Lucide React |
| Backend | Django 5, Django REST Framework, JWT Auth, Celery |
| Database | MongoDB, MongoEngine |
| Cache / Queue | Redis |
| AI | Google Gemini API |
| Deployment | Vercel (Frontend), Django Server / Hosting Setup (Backend) |

---

## 🏗️ Project Structure

```text
Pantry_To_Plate/
├── backend/                        # Django REST API
│   ├── apps/                       # Modular app structure
│   │   ├── auth_app/               # Authentication and user setup
│   │   ├── kitchen/                # Workspace settings
│   │   ├── pantry/                 # Inventory management
│   │   ├── recipes/                # Recipe engine and recommendations
│   │   ├── buylist/                # Shopping list logic
│   │   ├── mealplans/              # Meal planning features
│   │   ├── chat/                   # Family chat system
│   │   ├── alerts/                 # Notifications and reminders
│   │   ├── dietary/                # Dietary preferences and allergies
│   │   └── analytics/              # Consumption and insights
│   ├── pantrytoplate/              # Django project config
│   ├── requirements.txt            # Python dependencies
│   ├── manage.py                   # Django CLI
│   └── seed_data.py                # Seed master pantry data
│
├── frontend/                       # React + Vite client
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── services/
│   │   └── Router.jsx
│   ├── package.json
│   └── vite.config.js
│
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Local Development Setup

### Prerequisites

Before starting, make sure you have:

- Python 3.11+
- Node.js 18+
- MongoDB running locally or through MongoDB Atlas
- Redis (recommended for Celery/background tasks)

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

The backend API will typically run at:

- `http://127.0.0.1:8000`

### 2) Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The frontend app will usually run at:

- `http://localhost:5173`

> If your project uses a different environment variable naming convention, update the frontend config accordingly.

---

## 🔌 API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Create a new account |
| POST | `/api/v1/auth/login` | Authenticate and receive JWT |
| GET | `/api/v1/pantry` | Fetch pantry inventory |
| POST | `/api/v1/pantry` | Add new pantry items |
| POST | `/api/v1/recipes/ai-generate` | Generate AI recipe suggestions |
| GET | `/api/v1/buylist` | Retrieve shopping list |
| GET | `/api/v1/chat/messages` | View kitchen chat messages |
| GET | `/api/v1/alerts` | Get active kitchen alerts |

---

## 🗺️ Roadmap

- [x] Initial architecture and project scaffolding
- [x] Authentication and pantry CRUD flows
- [x] Core shopping list and kitchen logic
- [ ] AI recipe precision improvements
- [ ] Real-time chat and live updates
- [ ] Advanced alerts and household analytics
- [ ] Barcode and receipt scanning support

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Maintainer

- GitHub: [@dolendx7](https://github.com/dolendx7)
- Repository: [Pantry_To_Plate](https://github.com/dolendx7/Pantry_To_Plate)

Made with ❤️ for smarter family kitchens and less food waste.
