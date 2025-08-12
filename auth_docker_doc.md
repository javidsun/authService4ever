# Guida completa: Microservizio Auth + Docker (PostgreSQL) + Alembic

Questa documentazione raccoglie **tutto ciò che abbiamo fatto finora** e risponde alle domande pratiche su **Docker
“puro” vs Docker Compose**, oltre a spiegare **in dettaglio Alembic** (migrazioni). È pensata come base riutilizzabile
per tutti i progetti futuri che useranno questo microservizio di autenticazione.

---

## 0) Obiettivo del microservizio Auth

- Offrire **API di autenticazione** (register, login, refresh, me) riutilizzabili da più progetti.
- Usare **PostgreSQL** come database, eseguito **dentro Docker** (ambiente pulito e replicabile).
- Versionare lo schema DB con **Alembic** (migrazioni), in modo sicuro e tracciabile.

---

## 1) Stato attuale del progetto (recap)

- Cartella progetto (es. `authService4Ever`).
- Ambiente virtuale Python `.venv` collegato in PyCharm.
- `requirements.txt` installato (FastAPI, SQLAlchemy, Alembic, ecc.).
- Struttura di base con `app/main.py` (Hello `/healthz`).
- Chiavi JWT (`private.pem`, `public.pem`) e `.env` pronti.
- **Docker Desktop** installato e **Postgres** in container avviato via Compose.

---

## 2) Concetti Docker: “puro” vs Compose

### 2.1 Docker “puro”

- Usi **solo** `docker` per gestire **singoli container**: `docker run`, `docker logs`, `docker stop`, ecc.
- Configurazione (porte, env, volumi) scritta **ogni volta** a riga di comando.
- Esempio (Postgres con Docker “puro”):

    - ```bash
      docker run -d \
      --name my-postgres \
      -e POSTGRES_DB=auth_db \
      -e POSTGRES_USER=auth \
      -e POSTGRES_PASSWORD=authpass \
      -p 5432:5432 \
      -v pgdata:/var/lib/postgresql/data \
      postgres:16
    ```
```bash
    docker logs -f my-postgres
```

2.2 Docker Compose
Descrivi uno o più container (servizi) in un file YAML (docker-compose.yml).

Usi docker compose up/down/logs/ps/exec dalla cartella che contiene il file YAML.

Esempio docker-compose.yml (solo DB):
```json
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: auth
      POSTGRES_PASSWORD: authpass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:

```
commandi 
```bash
docker compose up -d db
docker compose logs -f db
docker compose exec -it db psql -U auth -d auth_db -c "SELECT 1;"
docker compose down -v  # reset totale (cancella anche i dati)

```
2.3 Differenza pratica: nome servizio vs nome container
Compose: ti riferisci al servizio (db) → docker compose logs -f db.

Docker “puro”: ti riferisci al container (authservice4ever-db-1) → docker logs -f authservice4ever-db-1.

3) Docker Desktop: cosa puoi controllare
Containers / Apps: avvia/ferma, log, shell dentro il container.

Images: immagini scaricate (es. postgres:16), gestione spazio, pull/update.

Volumes: dati persistenti (es. authservice4ever_pgdata).

Settings: CPU/RAM, proxy (se impostato può bloccare il pull delle immagini), rete.

4) Avvio del DB in Docker (riassunto operativo)
Crea/aggiorna docker-compose.yml nella root del progetto.

Avvia:
```bash
docker compose up -d db
docker compose ps
docker compose logs -f db

```
Testa con psql:
```bash
  docker compose exec -it db psql -U auth -d auth_db -c "SELECT 1;"
```
5) Vedere tabelle, colonne e dati

```bash
  docker compose exec -it db psql -U auth -d auth_db
\l            -- lista database
\dt           -- lista tabelle schema corrente
\d users      -- struttura tabella 'users'
SELECT * FROM users LIMIT 10;
\q            -- esci
```

Con client esterno (es. TablePlus/DBeaver):

```yaml
  Host: localhost
Port: 5432
Database: auth_db
User: auth
Password: authpass
```

6) Alembic: cos’è e perché lo usiamo
Scopo: tracciare versioni dello schema del database nel tempo.
Perché: evitare CREATE TABLE manuali e mantenere allineati i DB tra ambienti.
```bash
  alembic init migrations
```
alembic.ini
```bash
  sqlalchemy.url = postgresql+psycopg2://auth:authpass@localhost:5432/auth_db
```
migrations/env.py
```bash
  from app.db import Base
from app import models
target_metadata = Base.metadata

```
genera migrazione 
```bash
  alembic revision --autogenerate -m "init users & refresh_tokens"
```
applica
```bash
  alembic upgrade head
```

