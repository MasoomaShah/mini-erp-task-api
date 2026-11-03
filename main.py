
import os
import sqlite3
import secrets

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


# Configuration
DB_PATH = os.getenv("DB_PATH", "data/tasks.db")
API_TOKEN = os.getenv("API_TOKEN")

security = HTTPBearer()


# Database initialization
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Mini ERP Task API",
    description="A small authenticated task management API",
    version="1.0.0",
    lifespan=lifespan
)


# Authentication
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="API_TOKEN is not configured"
        )

    if not secrets.compare_digest(
        credentials.credentials, API_TOKEN
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token"
        )

    return True


# Request models
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


# Health check (public)
@app.get("/health")
def health():
    return {"status": "healthy"}


# Retrieve tasks (protected)
@app.get("/tasks")
def get_tasks(auth: bool = Depends(verify_token)):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]


# Create task (protected)
@app.post("/tasks", status_code=201)
def create_task(
    task: TaskCreate,
    auth: bool = Depends(verify_token)
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (task.title,)
        )
        task_id = cursor.lastrowid

        return {
            "id": task_id,
            "title": task.title,
            "completed": False
        }


# Update task (protected)
@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    auth: bool = Depends(verify_token)
):
    updates = task.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No update fields supplied"
        )

    if "title" in updates and (
        updates["title"] is None or not updates["title"].strip()
    ):
        raise HTTPException(
            status_code=422,
            detail="Title cannot be empty"
        )

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        existing = conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        fields = list(updates.keys())
        assignments = ", ".join(
            f"{field} = ?" for field in fields
        )
        values = [
            int(value) if field == "completed" else value
            for field, value in updates.items()
        ]

        conn.execute(
            f"UPDATE tasks SET {assignments} WHERE id = ?",
            (*values, task_id)
        )

        updated = conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        result = dict(updated)
        result["completed"] = bool(result["completed"])

        return result
