import random
import sys
import os
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Customer, Order, OrderItem, Event, OrderStatus, EventType

# ── Config ─────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

fake = Faker()
random.seed(42)
Faker.seed(42)

# ── Realistic Parameters ───────────────────────────────────────

# Watches with their IDs and price (must match seeded products)
PRODUCTS = [
    {"id": 1, "name": "Perpetuelle I",       "price": 8900,  "collection": "classic", "weight": 35},
    {"id": 2, "name": "Élégance Ultra Thin", "price": 12500, "collection": "classic", "weight": 20},
    {"id": 3, "name": "Chronos Sport",       "price": 9800,  "collection": "sport",   "weight": 25},
    {"id": 4, "name": "Grande Complication", "price": 24900, "collection": "grand",   "weight": 5},
    {"id": 5, "name": "Ladies' Pavé",        "price": 14500, "collection": "ladies",  "weight": 15},
]

# Customer segments with realistic behavioural profiles
SEGMENTS = {
    "high_value_collector": {
        "weight"          : 10,
        "orders_range"    : (1, 2),
        "product_weights" : [15, 20, 15, 40, 10],
        "countries"       : ["CH", "US", "AE", "HK", "GB"],
    },
    "classic_enthusiast": {
        "weight"          : 30,
        "orders_range"    : (1, 2),
        "product_weights" : [40, 30, 10, 5, 15],
        "countries"       : ["DE", "FR", "GB", "IT", "US"],
    },
    "sport_buyer": {
        "weight"          : 25,
        "orders_range"    : (1, 1),
        "product_weights" : [10, 5, 70, 5, 10],
        "countries"       : ["US", "AU", "NO", "CA", "GB"],
    },
    "gift_buyer": {
        "weight"          : 20,
        "orders_range"    : (1, 1),
        "product_weights" : [25, 15, 20, 5, 35],
        "countries"       : ["US", "GB", "FR", "SG", "JP"],
    },
    "one_time_buyer": {
        "weight"          : 15,
        "orders_range"    : (1, 1),
        "product_weights" : [30, 20, 25, 5, 20],
        "countries"       : ["US", "DE", "FR", "IT", "ES"],
    },
}

# Seasonality multipliers by month (luxury watches peak Dec, Q1 dip)
SEASONALITY = {
    1: 0.7, 2: 0.75, 3: 0.85, 4: 0.9,  5: 0.95, 6: 1.0,
    7: 0.9, 8: 0.85, 9: 1.0,  10: 1.1, 11: 1.2, 12: 1.5,
}

# Funnel conversion rates — how many events before a purchase
FUNNEL = {
    "page_views_per_session"   : (3, 12),
    "product_views_per_session": (1, 4),
    "add_to_cart_rate"         : 0.35,
    "checkout_start_rate"      : 0.60,
    "purchase_rate"            : 0.75,
}


# ── Helpers ────────────────────────────────────────────────────
def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def seasonal_date(year: int) -> datetime:
    """Pick a random date weighted by seasonality."""
    month_weights = [SEASONALITY[m] for m in range(1, 13)]
    month = weighted_choice(range(1, 13), month_weights)
    day   = random.randint(1, 28)
    hour  = random.randint(8, 22)
    return datetime(year, month, day, hour, random.randint(0, 59))


# ── Generators ─────────────────────────────────────────────────
def generate_customers(n: int = 500) -> list[Customer]:
    customers = []
    segment_names    = list(SEGMENTS.keys())
    segment_weights  = [SEGMENTS[s]["weight"] for s in segment_names]

    for _ in range(n):
        segment  = weighted_choice(segment_names, segment_weights)
        country  = random.choice(SEGMENTS[segment]["countries"])
        created  = random_date(datetime(2021, 1, 1), datetime(2024, 6, 1))

        customers.append(Customer(
            name       = fake.name(),
            email      = fake.unique.email(),
            country    = country,
            city       = fake.city(),
            created_at = created,
            # Store segment as a note in city field — we'll use a proper column in ETL
        ))

    return customers