7) Prossimi passi
Creare tabelle users e refresh_tokens con SQLAlchemy.

Aggiungere logica security.py, tokens.py, schemas.py, routers/auth.py.

```mirmaid
flowchart TD
    A[Docker Desktop] --> B[Docker Compose]
    B --> C[Container Postgres]
    C --> D[(Volume pgdata)]
    C --> E[Porta 5432]
    E --> F[FastAPI Auth Service]
    F --> G[SQLAlchemy Models]
    G --> H[Alembic]
    H --> I[(Migrazioni DB)]
    I --> C
    F --> J[API REST: /register, /login, /refresh, /me]

```
Spiegazione del diagramma:

Docker Desktop → Interfaccia grafica per gestire i container.

Docker Compose → File docker-compose.yml che descrive i servizi (DB).

Container Postgres → Istanza isolata di PostgreSQL.

Volume pgdata → Salva i dati in modo persistente anche se il container viene ricreato.

Porta 5432 → Permette alla tua app di connettersi al DB.

FastAPI Auth Service → Microservizio Python per autenticazione.

SQLAlchemy Models → Definiscono tabelle e colonne del DB.

Alembic → Gestisce versionamento dello schema DB.

Migrazioni DB → Script generati da Alembic che modificano lo schema.

API REST → Endpoints per autenticazione.

ciclo di sviluppo end to end 
```mermaid
  flowchart LR
    subgraph Dev[Ambiente Dev]
      A[1. Scrivi/aggiorna Modelli SQLAlchemy<br/>app/models.py]
      B[2. Genera migrazione<br/>alembic revision --autogenerate]
      C[3. Verifica script migrazione<br/>migrations/versions/*.py]
      D[4. Applica migrazioni<br/>alembic upgrade head]
      E[5. Avvia API FastAPI<br/>uvicorn app.main:app --reload]
      F[6. Testa Endpoints Auth<br/>/register /login /refresh /me]
    end

    subgraph Docker[Docker Compose]
      G[(Postgres Container)]
      H[(Volume pgdata)]
    end

    A --> B --> C --> D --> E --> F
    D --> G
    G --> H
    E -->|DB_URL=postgresql://...@localhost:5432/auth_db| G

```

Lettura rapida:

aggiorni i modelli →

autogenerate la migrazione →

la controlli →

la applichi →

alzi l’API →

testi gli endpoint.
Il container Postgres (con volume) riceve gli aggiornamenti schema quando fai upgrade.


2) Sequenza “registro → login → /me → refresh”

```mermaid
  sequenceDiagram
    participant Client (RN App)
    participant AuthAPI (FastAPI)
    participant DB (Postgres)

    Client->>AuthAPI: POST /auth/register {email, password}
    AuthAPI->>DB: INSERT INTO users(...)
    DB-->>AuthAPI: OK (user id)
    AuthAPI-->>Client: 201 {id, email, is_email_verified}

    Client->>AuthAPI: POST /auth/login {email, password}
    AuthAPI->>DB: SELECT user by email
    DB-->>AuthAPI: user + password_hash
    AuthAPI->>AuthAPI: verify_pwd + issue JWT (access, refresh) + save refresh jti
    AuthAPI-->>Client: 200 {access_token, refresh_token}

    Client->>AuthAPI: GET /auth/me (Authorization: Bearer ACCESS)
    AuthAPI->>AuthAPI: verify access JWT (public key)
    AuthAPI->>DB: SELECT user by sub
    DB-->>AuthAPI: user
    AuthAPI-->>Client: 200 {id, email, is_email_verified}

    Client->>AuthAPI: POST /auth/refresh (Authorization: Bearer REFRESH)
    AuthAPI->>AuthAPI: verify refresh JWT + jti
    AuthAPI->>DB: mark old jti revoked + create new jti
    DB-->>AuthAPI: OK
    AuthAPI-->>Client: 200 {new access_token, new refresh_token}

```

Punti chiave da ricordare:

Password: mai salvate in chiaro, solo hash bcrypt.

JWT: access token breve; refresh rotato ad ogni uso (revoca jti precedente).

/me: si valida solo l’access token con la public key.

/refresh: si valida il refresh, si ruota e si rilascia una nuova coppia.

