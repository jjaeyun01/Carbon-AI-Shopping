# 🌱 Novera — Carbon-Aware Shopping Platform

AI-powered platform that analyzes product sustainability and recommends **lower-carbon alternatives** for everyday products.

Novera helps users compare products based on sustainability signals such as **materials, eco scores, and shipping impact** to support more environmentally responsible purchasing decisions.

---

# 🚀 Demo

## Landing Page
Search and explore products with sustainability metrics.

## Product Detail
View environmental impact information and compare alternatives.

## Recommendation Engine
AI-suggested lower-carbon product alternatives.

## Sustainability Dashboard
Track sustainability impact and eco choices.

---

# 📌 Overview

Novera is a **full-stack sustainability shopping platform** designed to help users make better purchasing decisions by comparing environmental impact across products.

The platform analyzes product attributes such as:

- materials  
- carbon footprint estimates  
- eco scores  

and recommends alternatives with lower environmental impact.

This project combines **full-stack engineering, data processing, and recommendation system design** to build a practical sustainability-focused product discovery experience.

---

# ⚠️ Problem

Consumers increasingly want to purchase sustainable products, but product-level environmental information is often:

- unavailable
- inconsistent
- difficult to interpret

As a result, users struggle to:

- compare products based on environmental impact
- identify lower-carbon alternatives
- understand sustainability tradeoffs

Most shopping platforms optimize for **price and popularity rather than sustainability**.

---

# 💡 Solution

Novera addresses this problem by providing:

- structured sustainability product attributes
- eco score comparisons
- recommendation of lower-carbon alternatives
- sustainability analytics dashboards

Users can search products, explore sustainability metrics, and discover environmentally responsible alternatives.

---

# ✨ Key Features

## Product Search

Users can search products based on:

- product name
- category
- materials
- sustainability tags

---

## Product Detail Pages

Each product page displays:

- price
- materials
- eco score
- carbon footprint estimate
- ESG rating
- shipping type
- sustainability tags

---

## AI Recommendation Engine

Novera recommends alternative products that:

- belong to the same category
- have similar price ranges
- use similar materials
- have improved eco scores

---

## Sustainability Dashboard

Users can view sustainability metrics such as:

- total carbon saved
- eco choices made
- sustainability score

---

## Recently Viewed Products

Tracks recently viewed items using user interaction logs.

---

## Trending Products

Displays the most viewed products based on aggregated user behavior.

---

## User Interaction Tracking

Tracks platform activity such as:

- product views
- recommendation clicks
- product grid clicks
- search queries

These logs support analytics and future personalization features.

---

# 🏗 System Architecture
React Frontend
↓
FastAPI Backend
↓
Product APIs + User Actions
↓
Recommendation Engine
↓
Analytics (Trending / Recently Viewed)

---

# 🧰 Tech Stack

## Frontend

- React
- TypeScript
- React Router
- CSS

## Backend

- FastAPI
- Python
- REST APIs

## Data

- JSON product dataset
- user interaction logs

---

# 🔗 API Endpoints

## Products
GET /products
GET /products/{product_id}


## Recommendations


GET /products/{product_id}/recommendations


## Dashboard


GET /dashboard


## User Actions


POST /user-actions
GET /user-actions
GET /user-actions/recent-products
GET /user-actions/most-viewed-products


---

# 📂 Project Structure


carbon-aware-shopping/

frontend
├─ src
│ ├─ components
│ ├─ pages
│ ├─ services
│ └─ styles

backend
├─ routers
├─ services
└─ data


---

# ⚙️ How to Run Locally

## Clone repository


git clone https://github.com/yourusername/carbon-aware-shopping.git

cd carbon-aware-shopping


---

## Backend Setup


cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload


Backend runs at:


http://127.0.0.1:8000


API docs:


http://127.0.0.1:8000/docs


---

## Frontend Setup


cd frontend

npm install
npm run dev


Frontend runs at:


http://localhost:5173


---

# 🔮 Future Improvements

Potential future enhancements include:

- machine learning recommendation models
- carbon footprint prediction
- user authentication
- personalized recommendations
- PostgreSQL database integration
- advanced sustainability analytics

---

# 👨‍💻 Author

Jaeyoon Lee  
Computer Science & Data Science

---

# 📁 Portfolio Project

This project demonstrates experience in:

- full-stack web development
- API design
- recommendation systems
- user analytics pipelines
- sustainability-focused product engineering