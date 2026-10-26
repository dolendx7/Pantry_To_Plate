# 🍽️ Pantry to Plate

> **AI-Powered Family Kitchen Management Platform**  
> *No more "what to cook today?" — Let AI manage your kitchen, family, and table.*

[![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge&logo=github)](https://github.com/dolendx7/Pantry_To_Plate)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-blue?style=for-the-badge&logo=react)](https://github.com/dolendx7/Pantry_To_Plate)
[![Backend](https://img.shields.io/badge/Backend-Django%205%20%2B%20DRF-green?style=for-the-badge&logo=django)](https://github.com/dolendx7/Pantry_To_Plate)
[![Database](https://img.shields.io/badge/Database-MongoDB%20%2B%20MongoEngine-brightgreen?style=for-the-badge&logo=mongodb)](https://github.com/dolendx7/Pantry_To_Plate)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](https://github.com/dolendx7/Pantry_To_Plate)

---

## 🌟 Overview

**Pantry to Plate** is an advanced, family-collaborative kitchen management platform designed to eliminate mealtime decision fatigue and minimize household food waste. Using a **Hub & Spoke model**, a household **Admin** creates a shared kitchen workspace, inviting **Members** (family/roommates) to participate. 

The application integrates real-time inventory tracking, collaborative tools, and a state-of-the-art **AI Recipe Engine** powered by Google's Gemini API to suggest personalized recipes based on ingredients currently in the pantry.

---

## 🧪 Tech Stack

### Frontend
*   **Core:** React 19 (Single Page Application)
*   **Build System:** Vite
*   **Styling:** Tailwind CSS v4 & custom CSS variables
*   **State Management:** Zustand
*   **Routing:** React Router v7
*   **Animations:** Framer Motion
*   **Icons:** Lucide React
*   **API Client:** Axios

### Backend
*   **Framework:** Django 5.0 & Django REST Framework (DRF)
*   **Authentication:** JWT (JSON Web Tokens via DRF SimpleJWT)
*   **Database:** MongoDB + MongoEngine (Object-Document Mapper)
*   **Task Queue:** Celery (Asynchronous background tasks)
*   **Caching & Broker:** Redis
*   **WSGI Server:** Gunicorn

### AI Integration
*   **Engine:** Google Gemini API (`gemini-3.1-flash-lite`)
*   **Fallback:** Dynamic local matching and heuristic recipe generator with sub-score ranking

---

## ✨ Features Breakdown

### 📦 Smart Pantry Tracking (CRUD)
*   Categorized view of items (Produce, Dairy, Grains, Spices, Bakery, etc.).
*   Automatic expiry countdowns and color-coded status badges.
*   "Running Low" stock thresholds with auto-flagging.
*   Location tracking (Fridge, Shelf, Freezer, Pantry).
*   Add custom items with auto-matching from a master database.

### 🤖 AI Recipe Generation
*   **Gemini Integration:** Recommends recipes using available pantry ingredients.
*   **Custom Filters:** Filter by cuisine (Indian, Italian, Mexican, etc.), diet (Veg, Vegan, Non-Veg), preparation time, and max calories.
*   **Smart Substitutions:** Recommends replacements for missing items (e.g., Tofu for Paneer, Greek Yogurt for Mayonnaise).
*   **Nutritional Estimates:** Calculates calories, protein, fats, and carbs dynamically.

### 👨‍👩‍👧‍👦 Family Collaboration
*   Admin generates a unique invite code to build a shared kitchen workspace.
*   Role-based permissions (Admin, Member, Guest).
*   **Shared To-Buy List:** Autocomplete shopping items based on low stock or custom inputs, with options to assign tasks to specific family members.
*   **Alert Center:** Shared real-time notifications for expiring dairy, low stock, or grocery list changes.

### 💬 Family Communication
*   Integrated, real-time Group Chat system.
*   Daily meal plan broadcasts.
*   Food Polls ("What should we make for dinner?") with reaction emojis.

### 🎨 Visual & UI Design (Premium Glassmorphism)
*   Curated colors featuring Rose Gold primary keys, Periwinkle accents, and Sage support colors.
*   Frosted glass panels (`backdrop-filter: blur`), subtle micro-animations, and bento-grid dashboards.
*   Fully responsive and optimized layout.

---

## 📁 Folder Structure

```text
Pantry_To_Plate/
├── backend/                        # Django API Backend
│   ├── apps/                       # Modular Django Applications
│   │   ├── auth_app/               # JWT Auth & Subscriptions
│   │   ├── kitchen/                # Kitchen/Workspace settings
│   │   ├── pantry/                 # Pantry inventory tracking
│   │   ├── recipes/                # Recipe database & AI view
│   │   ├── buylist/                # Shopping lists
│   │   ├── mealplans/              # Calendar-based meal scheduling
│   │   ├── chat/                   # Internal family chat
│   │   ├── alerts/                 # Expiring alerts & low stock
│   │   ├── dietary/                # Health preferences & allergies
│   │   └── analytics/              # Consumption graphs & charts
│   ├── pantrytoplate/              # Core Django config
│   ├── requirements.txt            # Python dependencies
│   ├── manage.py                   # Django CLI utility
│   └── seed_data.py                # Database seeding script
│
├── frontend/                       # Vite + React Client
│   ├── src/
│   │   ├── components/             # Common & Layout components
│   │   ├── pages/                  # Page components (Pantry, Chat, etc.)
│   │   ├── store/                  # Zustand state containers
│   │   ├── services/               # REST API Client files
│   │   └── Router.jsx              # React Router v7 routes configuration
│   ├── package.json                # NPM dependencies
│   └── vite.config.js              # Vite configuration
```

---

## 🚀 Local Development Setup

### Prerequisites
Make sure you have the following installed:
*   **Python 3.11+**
*   **Node.js 18+**
*   **MongoDB** (running locally on `mongodb://localhost:27017` or Atlas)
*   **Redis** (optional, running on `localhost:6379`)

---

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    # Windows:
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac:
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure environment variables:
    ```bash
    copy .env.example .env     # Windows
    # cp .env.example .env     # Linux/Mac
    ```
    *Open `.env` and set your credentials, database name, and `GEMINI_API_KEY` (or `OPENAI_API_KEY`).*

5.  Seed the database with default master items (optional but recommended):
    ```bash
    python seed_data.py
    ```

6.  Start the development server:
    ```bash
    python manage.py runserver
    ```
    *The backend API will run on `http://127.0.0.1:8000`.*

---

### 2. Frontend Setup

1.  Open a new terminal window and navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Configure frontend environment variables:
    ```bash
    # Create .env.local file
    echo VITE_API_URL=http://localhost:8000/api/v1 > .env.local
    ```

4.  Start the Vite developer server:
    ```bash
    npm run dev
    ```
    *The frontend application will be hosted on `http://localhost:5173`.*

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/v1/auth/register` | Create a new Admin account |
| **POST** | `/api/v1/auth/login` | Authenticate user and receive JWT |
| **GET** | `/api/v1/pantry` | List items in the kitchen's pantry |
| **POST** | `/api/v1/pantry` | Add a new pantry item |
| **POST** | `/api/v1/recipes/ai-generate` | Generate recipes via Google Gemini |
| **GET** | `/api/v1/buylist` | Get active shopping list |
| **GET** | `/api/v1/chat/messages` | Retrieve real-time kitchen chat messages |
| **GET** | `/api/v1/alerts` | List unread food/pantry notifications |

---

## 🗺️ Project Roadmap

- [x] **Phase 1 (Complete):** Architecture configuration, MongoDB connection, Glassmorphism UI components.
- [x] **Phase 2 (Complete):** Session auth, Pantry CRUD, basic Shopping List functionality.
- [ ] **Phase 3 (Active):** Fine-tuning Gemini prompt instructions and ingredient-matching precision.
- [ ] **Phase 4 (Upcoming):** WebSockets implementation for instant Chat & shared UI sync.
- [ ] **Phase 5 (Planned):** Barcode receipt scanner and native mobile packaging (PWA).

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the Repository.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

## 👨‍💻 Maintainers

*   **GitHub Username:** [@dolendx7](https://github.com/dolendx7)
*   **Repository:** [Pantry_To_Plate](https://github.com/dolendx7/Pantry_To_Plate)

***Made with ❤️ to simplify family kitchens and reduce food waste.***
