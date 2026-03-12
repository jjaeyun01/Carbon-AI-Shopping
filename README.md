# Novera — Carbon-Aware Shopping Platform

AI-powered platform that analyzes product sustainability and recommends lower-carbon alternatives for furniture and clothing.

Novera helps users compare products based on sustainability signals such as materials, eco scores, and shipping impact to support more environmentally responsible purchasing decisions.

---

## Demo

### Landing Page
Search and explore products with sustainability metrics.

### Product Detail
View environmental impact information and compare alternatives.

### Recommendation Engine
AI-suggested lower-carbon product alternatives.

### Sustainability Dashboard
Track sustainability impact and eco choices.

---

## Overview

Novera is a full-stack sustainability shopping platform designed to help users make better purchasing decisions by comparing environmental impact across products.

The platform analyzes product attributes such as materials, carbon footprint estimates, and eco scores to recommend alternatives with lower environmental impact.

This project combines full-stack engineering, data processing, and recommendation system design to build a practical sustainability-focused product discovery experience.

---

## Problem

Consumers increasingly want to purchase sustainable products, but product-level environmental information is often unavailable, inconsistent, or difficult to interpret.

As a result, users struggle to:

- compare products by environmental impact
- identify lower-carbon alternatives
- understand sustainability tradeoffs

---

## Solution

Novera addresses this problem by providing:

- structured sustainability product attributes
- eco score comparisons
- recommendation of lower-carbon alternatives
- sustainability analytics dashboards

Users can search products, explore sustainability metrics, and discover environmentally responsible alternatives.

---

## Key Features

### Product Search
Users can search products based on:

- product name
- category
- materials
- sustainability tags

### Product Detail Pages

Each product page displays:

- price
- materials
- eco score
- carbon footprint estimate
- ESG rating
- shipping type
- sustainability tags

### Recommendation Engine

Novera recommends alternative products that:

- belong to the same category
- have similar price ranges
- use similar materials
- have improved eco scores

### Sustainability Dashboard

Users can view sustainability metrics such as:

- total carbon saved
- eco choices made
- sustainability score

### Recently Viewed Products

Tracks recently viewed items using user interaction logs.

### Trending Products

Displays the most viewed products based on aggregated user behavior.

---

## System Architecture
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

## Tech Stack

### Frontend
- React
- TypeScript
- React Router
- CSS

### Backend
- FastAPI
- Python
- REST APIs

### Data
- JSON product dataset
- user interaction logs

---

## API Endpoints

### Products

- GET /products
- GET /products/{product_id}

### Recommendations

- GET /products/{product_id}/recommendations

### Dashboard

- GET /dashboard

### User Actions

- POST /user-actions
- GET /user-actions
- GET /user-actions/recent-products
- GET /user-actions/most-viewed-products

---

## Project Structure
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

## Author

Jaeyoon Lee  
Computer Science & Data Science