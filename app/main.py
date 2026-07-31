from dataclasses import Field
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic.fields import Field

from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from .database import get_db, init_db, seed_db

app = FastAPI(title="Figure Ticketing API - Debugging Olympics")


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_db(hash_password)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: int = Field(gt=0, lt=6)


class TicketStatusUpdate(BaseModel):
    status: str


@app.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (credentials.username,)
    ).fetchone()
    conn.close()
    if row is None or not verify_password(credentials.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": row["username"], "role": row["role"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/tickets")
def list_tickets(search: str = "", current_user=Depends(get_current_user)):
    conn = get_db()
    query = "Select * FROM tickets WHERE title LIKE ? OR description LIKE ?"
    rows = conn.execute(query, (f"%{search}%", f"%{search}%")).fetchall()

    conn.close()
    return [dict(row) for row in rows]


@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate, current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tickets (title, description, priority, status, owner) VALUES (?, ?, ?, 'open', ?)",
        (ticket.title, ticket.description, ticket.priority, current_user["username"]),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return {
        "id": ticket_id,
        "title": ticket.title,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": "open",
        "owner": current_user["username"],
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, current_user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return dict(row)


@app.put("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int, update: TicketStatusUpdate, current_user=Depends(require_admin)
):
    conn = get_db()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (update.status, ticket_id))
    conn.commit()
    conn.close()
    return {"id": ticket_id, "status": update.status}


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, current_user=Depends(require_admin)):
    conn = get_db()
    conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return None
