from sqlalchemy import create_engine
from models import Base, Product, Collection
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    Base.metadata.create_all(engine)
    seed_products()
    print("Database initialised.")

def seed_products():
    """Insert the 5 Aurum Tempus watches."""
    products = [
        Product(name="Perpetuelle I",       collection=Collection.classic, price_chf=8900,  stock=15, description="The original expression of the Vallat philosophy."),
        Product(name="Élégance Ultra Thin", collection=Collection.classic, price_chf=12500, stock=10, description="At 5.9mm, the thinnest movement ever produced in-house."),
        Product(name="Chronos Sport",       collection=Collection.sport,   price_chf=9800,  stock=20, description="A flyback chronograph born from an Everest expedition brief."),
        Product(name="Grande Complication", collection=Collection.grand,   price_chf=24900, stock=3,  description="The pinnacle of horological ambition. 12 produced annually."),
        Product(name="Ladies' Pavé",        collection=Collection.ladies,  price_chf=14500, stock=8,  description="186 VVS diamonds, mother-of-pearl dial, white gold case."),
    ]
    with Session(engine) as session:
        # Only seed if empty
        if session.query(Product).count() == 0:
            session.add_all(products)
            session.commit()
            print("Products seeded.")

if __name__ == "__main__":
    init_db()