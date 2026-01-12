from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "knowledge.db"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="外挂大脑知识库")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_db() as connection:
        connection.execute(SCHEMA)
        connection.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def fetch_notes(query: str | None = None) -> list[sqlite3.Row]:
    sql = "SELECT * FROM notes"
    params: Iterable[str] = []
    if query:
        sql += " WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?"
        like_query = f"%{query}%"
        params = [like_query, like_query, like_query]
    sql += " ORDER BY updated_at DESC"
    with get_db() as connection:
        return list(connection.execute(sql, params))


def fetch_note(note_id: int) -> sqlite3.Row | None:
    with get_db() as connection:
        return connection.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()


@app.get("/")
def index(request: Request, q: str | None = None) -> object:
    notes = fetch_notes(q)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "notes": notes,
            "query": q or "",
        },
    )


@app.post("/notes")
def create_note(
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
) -> RedirectResponse:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_db() as connection:
        connection.execute(
            "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (title.strip(), content.strip(), tags.strip(), now, now),
        )
        connection.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/notes/{note_id}")
def view_note(request: Request, note_id: int) -> object:
    note = fetch_note(note_id)
    if note is None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("detail.html", {"request": request, "note": note})


@app.get("/notes/{note_id}/edit")
def edit_note(request: Request, note_id: int) -> object:
    note = fetch_note(note_id)
    if note is None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("edit.html", {"request": request, "note": note})


@app.post("/notes/{note_id}/edit")
def update_note(
    note_id: int,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
) -> RedirectResponse:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_db() as connection:
        connection.execute(
            """
            UPDATE notes
            SET title = ?, content = ?, tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (title.strip(), content.strip(), tags.strip(), now, note_id),
        )
        connection.commit()
    return RedirectResponse(url=f"/notes/{note_id}", status_code=303)


@app.post("/notes/{note_id}/delete")
def delete_note(note_id: int) -> RedirectResponse:
    with get_db() as connection:
        connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        connection.commit()
    return RedirectResponse(url="/", status_code=303)
