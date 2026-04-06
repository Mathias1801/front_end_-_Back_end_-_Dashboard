# Aurum Tempus — Luxury Watch E-Commerce Portfolio

> A full-stack data science portfolio project simulating the digital presence and analytics infrastructure of a fictional Geneva watchmaker.

## 🌐 Live Demo

**[https://mathias1801.github.io/front_end_-_Back_end_-_Dashboard/](https://mathias1801.github.io/front_end_-_Back_end_-_Dashboard/)**

The live site includes:
- Customer-facing e-commerce frontend (collections, heritage, craftsmanship, contact)
- Static analytics dashboard with revenue, funnel, customer segments, and ML insights
- Portal entry page to switch between the two views

---

## Overview

Aurum Tempus is a portfolio piece demonstrating end-to-end data engineering, backend API development, machine learning, and business intelligence — all built around a luxury e-commerce theme.

| Layer | Technology |
|---|---|
| Frontend | HTML / CSS / Vanilla JS |
| Backend API | FastAPI + SQLAlchemy |
| Database | SQLite |
| ML Pipeline | scikit-learn (KMeans, RF, GBM) |
| Dashboard | Static HTML (GitHub Pages) + Streamlit (local) |
| Data Generation | Faker + custom synthetic pipeline |

---

## Project Structure

```
Aurum_Tempus_demo/
│
├── docs/                       # Static site — served via GitHub Pages
│   ├── portal.html             # Entry page (site vs dashboard)
│   ├── index.html              # Customer-facing homepage
│   ├── collections.html        # Watch collections + cart
│   ├── heritage.html
│   ├── craftsmanship.html
│   ├── contact.html
│   ├── dashboard.html          # Static analytics dashboard
│   ├── styles.css
│   └── script.js               # API event logger + cart system
│
├── api/
│   └── main.py                 # FastAPI — /events, /orders endpoints
│
├── database/
│   ├── models.py               # SQLAlchemy ORM models
│   └── init_db.py              # Schema creation + product seeding
│
├── data/
│   └── synthetic.py            # Synthetic data generator (150 customers)
│
├── etl/
│   └── pipeline.py             # ETL pipeline
│
├── ml/
│   ├── models.py               # ML training pipeline
│   └── saved/                  # Trained model binaries (not in repo)
│       ├── segmentation_kmeans.pkl
│       ├── churn_rf.pkl
│       ├── ltv_gbr.pkl
│       └── recommendations.pkl
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard (local only)
│
├── aurum_tempus.db             # SQLite database (not in repo)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                        # Environment variables (not in repo)
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/mathias1801/front_end_-_Back_end_-_Dashboard.git
cd front_end_-_Back_end_-_Dashboard
pip install -r requirements.txt
```

### 2. Initialise database & generate data

```bash
python database/init_db.py       # creates tables, seeds 5 products
python data/synthetic.py         # generates 150 synthetic customers + events
```

### 3. Run the API

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

The frontend logs the following events to the API automatically:

| Event | Trigger |
|---|---|
| `page_view` | Every page load |
| `product_view` | Watch card scrolls into viewport |
| `add_to_cart` | Add to Cart button clicked |
| `checkout_start` | Checkout modal opened |
| `purchase` | Order confirmed (per line item) |

Each event carries a `session_id` (UUID, per browser session) for funnel analysis.

---

## Data

- **150 synthetic customers** generated with Faker
- **~179 orders** across 2021–2024 with seasonal weighting
- **~2,146 events** across the full purchase funnel
- **Total revenue: $2.4M USD**
- **5 watch collections** seeded: Perpetuelle I, Élégance Ultra Thin, Chronos Sport, Grande Complication, Ladies' Pavé

---

## ML Models

| Model | Algorithm | Output |
|---|---|---|
| Customer Segmentation | KMeans | 4 segment labels + RFM scores |
| Churn Prediction | Random Forest | Churn probability per customer |
| LTV Prediction | Gradient Boosting | Predicted lifetime value |
| Product Recommendations | Cosine Similarity | Top-N watches per customer |

---

## Disclaimer

All data is synthetic. Aurum Tempus is a fictional brand created for portfolio and learning purposes only.
