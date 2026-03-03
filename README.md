# 🏕️ Campsite Manager

A comprehensive management system for campsites, featuring a RESTful API and a modern web dashboard. This application allows campsite owners to effortlessly manage camping spots, customer data, and reservations.

## ✨ Features

* **Spots Management**: Add, view, and edit camping spots (tents, campers, cabins) with specific pricing.
* **Customer Database**: Register new customers, update their contact information, and ensure no duplicate emails exist.
* **Reservation System**: Book spots for customers with automatic date validation to prevent illogical bookings (e.g., end date before start date).
* **Modern Web UI**: A user-friendly, responsive web interface built with Streamlit.
* **Interactive API Docs**: Auto-generated Swagger UI for easy API testing and exploration.

## 🛠️ Tech Stack

* **Backend**: FastAPI, Python
* **Database**: PostgreSQL, SQLAlchemy (ORM)
* **Frontend**: Streamlit, Pandas, Requests
* **Infrastructure**: Docker & Docker Compose

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:
* Python 3.8 or higher
* Docker and Docker Compose (for running the database)

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone <your-repository-url>
cd campsite-manager

```

**2. Start the PostgreSQL Database**
The project uses Docker to quickly spin up a pre-configured database.

```bash
docker-compose up -d

```

*Note: The database runs on `localhost:5432` with user `admin` and password `secretpassword`.*

**3. Install Python Dependencies**
It is recommended to use a virtual environment.

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic streamlit requests pandas

```

## 💻 Running the Application

To run the full stack, you need to open **two separate terminal windows**.

**Terminal 1: Start the Backend API**

```bash
uvicorn main:app --reload

```

The API will start running at `http://127.0.0.1:8000`.

* You can view the interactive API documentation by visiting: `http://127.0.0.1:8000/docs`

**Terminal 2: Start the Web Dashboard**

```bash
streamlit run frontend.py

```

Your browser should automatically open the dashboard at `http://localhost:8501`.

## 🗂️ Project Structure

* `main.py` - The FastAPI application containing database models, Pydantic schemas, and API endpoints.
* `frontend.py` - The Streamlit web application serving as the UI.
* `docker-compose.yml` - Configuration for the PostgreSQL database container.
* `client.py` - (Legacy) A terminal-based Python client for interacting with the API.

