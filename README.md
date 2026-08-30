# Expense API

[![CI](https://github.com/Acedpol/expense-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Acedpol/expense-api/actions/workflows/ci.yml)
![coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

API REST para gestión de gastos personales. Proyecto de portfolio con foco en **backend**: auth con JWT, CRUD, tests, Docker y CI/CD.

## Stack

- FastAPI + SQLAlchemy 2.0 + Alembic (migraciones versionadas del esquema)
- SQLite en local sin Docker (rápido para desarrollar) / PostgreSQL vía Docker Compose (real)
- JWT (OAuth2 password flow) para auth
- pytest + httpx para tests
- GitHub Actions para CI

## Arrancar en local (sin Docker, SQLite)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
alembic upgrade head
uvicorn app.main:app --reload
```

`pre-commit install` deja `ruff check --fix` y `ruff format` corriendo antes de cada commit, así un fallo de lint se detecta en tu máquina y no en el CI.

Docs interactivas en `http://localhost:8000/docs`.

## Migraciones (Alembic)

El esquema de la base de datos ya no lo crea la app al arrancar — lo crean las migraciones. Flujo habitual:

```bash
# después de cambiar un modelo en app/models/
alembic revision --autogenerate -m "descripción del cambio"
# revisar el archivo generado en alembic/versions/ antes de aplicarlo
alembic upgrade head

# deshacer la última migración
alembic downgrade -1

# ver el historial / en qué revisión está la DB actual
alembic history --verbose
alembic current
```

En Docker, `alembic upgrade head` se ejecuta automáticamente antes de arrancar uvicorn (ver `Dockerfile`).

## Arrancar con Docker Compose (PostgreSQL real)

```bash
cp .env.example .env
docker compose up --build
```

## Tests

```bash
pytest -v

# con cobertura (lo que corre en CI, falla si baja del 90%)
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90
```

El badge de cobertura es la última cifra medida manualmente — si baja de forma notable al añadir código, actualízalo.

## Estructura

```
alembic/                # migraciones del esquema (versions/)
app/
├── main.py            # entrypoint, routers, exception handlers
├── core/               # config y seguridad (hash, JWT)
├── db/                 # base declarativa y sesión
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/routes/          # endpoints (auth, categories, expenses)
└── services/             # lógica de negocio separada de los routers
```

## Estado del proyecto / hitos

Lo ya scaffoldeado (fases 0-2 del roadmap):

- [x] Estructura del proyecto + Docker Compose + venv
- [x] Modelos `User`, `Category`, `Expense`
- [x] Registro y login con JWT
- [x] CRUD de `Categories` y `Expenses` protegido por auth
- [x] Tests de integración de auth y CRUD básico
- [x] CI (lint + test) en GitHub Actions
- [x] Manejo de errores consistente (`{"error": ...}`)
- [x] Migraciones con Alembic (esquema versionado, `create_all` eliminado de `main.py`)
- [x] Tests unitarios de la capa `services/` (con mocks, sin DB — `tests/unit/`)
- [x] Reporte de cobertura (`pytest-cov`, gate en CI al 90%, badge en README)
- [x] Rate limiting en `/auth/login` (5 intentos/min por IP, `slowapi`)
- [x] Logging estructurado (JSON por request: método, ruta, status, duración, IP)
- [x] CORS configurado (`CORS_ORIGINS` en `.env`, por defecto habilita `localhost:5173`/`3000` para el frontend)

Pendiente — requieren cuenta/credenciales externas propias, aplazados deliberadamente:
- [ ] Deploy a Railway/Fly.io/Render + endpoint `/health` monitorizado
- [ ] (Stretch) Endpoint que categorice un gasto automáticamente llamando a un LLM (necesita API key propia)

Cada uno de estos pendientes debería vivir como un issue individual en GitHub, con su propia rama y PR, para que el historial del repo muestre trabajo incremental.

## Bugs reales encontrados construyendo esto

1. **`ExpenseUpdate.date` solo aceptaba `null`** — `PATCH /expenses/{id}` rechazaba con 422 cualquier intento de cambiar la fecha de un gasto. Causa: para una asignación anotada dentro del cuerpo de una clase (`date: Optional[date] = None`), Python guarda el valor de la derecha (`None`) bajo el nombre `date` en el namespace de la clase *antes* de evaluar la anotación `Optional[date]` — así que cuando la anotación se evalúa, `date` ya no apunta al tipo `datetime.date` importado, apunta a `None`. `Optional[None]` colapsa a `NoneType`, y por eso el schema de OpenAPI generado mostraba `"date": {"type": "null"}` en vez de una unión real de fecha/null. Solo ocurre porque `ExpenseUpdate.date` tiene un valor por defecto (`= None`) — `ExpenseCreate.date` y `ExpenseRead.date`, campos obligatorios sin default, nunca lo sufrieron, y esa asimetría es lo que lo hizo fácil de pasar por alto. Detectado desde el cliente tipado del frontend (`openapi-typescript` generaba `date?: null`, que no compilaba contra una fecha real) — ningún test existente lo capturó, porque `update_expense` solo estaba testeado con mocks que construyen `ExpenseUpdate` directamente en Python, sin pasar por la capa HTTP+Pydantic donde vivía el bug real. Arreglado importando el tipo bajo alias (`from datetime import date as date_`) y añadiendo `tests/integration/test_expenses.py` con este caso como regresión explícita.
