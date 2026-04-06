# Aurum Tempus — Luxury Watch E-Commerce Portfolio

> A full-stack data science portfolio project simulating the digital presence and analytics infrastructure of a fictional Geneva watchmaker.

---

## Overview

Aurum Tempus is a portfolio piece demonstrating end-to-end data engineering, backend API development, machine learning, and business intelligence — all built around a luxury e-commerce theme.

| Layer | Technology |
|---|---|
| Frontend | HTML / CSS / Vanilla JS |
| Backend API | FastAPI + SQLAlchemy |
| Database | SQLite |
| ML Pipeline | scikit-learn (KMeans, RF, GBM) |
| Dashboard | Streamlit + Plotly |
| Data Generation | Faker + custom synthetic pipeline |

---

## Project Structure

```
aurum_tempus/
│
├── frontend/               # Static site (HTML/CSS/JS)
│   ├── index.html
│   ├── collections.html
│   ├── heritage.html
│   ├── craftsmanship.html
│   ├── contact.html
│   ├── styles.css
│   └── script.js           # API-connected event logger + cart
│
├── api/                    # FastAPI backend
│   └── main.py             # /events, /orders endpoints
│
├── database/
│   ├── models.py           # SQLAlchemy ORM models
│   └── init_db.py          # Schema creation + product seeding
│
├── ml/                     # ML pipeline
│   ├── train.py            # Segment, churn, LTV, recommendations
│   └── ...
│
├── app.py                  # Streamlit analytics dashboard
├── synthetic.py            # Synthetic data generator (500 customers)
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/<your-username>/aurum-tempus.git
cd aurum-tempus
pip install -r requirements.txt
```

### 2. Initialise database & generate data

```bash
python database/init_db.py       # creates tables, seeds 5 products
python synthetic.py              # generates 500 synthetic customers + events
```

### 3. Run the API

```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Open the frontend

Open `frontend/index.html` in your browser (or serve with any static server).

### 5. Run the dashboard

```bash
streamlit run app.py
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

## ML Models

| Model | Algorithm | Output |
|---|---|---|
| Customer Segmentation | KMeans | Segment labels + RFM scores |
| Churn Prediction | Random Forest | Churn probability per customer |
| LTV Prediction | Gradient Boosting | Predicted lifetime value |
| Product Recommendations | Cosine Similarity | Top-N watches per customer |

---

## Disclaimer

All data is synthetic. Aurum Tempus is a fictional brand created for portfolio and learning purposes only.
