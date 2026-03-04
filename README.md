
# 🏕️ Campsite Manager (REST API + UI)

A comprehensive system for managing a campsite and RV park. The application enables seamless management of customers, camping spots, and reservations. The project features a high-performance backend built with FastAPI, an interactive frontend powered by Streamlit, and a PostgreSQL relational database. 

The entire stack is containerized using Docker and is covered by automated testing with a Continuous Integration (CI) pipeline configured via GitHub Actions.

## 🚀 Tech Stack

* **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Pydantic
* **Frontend:** Streamlit, Pandas, Requests
* **Database:** PostgreSQL (production/Docker environment), SQLite (local testing environment)
* **Testing:** Pytest, HTTPX
* **DevOps:** Docker, Docker Compose, GitHub Actions (CI)

## 🏗️ System Architecture



The application relies on three primary, interconnected containers orchestrated by Docker Compose:
1. `db`: A PostgreSQL database container configured with a persistent Docker Volume to ensure data retention across container restarts.
2. `api`: The backend container serving the REST API endpoints and handling business logic.
3. `frontend`: The Streamlit-based graphical user interface for end-users.

## ⚙️ Getting Started (Docker)

The recommended and most straightforward way to run the project is using Docker. There is no need to install Python or PostgreSQL locally on your host machine.

1. Clone the repository:
```bash
git clone [https://github.com/BartoliniBartlomiej/Campsite-Manager-with-RestAPI-SQL-and-Docker.git](https://github.com/BartoliniBartlomiej/Campsite-Manager-with-RestAPI-SQL-and-Docker.git)
cd Campsite-Manager-with-RestAPI-SQL-and-Docker
```

2. Build and run the containers using Docker Compose:
```bash
docker-compose up --build

```


*(To run the containers in the background/detached mode, append the `-d` flag).*
3. Access the application:
* **Frontend UI (Streamlit):** [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
* **API Documentation (Swagger UI):** [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)



## 🧪 Testing and CI/CD

The project includes unit and integration tests covering core business logic (e.g., reservation date validation, data integrity). During testing, the application dynamically switches to an isolated, in-memory SQLite database to prevent modifications to the main data.

**Running tests locally:**

```bash
# Requires an active virtual environment and installed dependencies from requirements.txt
pytest -v

```

**Continuous Integration (CI):**
This repository is integrated with GitHub Actions. Upon every `push` or `pull_request` to the main branch, the CI pipeline automatically sets up the Python environment, installs dependencies, and executes the Pytest test suite to ensure code stability and prevent regressions.

## 🛑 Stopping the Environment

To gracefully stop the application while preserving all database records (thanks to Docker Volumes), run:

```bash
docker-compose down

```
