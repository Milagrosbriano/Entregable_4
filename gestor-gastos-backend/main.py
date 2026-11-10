import os
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "data" / "gastos.db"))
CATEGORIAS = ["Comida", "Transporte", "Ocio", "Servicios", "Otros"]

app = FastAPI(title="Gestor de Gastos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080"
    ).split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Métrica de negocio: cantidad de gastos creados, separada por categoría.
gastos_creados = Counter(
    "gastos_creados_total",
    "Cantidad de gastos creados",
    ["categoria"],
)


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT NOT NULL,
                fecha TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


init_db()


class GastoIn(BaseModel):
    descripcion: str
    monto: float
    categoria: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/categorias")
def categorias():
    return CATEGORIAS


@app.get("/api/gastos")
def listar_gastos():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM gastos ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@app.post("/api/gastos")
def crear_gasto(gasto: GastoIn):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "INSERT INTO gastos (descripcion, monto, categoria) VALUES (?, ?, ?)",
            (gasto.descripcion, gasto.monto, gasto.categoria),
        )
        gastos_creados.labels(categoria=gasto.categoria).inc()
        return {"id": cur.lastrowid, **gasto.model_dump()}


# Métricas y documentación son responsabilidad del backend.
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
