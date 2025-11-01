import os
import sqlite3
import uvicorn

from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DB_PATH = os.environ.get("DB_PATH", "./db/tasks.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


def db_init():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'not_started',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            total_elapsed INTEGER DEFAULT 0,
            last_started TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/tasks")
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM tasks
        ORDER BY 
            completed_at IS NULL DESC,
            created_at DESC
        """
    )

    tasks = [dict(row) for row in cur.fetchall()]
    conn.close()
    return tasks


@app.post("/api/tasks")
def create_task(task: TaskCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tasks (title, description)
        VALUES (?, ?)
        """,
        (task.title, task.description or ""),
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()

    return {"id": task_id, "status": "success"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
