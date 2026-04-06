from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()


# ── Enums ──────────────────────────────────────────────────────
class OrderStatus(enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    shipped   = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class EventType(enum.Enum):
    page_view       = "page_view"
    product_view    = "product_view"
    add_to_cart     = "add_to_cart"
    checkout_start  = "checkout_start"
    purchase        = "purchase"

class Collection(enum.Enum):
    classic = "classic"
    sport   = "sport"
    grand   = "grand"
    ladies  = "ladies"


# ── Products ───────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), nullable=False)
    collection  = Column(Enum(Collection), nullable=False)
    price_chf   = Column(Float, nullable=False)
    stock       = Column(Integer, default=10)
    description = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")
    events      = relationship("Event",     back_populates="product")


# ── Customers ──────────────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    id         = Column(Integer, primary_key=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    country    = Column(String(60))
    city       = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")
    events = relationship("Event", back_populates="customer")


# ── Orders ─────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id          = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status      = Column(Enum(OrderStatus), default=OrderStatus.confirmed)
    total_chf   = Column(Float, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    customer    = relationship("Customer",   back_populates="orders")
    order_items = relationship("OrderItem",  back_populates="order")


# ── Order Items ────────────────────────────────────────────────
class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True)
    order_id   = Column(Integer, ForeignKey("orders.id"),   nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, default=1)
    unit_price = Column(Float,   nullable=False)

    order   = relationship("Order",   back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


# ── Events ─────────────────────────────────────────────────────
class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)  # null = anonymous
    product_id  = Column(Integer, ForeignKey("products.id"),  nullable=True)  # null for page_view
    event_type  = Column(Enum(EventType), nullable=False)
    session_id  = Column(String(64))   # groups events into browsing sessions
    created_at  = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="events")
    product  = relationship("Product",  back_populates="events")