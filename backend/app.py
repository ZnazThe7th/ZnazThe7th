from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "appointments.sqlite3"
SCHEMA_PATH = BASE_DIR / "schema.sql"

app = FastAPI(title="AI Appointment Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ServiceIn(BaseModel):
    name: str = Field(..., min_length=2)
    duration_minutes: int = Field(..., ge=15)
    price_cents: int = Field(..., ge=0)


class ClientIn(BaseModel):
    full_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=7)
    email: str | None = None
    notes: str | None = None


class AppointmentIn(BaseModel):
    service_id: int
    client_id: int
    start_time: str
    end_time: str


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)


def fetch_all(connection: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cursor = connection.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/services")
def list_services() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return fetch_all(connection, "SELECT * FROM services ORDER BY id DESC")


@app.post("/services", status_code=201)
def create_service(service: ServiceIn) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO services (name, duration_minutes, price_cents) VALUES (?, ?, ?)",
            (service.name, service.duration_minutes, service.price_cents),
        )
        connection.commit()
        service_id = cursor.lastrowid
    return {"id": service_id, **service.model_dump()}


@app.get("/clients")
def list_clients() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return fetch_all(connection, "SELECT * FROM clients ORDER BY id DESC")


@app.post("/clients", status_code=201)
def create_client(client: ClientIn) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO clients (full_name, phone, email, notes) VALUES (?, ?, ?, ?)",
            (client.full_name, client.phone, client.email, client.notes),
        )
        connection.commit()
        client_id = cursor.lastrowid
    return {"id": client_id, **client.model_dump()}


@app.get("/appointments")
def list_appointments() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return fetch_all(
            connection,
            """
            SELECT appointments.*, services.name AS service_name, clients.full_name AS client_name
            FROM appointments
            JOIN services ON services.id = appointments.service_id
            JOIN clients ON clients.id = appointments.client_id
            ORDER BY appointments.start_time ASC
            """,
        )


@app.post("/appointments", status_code=201)
def create_appointment(appointment: AppointmentIn) -> dict[str, Any]:
    with get_connection() as connection:
        service_exists = connection.execute(
            "SELECT 1 FROM services WHERE id = ?", (appointment.service_id,)
        ).fetchone()
        client_exists = connection.execute(
            "SELECT 1 FROM clients WHERE id = ?", (appointment.client_id,)
        ).fetchone()
        if not service_exists or not client_exists:
            raise HTTPException(status_code=404, detail="Service or client not found")

        conflict = connection.execute(
            """
            SELECT 1 FROM appointments
            WHERE (? < end_time AND ? > start_time)
            """,
            (appointment.start_time, appointment.end_time),
        ).fetchone()
        if conflict:
            raise HTTPException(status_code=409, detail="Time slot unavailable")

        cursor = connection.execute(
            """
            INSERT INTO appointments (service_id, client_id, start_time, end_time)
            VALUES (?, ?, ?, ?)
            """,
            (
                appointment.service_id,
                appointment.client_id,
                appointment.start_time,
                appointment.end_time,
            ),
        )
        connection.commit()
        appointment_id = cursor.lastrowid

    return {"id": appointment_id, **appointment.model_dump(), "status": "booked"}