def generate_orders_and_events(
    customers : list[Customer],
    db        : Session,
    start_year: int = 2021,
    end_year  : int = 2024,
) -> None:
    """
    For each customer, generate a realistic purchase history
    and the browsing events that led to each purchase.
    """
    segment_names   = list(SEGMENTS.keys())
    segment_weights = [SEGMENTS[s]["weight"] for s in segment_names]
    product_ids     = [p["id"] for p in PRODUCTS]

    for customer in customers:
        segment_name    = weighted_choice(segment_names, segment_weights)
        segment         = SEGMENTS[segment_name]
        n_orders        = random.randint(*segment["orders_range"])
        product_weights = segment["product_weights"]

        for _ in range(n_orders):
            year         = random.randint(start_year, end_year)
            order_date   = seasonal_date(year)
            session_id   = fake.uuid4()
            product      = weighted_choice(PRODUCTS, product_weights)

            # ── Pre-purchase funnel events ──────────────────────
            events = []

            # Page views
            n_page_views = random.randint(*FUNNEL["page_views_per_session"])
            for i in range(n_page_views):
                events.append(Event(
                    customer_id = customer.id,
                    product_id  = None,
                    event_type  = EventType.page_view,
                    session_id  = session_id,
                    created_at  = order_date - timedelta(minutes=n_page_views - i + 20),
                ))

            # Product views
            n_product_views = random.randint(*FUNNEL["product_views_per_session"])
            viewed_products = random.choices(PRODUCTS, weights=product_weights, k=n_product_views)
            for i, vp in enumerate(viewed_products):
                events.append(Event(
                    customer_id = customer.id,
                    product_id  = vp["id"],
                    event_type  = EventType.product_view,
                    session_id  = session_id,
                    created_at  = order_date - timedelta(minutes=n_product_views - i + 10),
                ))

            # Add to cart
            if random.random() < FUNNEL["add_to_cart_rate"]:
                events.append(Event(
                    customer_id = customer.id,
                    product_id  = product["id"],
                    event_type  = EventType.add_to_cart,
                    session_id  = session_id,
                    created_at  = order_date - timedelta(minutes=5),
                ))

            # Checkout start
            if random.random() < FUNNEL["checkout_start_rate"]:
                events.append(Event(
                    customer_id = customer.id,
                    product_id  = None,
                    event_type  = EventType.checkout_start,
                    session_id  = session_id,
                    created_at  = order_date - timedelta(minutes=2),
                ))

            db.add_all(events)

            # ── Order ───────────────────────────────────────────
            # Occasionally buy 2 of the same or an additional watch
            qty        = 2 if random.random() < 0.05 else 1
            total      = product["price"] * qty
            order_stat = random.choices(
                list(OrderStatus),
                weights=[5, 70, 15, 8, 2],
                k=1
            )[0]

            order = Order(
                customer_id = customer.id,
                status      = order_stat,
                total_chf   = total,
                created_at  = order_date,
            )
            db.add(order)
            db.flush()

            db.add(OrderItem(
                order_id   = order.id,
                product_id = product["id"],
                quantity   = qty,
                unit_price = product["price"],
            ))

            # Purchase event
            db.add(Event(
                customer_id = customer.id,
                product_id  = product["id"],
                event_type  = EventType.purchase,
                session_id  = session_id,
                created_at  = order_date,
            ))

        db.commit()
        print(f"  Generated data for customer {customer.id} ({segment_name})")


# ── Main ───────────────────────────────────────────────────────
def run(n_customers: int = 250):
    print(f"Generating {n_customers} customers...")
    with SessionLocal() as db:
        customers = generate_customers(n_customers)
        db.add_all(customers)
        db.flush()

        print("Generating orders and events...")
        generate_orders_and_events(customers, db)

    print("Done. Synthetic data generation complete.")


if __name__ == "__main__":
    run(n_customers=150)