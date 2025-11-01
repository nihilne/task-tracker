import os
import sqlite3

from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://enitoxy.github.io", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM tasks
        WHERE ID = ?
        """,
        (task_id,),
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.commit()
    conn.close()
    return {"deleted_id": task_id, "status": "success"}


@app.post("/api/tasks/{task_id}/start")
def start_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now().isoformat()

    cur.execute(
        """
        UPDATE tasks 
        SET status = 'active',
            started_at = COALESCE(started_at, ?),
            last_started = ?
        WHERE id = ?
        """,
        (now, now, task_id),
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.commit()
    conn.close()
    return {"status": "success"}


@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: int):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT last_started, total_elapsed FROM tasks WHERE id = ?", (task_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    if row["last_started"]:
        last_started = datetime.fromisoformat(row["last_started"])
        elapsed = (datetime.now() - last_started).total_seconds()
        new_total = row["total_elapsed"] + elapsed

        c.execute(
            """
            UPDATE tasks
            SET status = 'paused',
                total_elapsed = ?,
                last_started = NULL
            WHERE id = ?
            """,
            (new_total, task_id),
        )

    conn.commit()
    conn.close()
    return {"status": "success"}


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        "SELECT last_started, total_elapsed, status FROM tasks WHERE id = ?",
        (task_id,),
    )
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    total_elapsed = row["total_elapsed"]
    if row["last_started"] and row["status"] == "active":
        last_started = datetime.fromisoformat(row["last_started"])
        elapsed = (datetime.now() - last_started).total_seconds()
        total_elapsed += elapsed

    now = datetime.now().isoformat()
    c.execute(
        """
        UPDATE tasks
        SET status = 'completed',
            completed_at = ?,
            total_elapsed = ?,
            last_started = NULL
        WHERE id = ?
        """,
        (now, total_elapsed, task_id),
    )

    conn.commit()
    conn.close()
    return {"status": "success"}


db_init()
