# Expense API

API REST para gestión de gastos personales. Proyecto de portfolio con foco en **backend**: auth con JWT, CRUD, tests, Docker y CI/CD.

## Stack

- FastAPI + SQLAlchemy 2.0 + Alembic (pendiente de configurar, ver hitos)
- SQLite en local sin Docker (rápido para desarrollar) / PostgreSQL vía Docker Compose (real)
- JWT (OAuth2 password flow) para auth
- pytest + httpx para tests
- GitHub Actions para CI

## Arrancar en local (sin Docker, SQLite)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Docs interactivas en `http://localhost:8000/docs`.

## Arrancar con Docker Compose (PostgreSQL real)

```bash
cp .env.example .env
docker compose up --build
```

## Tests

```bash
pytest -v
```

## Estructura

```
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

Pendiente (para seguir practicando encima de esta base):

- [ ] Migraciones con Alembic (ahora mismo las tablas se crean con `create_all`, que sirve para desarrollo rápido pero no es lo que se usa en producción)
- [ ] Tests unitarios de la capa `services/` (con mocks, sin DB)
- [ ] Reporte de cobertura (`pytest-cov`) + badge en README
- [ ] Rate limiting en `/auth/login`
- [ ] Logging estructurado
- [ ] Deploy a Railway/Fly.io/Render + endpoint `/health` monitorizado
- [ ] (Stretch) Endpoint que categorice un gasto automáticamente llamando a un LLM

Cada uno de estos pendientes debería vivir como un issue individual en GitHub, con su propia rama y PR, para que el historial del repo muestre trabajo incremental.
