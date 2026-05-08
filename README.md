# Aurum Tempus — Luxury Watch E-Commerce Portfolio

A full-stack data science portfolio project simulating the digital presence and analytics infrastructure of a fictional Geneva watchmaker.

**Live demo:** https://mathias1801.github.io/Front-end_and_Back-end_Dashboard/

The live site includes a customer-facing e-commerce frontend (collections, heritage, craftsmanship, contact), a static analytics dashboard with revenue, funnel, customer segment, and ML insights views, and a portal entry page to switch between the two.

---

## What This Project Demonstrates

- End-to-end full-stack architecture: frontend, REST API, database, ETL, ML, and BI dashboard as integrated layers
- REST API development with FastAPI and SQLAlchemy ORM
- Synthetic data pipeline design using Faker with realistic seasonal and behavioural weighting
- Customer analytics ML pipeline: segmentation (KMeans/RFM), churn prediction (Random Forest), LTV prediction (Gradient Boosting), and product recommendations (cosine similarity)
- Frontend event tracking wired to a backend API for full purchase funnel analytics
- Containerised deployment with Docker and Docker Compose
- Static site hosting via GitHub Pages with a locally runnable Streamlit dashboard

---

## Overview

Aurum Tempus is built around the premise of a luxury Geneva watchmaker. The project covers the full data science stack: a synthetic customer and transaction dataset, a backend that captures live behavioural events, an ETL pipeline feeding a SQLite database, and a suite of ML models producing actionable business insights — all surfaced through both a static dashboard and an interactive Streamlit app.

---

## Project Structure

```
Aurum_Tempus_demo/
│
├── docs/                        # Static site — served via GitHub Pages
│   ├── portal.html              # Entry page (site vs dashboard)
│   ├── index.html               # Customer-facing homepage
│   ├── collections.html         # Watch collections + cart
│   ├── heritage.html
│   ├── craftsmanship.html
│   ├── contact.html
│   ├── dashboard.html           # Static analytics dashboard
│   ├── styles.css
│   └── script.js                # API event logger + cart system
│
├── api/
│   └── main.py                  # FastAPI — /events, /orders endpoints
│
├── database/
│   ├── models.py                # SQLAlchemy ORM models
│   └── init_db.py               # Schema creation + product seeding
│
├── data/
│   └── synthetic.py             # Synthetic data generator (150 customers)
│
├── etl/
│   └── pipeline.py              # ETL pipeline
│
├── ml/
│   ├── models.py                # ML training pipeline
│   └── saved/                   # Trained model binaries (not in repo)
│
├── dashboard/
│   └── app.py                   # Streamlit dashboard (local only)
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                         # Environment variables (not in repo)
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/mathias1801/front_end_-_Back_end_-_Dashboard.git
cd front_end_-_Back_end_-_Dashboard
pip install -r requirements.txt
```

### 2. Initialise the database and generate data

```bash
python database/init_db.py    # creates tables, seeds 5 products
python data/synthetic.py      # generates 150 synthetic customers + events
```

### 3. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Serve the frontend locally

```bash
python -m http.server 5500 --directory docs
# open http://localhost:5500
```

### 5. Run the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

---

## Docker

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Streamlit Dashboard | http://localhost:8501 |

---

## Event Tracking

The frontend automatically logs the following events to the API, each carrying a `session_id` (UUID, per browser session) for funnel analysis:

| Event | Trigger |
|---|---|
| `page_view` | Every page load |
| `product_view` | Watch card scrolls into viewport |
| `add_to_cart` | Add to Cart button clicked |
| `checkout_start` | Checkout modal opened |
| `purchase` | Order confirmed (per line item) |

---

## Dataset

The synthetic dataset was generated with Faker and a custom pipeline with realistic seasonal and behavioural weighting:

- 150 synthetic customers
- ~179 orders across 2021–2024
- ~2,146 events across the full purchase funnel
- $2.4M USD total revenue
- 5 watch collections: Perpetuelle I, Élégance Ultra Thin, Chronos Sport, Grande Complication, Ladies' Pavé

---

## ML Models

| Model | Algorithm | Output |
|---|---|---|
| Customer Segmentation | KMeans | 4 segment labels + RFM scores |
| Churn Prediction | Random Forest | Churn probability per customer |
| LTV Prediction | Gradient Boosting | Predicted lifetime value |
| Product Recommendations | Cosine Similarity | Top-N watches per customer |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend API | FastAPI, SQLAlchemy |
| Database | SQLite |
| ML Pipeline | scikit-learn (KMeans, Random Forest, GBM) |
| Dashboard | Static HTML (GitHub Pages) + Streamlit (local) |
| Data Generation | Faker + custom synthetic pipeline |
| Containerisation | Docker, Docker Compose |
