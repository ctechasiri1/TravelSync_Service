# ✈️ TravelSync Backend Service

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791.svg?logo=postgresql)

The official backend service for **TravelSync**, a production-ready iOS travel application designed to facilitate seamless itinerary planning and document management. 

This repository houses a high-performance, asynchronous REST API built with **FastAPI**. It is engineered with a strict 3-Tier Architecture to completely decouple database operations and business logic from HTTP routing, ensuring a highly scalable, testable, and maintainable codebase.

---

## ✨ Core Features

* **Stateless JWT Authentication:** Secure user registration and login flows using industry-standard JSON Web Tokens and robust password hashing via `pwdlib`.
* **Enterprise 3-Tier Architecture:** Strict separation of concerns utilizing Routers (HTTP traffic control), Services (business logic & validation), Repositories (data access layer), and Schemas (Pydantic data validation).
* **Complex Relational Data:** Fully cascaded SQLAlchemy ORM models managing Users, multi-day Trips, scheduled Events, and attached Documents.
* **Media & Document Processing:** * **Images:** Secure, automated processing of profile and cover photos using `Pillow` (includes EXIF orientation correction, Lanczos resampling, and UUID filename generation to prevent directory traversal).
  * **Documents:** Strict file-type validation and secure localized storage for trip itineraries (PDFs, TXTs, CSVs).
* **Async Database Operations:** Utilizes `aiosqlite` (local) and `asyncpg` (production) to ensure non-blocking, thread-safe database queries.

---

## 🏗️ Architecture & Project Structure

The codebase follows a modular, domain-driven structure utilizing Request-Scoped Dependency Injection:

```text
TravelSync_Service/
├── main.py               # ASGI application entry point & lifespan manager
├── config.py             # Pydantic BaseSettings for secure environment variables
├── database.py           # Async SQLAlchemy engine setup
├── dependencies.py       # FastAPI Dependency Injection (DI) factory & Auth wiring
├── auth.py               # Pure cryptography, password hashing, & JWT generation
├── models.py             # SQLAlchemy ORM models
├── schemas.py            # Pydantic models (Data Validation & Serialization)
├── routers/              # HTTP Traffic Controllers
│   └── users.py
├── services/             # Core Business Logic (Domain Layer)
│   └── user_service.py
├── repositories/         # Data Access Layer (Database Operations)
│   └── user_repository.py
├── utils/                # Helper modules
│   └── file_utils.py     
└── media/                # Local storage for user-uploaded assets
