Microservizio Auth — Database in Docker + Alembic (Guida completa)
Questa guida spiega come:

avviare PostgreSQL in Docker

collegare il microservizio FastAPI

creare lo schema con Alembic (migrazioni)

È pensata per essere riusabile in tutti i tuoi progetti.

0) Prerequisiti
Docker Desktop avviato (balena attiva).

Progetto Python con virtualenv (es.: authService4Ever/.venv).

Dipendenze installate: fastapi, uvicorn, sqlalchemy>=2, alembic, psycopg2-binary, pydantic-settings, python-dotenv, passlib[bcrypt], python-jose[cryptography]

```bash
# dentro la root del progetto
source .venv/bin/activate
python -m pip install -U pip
python -m pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary pydantic-settings python-dotenv passlib[bcrypt] python-jose[cryptography]

```

1) Avviare Postgres in Docker (Compose)
Crea docker-compose.yml alla root del progetto:
```yaml

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: auth
      POSTGRES_PASSWORD: authpass
    ports:
      - "5432:5432"         # se 5432 è occupata: "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

```


services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: auth
      POSTGRES_PASSWORD: authpass
    ports:
      - "5432:5432"         # se 5432 è occupata: "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

```bash
docker compose up -d db
docker compose ps
docker compose logs -f db
docker compose exec -it db psql -U auth -d auth_db -c "SELECT 1;"

```

Se usi porta diversa (es. 5433), ricordalo più avanti nelle URL.

2) Config applicazione (env + settings)
Crea .env in root (app gira fuori da Docker → host localhost):

```yaml
DB_URL=postgresql+psycopg2://auth:authpass@localhost:5432/auth_db
JWT_ALG=RS256
ACCESS_EXPIRES_MIN=15
REFRESH_EXPIRES_DAYS=7
PRIVATE_KEY_PATH=./private.pem
PUBLIC_KEY_PATH=./public.pem
CORS_ORIGINS=*


```
craazione config.py come adesso c'è 

3) Base SQLAlchemy, Engine, Session
3.1 app/db_base.py — solo Base
come adesso c'è

3.2 app/db.py — engine/session + get_db


4) Modelli (tabelle)
Nota: separare Base in db_base.py evita che Alembic debba importare config .env.

5) Alembic — setup e prima migrazione
```bash
alembic init migrations

```

Questo crea alembic.ini e la cartella migrations/.


5.2 alembic.ini (in root)


```yaml
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+psycopg2://auth:authpass@localhost:5432/auth_db

```

Se hai mappato 5433: usa localhost:5433.


5.3 migrations/env.py
Aggiungi gli import per far “vedere” i modelli e la Base:


5.4 Genera e applica
```bash
alembic revision --autogenerate -m "init users & refresh_tokens"
alembic upgrade head

```

Verifica nel DB (psql nel container):

```bash
docker compose exec -it db psql -U auth -d auth_db -c "\dt"
docker compose exec -it db psql -U auth -d auth_db -c "\d users"

```
Se vedi le tabelle → fatto ✅

6) Main app — test rapido
app/main.py (minimo, per health check + CORS):

```bash
uvicorn app.main:app --reload --port 8081
# http://localhost:8081/healthz -> {"status": "ok"}

```

7) Comandi utili (cheat sheet)
docker compose

```bash
docker compose up -d db
docker compose ps
docker compose logs -f db
docker compose exec -it db psql -U auth -d auth_db
docker compose down -v         # reset totale (cancella volume dati)

```

psql

```bash
\l           -- elenca database
\dt          -- elenca tabelle
\d users     -- descrive tabella users
SELECT * FROM users LIMIT 10;
\q           -- esci

```

alembic

```bash
alembic init migrations
alembic revision --autogenerate -m "msg"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history

```


8) Troubleshooting rapido
“Did not find any relations.” con \dt
Non hai ancora creato tabelle → fai migrazione Alembic (revision + upgrade).

No 'script_location' key found
alembic.ini mancante/nel posto sbagliato → metti alembic.ini in root con
script_location = migrations.

Migrazione vuota
In migrations/env.py manca from app import models o target_metadata = Base.metadata.

ModuleNotFoundError: app.config
Alembic importa i modelli passando da app.db che importa settings.
Soluzione: sposta Base in db_base.py e fai import di quella in models.py e in env.py.

Pydantic v2: BaseSettings moved
Usa pydantic-settings e from pydantic_settings import BaseSettings.

Connessione rifiutata
DB non pronto o porta sbagliata → docker compose ps, logs -f db, controlla porta (5432/5433).

9) Cosa fare dopo (per completare Auth)
security.py (hash/verify password con bcrypt)

tokens.py (JWT RS256: access+refresh, rotazione refresh)

schemas.py (Pydantic input/output)

routers/auth.py (/auth/register, /auth/login, /auth/me, /auth/refresh)

/.well-known/jwks.json (pubblica chiave pubblica per verificare access token)

Se vuoi, ti passo subito i file pronti per chiudere l’API Auth end‑to‑end.

Appendice — Struttura cartelle consigliata


```àrduino
authService4Ever/
  app/
    __init__.py
    main.py
    config.py
    db_base.py
    db.py
    models.py
    routers/
      __init__.py
      auth.py           # (step successivo)
    security.py         # (step successivo)
    tokens.py           # (step successivo)
    schemas.py          # (step successivo)
  migrations/
    env.py
    versions/
  alembic.ini
  docker-compose.yml
  .env
  requirements.txt
  private.pem
  public.pem

```
