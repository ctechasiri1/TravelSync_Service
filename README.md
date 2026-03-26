# ✈️ TravelSync Backend Service

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791.svg?logo=postgresql)

The official backend service for **TravelSync**, a production-ready iOS travel application designed to facilitate seamless itinerary planning and document management. 

This repository houses a high-performance, asynchronous REST API built with **FastAPI**. It is engineered with a strict Service Layer architecture to decouple business logic from HTTP routing, ensuring a scalable, testable, and maintainable codebase.

---

## ✨ Core Features

* **Stateless JWT Authentication:** Secure user registration and login flows using industry-standard JSON Web Tokens and Argon2/Bcrypt password hashing.
* **Complex Relational Data:** Fully cascaded SQLAlchemy ORM models managing Users, multi-day Trips, scheduled Events, and attached Documents.
* **Media & Document Processing:** * **Images:** Secure, automated processing of profile and cover photos using `Pillow` (includes EXIF orientation correction, Lanczos resampling, and UUID filename generation to prevent directory traversal).
  * **Documents:** Strict file-type validation and secure localized storage for trip itineraries (PDFs, TXTs, CSVs).
* **Clean Architecture:** Strict separation of concerns utilizing Routers (traffic control), Services (business logic), and Schemas (Pydantic data validation).
* **Async Database Operations:** Utilizes `aiosqlite` (local) and `asyncpg` (production) to ensure non-blocking, thread-safe database queries.

---

## 🏗️ Architecture & Project Structure

The codebase follows a modular, domain-driven structure:

```text
TravelSync_Service/
├── main.py               # ASGI application entry point & lifespan manager
├── config.py             # Pydantic BaseSettings for secure environment variables
├── database.py           # Async SQLAlchemy engine & dependency injection
├── auth.py               # Cryptography, password hashing, & JWT generation
├── models.py             # SQLAlchemy ORM models (Database Layer)
├── schemas.py            # Pydantic models (Data Validation & Serialization Layer)
├── routers/              # FastAPI APIRouters (HTTP Traffic Controllers)
│   └── users.py
├── services/             # Core Business Logic (Decoupled from HTTP)
│   └── user_service.py
├── utils/                # Helper modules
│   └── file_utils.py     # Image & Document processing logic
└── media/                # Local storage for user-uploaded assets
