from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Product, Customer, Order, OrderItem, Event, OrderStatus, EventType

# ── Setup ──────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Aurum Tempus API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB Dependency ──────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Pydantic Schemas ───────────────────────────────────────────
class EventIn(BaseModel):
    event_type  : str
    product_id  : Optional[int] = None
    customer_id : Optional[int] = None
    session_id  : Optional[str] = None

class OrderItemIn(BaseModel):
    product_id : int
    quantity   : int
    unit_price : float

class OrderIn(BaseModel):
    customer_name    : str
    customer_email   : str
    customer_country : Optional[str] = None
    customer_city    : Optional[str] = None
    items            : list[OrderItemIn]
    session_id       : Optional[str] = None


# ── Products ───────────────────────────────────────────────────
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "id"         : p.id,
            "name"       : p.name,
            "collection" : p.collection.value,
            "price_chf"  : p.price_chf,
            "stock"      : p.stock,
            "description": p.description,
        }
        for p in products
    ]

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id"         : p.id,
        "name"       : p.name,
        "collection" : p.collection.value,
        "price_chf"  : p.price_chf,
        "stock"      : p.stock,
        "description": p.description,
    }


# ── Events ─────────────────────────────────────────────────────
@app.post("/events", status_code=201)
def log_event(payload: EventIn, db: Session = Depends(get_db)):
    try:
        event_type = EventType[payload.event_type]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid event_type: {payload.event_type}")

    event = Event(
        event_type  = event_type,
        product_id  = payload.product_id,
        customer_id = payload.customer_id,
        session_id  = payload.session_id,
        created_at  = datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    return {"status": "logged", "event_type": payload.event_type}


# ── Orders ─────────────────────────────────────────────────────
@app.post("/orders", status_code=201)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):

    # Get or create customer
    customer = db.query(Customer).filter(Customer.email == payload.customer_email).first()
    if not customer:
        customer = Customer(
            name       = payload.customer_name,
            email      = payload.customer_email,
            country    = payload.customer_country,
            city       = payload.customer_city,
            created_at = datetime.utcnow(),
        )
        db.add(customer)
        db.flush()  # get customer.id without full commit

    # Validate products and calculate total
    total = 0.0
    items = []
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"{product.name} has insufficient stock")

        total += item.unit_price * item.quantity
        items.append((product, item))

    # Create order
    order = Order(
        customer_id = customer.id,
        status      = OrderStatus.confirmed,
        total_chf   = total,
        created_at  = datetime.utcnow(),
    )
    db.add(order)
    db.flush()

    # Create order items + decrement stock
    for product, item in items:
        db.add(OrderItem(
            order_id   = order.id,
            product_id = product.id,
            quantity   = item.quantity,
            unit_price = item.unit_price,
        ))
        product.stock -= item.quantity

    # Log purchase event
    db.add(Event(
        customer_id = customer.id,
        event_type  = EventType.purchase,
        session_id  = payload.session_id,
        created_at  = datetime.utcnow(),
    ))

    db.commit()

    return {
        "status"      : "confirmed",
        "order_id"    : order.id,
        "customer_id" : customer.id,
        "total_chf"   : total,
    }


# ── Health Check ───────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "Aurum Tempus API"}