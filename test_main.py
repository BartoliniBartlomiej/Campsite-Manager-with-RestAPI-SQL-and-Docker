from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import our application, database from main.py
from main import app, Base, get_db

# 1. RAM Database (SQLite) configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Creating table in test base
Base.metadata.create_all(bind=engine)


# 3. Override functions for database
# Thanks to that, those endpoints will not connect to main Database in PR
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# 4. Test client
client = TestClient(app)


# Actual tests

def test_read_root():
    """Main API endpoint test"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Database linked"}


def test_create_spot():
    response = client.post(
        "/spots",
        json={"name": "Test Sector", "type": "Tent", "price": 45.5}
    )

    # Checking if server return OK status
    assert response.status_code == 200

    # Checking if the data is correct
    data = response.json()
    assert data["name"] == "Test Sector"
    assert data["type"] == "Tent"
    assert data["price"] == 45.5
    assert "id" in data  # auto ID from database ?


def test_update_spot_success():
    create_res = client.post("/spots", json={
        "name": "Stare Pole",
        "type": "namiot",
        "price": 40.0
    })
    spot_id = create_res.json()["id"]

    updated_data = {
        "name": "Nowe Pole Premium",
        "type": "kamper",
        "price": 85.0
    }

    update_res = client.patch(f"/spots/{spot_id}", json=updated_data)

    assert update_res.status_code == 200

    response_data = update_res.json()

    assert response_data["message"] == f"Spot {spot_id} updated successfully"

    spot_data = response_data["spot"]
    assert spot_data["name"] == "Nowe Pole Premium"
    assert spot_data["type"] == "kamper"
    assert spot_data["price"] == 85.0


def test_update_spot_not_found():
    updated_data = {
        "name": "Widmo"
    }

    res = client.patch("/spots/9999", json=updated_data)

    assert res.status_code == 404 # Not found

def test_create_double_customers():
    first_response = client.post(
        "/customers",
        json={
            "first_name": "Test",
            "last_name": "First",
            "email": "test@example.com",
            "phone": "123456789"
        }
    )
    second_response = client.post(
        "/customers",
        json={
            "first_name": "Test",
            "last_name": "Second",
            "email": "test@example.com",
            "phone": "000000000"
        }
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400 # ERROR - second customer with the same email


def test_get_spots():
    response = client.get("/spots")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)  # make it sure it is a LIST
    assert len(data) >= 1 # minimum 1 (def test_create_spot())

    # Is data correct?
    assert data[0]["name"] == "Test Sector"

def test_create_reservation_invalid_dates():
    """Test validation against invalid reservation dates"""

    # 1. First, add a customer to the test database
    customer_response = client.post(
        "/customers",
        json={
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan.kowalski@example.com",
            "phone": "123456789"
        }
    )
    assert customer_response.status_code == 200
    customer_id = customer_response.json()["id"]

    # 2. Then, add a spot to the test database
    spot_response = client.post(
        "/spots",
        json={"name": "Sektor VIP", "type": "kamper", "price": 100.0}
    )
    assert spot_response.status_code == 200
    spot_id = spot_response.json()["id"]

    # 3. Try to create a reservation with INVALID dates (departure before arrival)
    bad_reservation = {
        "customer_id": customer_id,
        "spot_id": spot_id,
        "start_date": "2024-08-15",
        "end_date": "2024-08-10"  # Error!
    }

    response = client.post("/reservations", json=bad_reservation)

    # 4. Check if the API behaved correctly (blocked the action)
    assert response.status_code == 400
    assert response.json()["detail"] == "Data wyjazdu musi być późniejsza niż data przyjazdu!"


def test_create_reservation_success():
    """Test successful reservation creation"""

    # 1. Create a customer
    customer_res = client.post("/customers", json={
        "first_name": "Anna", "last_name": "Nowak",
        "email": "anna.nowak@example.com", "phone": "987654321"
    })
    customer_id = customer_res.json()["id"]

    # 2. Create a spot
    spot_res = client.post("/spots", json={
        "name": "Pole Namiotowe 1", "type": "namiot", "price": 50.0
    })
    spot_id = spot_res.json()["id"]

    # 3. Create a VALID reservation (departure after arrival)
    good_reservation = {
        "customer_id": customer_id,
        "spot_id": spot_id,
        "start_date": "2024-08-10",
        "end_date": "2024-08-15"  # Correct!
    }

    response = client.post("/reservations", json=good_reservation)

    # 4. Check if the API returned 200 OK (success)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id