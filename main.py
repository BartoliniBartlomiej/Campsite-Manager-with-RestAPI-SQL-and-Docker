from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import Optional
import os


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@localhost:5432/camping_db"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database models
class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    price = Column(Float)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)  # unique=True -> no 2 same customers (emails)
    phone = Column(String)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))  # Wskazuje na id w tabeli customers
    spot_id = Column(Integer, ForeignKey("spots.id"))  # Wskazuje na id w tabeli spots
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="confirmed")  # Np. confirmed, cancelled, completed

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("No connection with database (OK with tests on Github Actions.")


# --- Pydantic / validation of input data
class SpotCreate(BaseModel):
    name: str
    type: str
    price: float


class SpotUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    price: Optional[float] = None


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class ReservationCreate(BaseModel):
    customer_id: int
    spot_id: int
    start_date: date
    end_date: date


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ReservationUpdate(BaseModel):
    customer_id: Optional[int] = None
    spot_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


app = FastAPI(title="Camping Manager API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Database linked"}


@app.get("/spots")
def get_spots(db: Session = Depends(get_db)):
    spots = db.query(Spot).all()
    return spots


@app.post("/spots")
def create_spot(spot: SpotCreate, db: Session = Depends(get_db)):
    new_spot = Spot(name=spot.name, type=spot.type, price=spot.price)

    db.add(new_spot)
    db.commit()

    db.refresh(new_spot)

    return new_spot


@app.delete("/spots/{spot_id}")
def delete_spot(spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(Spot).filter(Spot.id == spot_id).first()

    if spot is None:
        raise HTTPException(status_code=404, detail="No spot with this ID")

    db.delete(spot)
    db.commit()

    return {"message": f"Spot {spot_id} deleted"}


@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # checking if the customer already exist in db
    existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email occupied!")

    new_customer = Customer(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@app.post("/reservations")
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    # 1. Prosta walidacja dat
    if reservation.start_date >= reservation.end_date:
        raise HTTPException(status_code=400, detail="Data wyjazdu musi być późniejsza niż data przyjazdu!")

    # 2. Tworzymy obiekt rezerwacji
    new_reservation = Reservation(
        customer_id=reservation.customer_id,
        spot_id=reservation.spot_id,
        start_date=reservation.start_date,
        end_date=reservation.end_date
    )

    # 3. Zapisujemy w bazie
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation


@app.get("/reservations")
def get_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()


@app.patch("/spots/{spot_id}")
def update_spot(spot_id: int, spot_update: SpotUpdate, db: Session = Depends(get_db)):
    # 1. Szukamy miejsca w bazie
    spot = db.query(Spot).filter(Spot.id == spot_id).first()

    if spot is None:
        raise HTTPException(status_code=404, detail="No spot with this ID")

    # 2. Wyciągamy tylko te pola, które zostały przesłane (wykluczamy puste/None)
    # Uwaga: w starszychwersjach Pydantic używało się .dict(exclude_unset=True)
    update_data = spot_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    # 3. Aktualizujemy atrybuty obiektu w bazie
    for key, value in update_data.items():
        setattr(spot, key, value)

    # 4. Zapisujemy zmiany
    db.commit()
    db.refresh(spot)

    return {"message": f"Spot {spot_id} updated successfully", "spot": spot}


@app.patch("/customers/{customer_id}")
def update_customer(customer_id: int, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Jeśli zmieniamy email, sprawdzamy czy nowy nie jest już w bazie
    if customer_update.email is not None and customer_update.email != customer.email:
        existing_email = db.query(Customer).filter(Customer.email == customer_update.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="This email is already taken!")

    update_data = customer_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer


@app.patch("/reservations/{reservation_id}")
def update_reservation(reservation_id: int, reservation_update: ReservationUpdate, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    update_data = reservation_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    for key, value in update_data.items():
        setattr(reservation, key, value)

    # Sprawdzamy, czy po aktualizacji daty nadal mają sens
    if reservation.start_date >= reservation.end_date:
        db.rollback()  # Cofamy ewentualne przypisania
        raise HTTPException(status_code=400, detail="End date must be after start date!")

    db.commit()
    db.refresh(reservation)
    return reservation
