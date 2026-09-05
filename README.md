# SIH26033 Backend

> Shared Authentication + RBAC + Farmer Profile/Verification + Admin Verification + Produce + Orders + Farmer Shipment View.

> - **Auth + RBAC (P1):** the one shared authentication system for the whole
>   platform — same users table, password hashing, JWT helpers, RBAC deps.
> - **Farmer Profile + Verification (P1):** farmer profile management and
>   document-based verification workflow.
> - **Admin Verification (P1):** admin review/approval/rejection of farmer
>   verification submissions.
> - **Farmer Produce (P1):** produce listing CRUD — the SINGLE SOURCE OF
>   TRUTH for produce data consumed by Marketplace, Consumer, etc.
> - **Orders (P1):** shared order system for CONSUMER/BULK_BUYER buyers and
>   FARMER sellers — single order API for all buyer roles.
> - **Farmer Shipment View (P1):** farmer-facing shipment status view linked
>   to confirmed orders.

> Future modules (Consumer, Marketplace, Finance, Logistics, Dispute) must
> **reuse** the auth foundation — never create separate auth systems.

Stack: **Python · FastAPI · PostgreSQL · SQLAlchemy 2 · Pydantic v2 · JWT (PyJWT) · bcrypt · pytest + httpx**

One FastAPI backend, one PostgreSQL database, one `users` table for all roles:

| Role | Used by |
|---|---|
| `FARMER` | P1 |
| `CONSUMER` | P2 |
| `BULK_BUYER` | P3 |
| `FINANCIER` | P4 |
| `LOGISTICS` | P5 |
| `ADMIN` | Admin |

---

## Project structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, startup table creation, routers
│   ├── core/
│   │   ├── config.py              # Env/.env config via pydantic-settings
│   │   ├── database.py            # Engine, SessionLocal, Base, get_db dependency
│   │   ├── enums.py               # Role + VerificationStatus + ProduceStatus + OrderStatus + ShipmentStatus enums
│   │   └── security.py            # hash_password / verify_password / JWT helpers
│   ├── models/
│   │   ├── user.py                # ONE users table for all roles
│   │   ├── farmer.py              # FarmerProfile + VerificationDocument tables
│   │   ├── produce.py             # Produce listing table
│   │   ├── order.py               # Order model (shared by Consumer, Bulk Buyer, etc.)
│   │   └── shipment.py            # Shipment model (farmer view, linked to orders)
│   ├── schemas/
│   │   ├── user.py                # Auth request/response schemas
│   │   ├── farmer.py              # Farmer profile + verification schemas
│   │   ├── admin.py               # Admin verification review schemas
│   │   ├── produce.py             # Produce listing schemas
│   │   ├── order.py               # Order request/response schemas
│   │   └── shipment.py            # Shipment response schemas
│   └── modules/
│       ├── auth/
│       │   ├── routes.py          # register / login / me + RBAC test endpoints
│       │   └── dependencies.py    # get_current_user, require_role (RBAC)
│       ├── farmer/
│       │   ├── routes.py          # farmer profile + verification routes
│       │   └── shipments_routes.py # farmer shipment view routes
│       ├── admin/
│       │   └── routes.py          # admin verification review routes
│       ├── produce/
│       │   └── routes.py          # produce listing CRUD routes
│       ├── orders/
│       │   └── routes.py          # shared order system routes
│       └── orders/
│           └── routes.py          # shared order system routes
├── tests/
│   ├── conftest.py                # Fixtures (disposable SQLite DB, client)
│   ├── test_auth.py               # The auth + RBAC test suite
│   ├── test_farmer.py             # Farmer profile + verification tests
│   ├── test_admin.py              # Admin verification tests
│   ├── test_produce.py            # Produce listing tests
│   ├── test_orders.py             # Orders tests
│   └── test_shipment.py           # Farmer shipment view tests
├── .env.example                   # Template for environment variables
├── pytest.ini
├── requirements.txt
└── README.md
```

## 1. Requirements

- **Python 3.11+** (developed against 3.13/3.14)
- **PostgreSQL 14+** (only needed for development/runtime — the test suite
  runs on a disposable SQLite database and works without PostgreSQL)

## 2. Create a virtual environment

From the `backend/` directory:

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (Git Bash / cmd):** `source .venv/Scripts/activate`
- **Linux / macOS:** `source .venv/bin/activate`

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE sih26033;"
# or
createdb sih26033
```

## 5. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env` and fill in real values. At minimum:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sih26033
JWT_SECRET_KEY=<generate one: python -c "import secrets; print(secrets.token_urlsafe(64))">
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`.env` is git-ignored — never commit it.

## 6. Start the backend

Tables are created automatically and safely on startup
(`Base.metadata.create_all` — it only creates what is missing, never drops or
resets data). Alembic migrations can replace this later without code changes.

```bash
uvicorn app.main:app --reload
```

## 7. Open Swagger

- **Swagger UI:** http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/

Swagger shows:

```
# Auth
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me                      (🔒 requires JWT)
GET    /api/auth/test-farmer             (🔒 DEV/TEST, FARMER only)
GET    /api/auth/test-admin              (🔒 DEV/TEST, ADMIN only)

# Farmer Profile (🔒 FARMER only)
POST   /api/farmer/profile              -> create profile
GET    /api/farmer/profile              -> view own profile
PUT    /api/farmer/profile              -> update own profile

# Farmer Verification (🔒 FARMER only)
POST   /api/verification/documents      -> submit a document
GET    /api/verification/status         -> view verification status

# Admin Verification (🔒 ADMIN only)
GET    /api/admin/verifications                 -> verification queue
GET    /api/admin/verifications/{user_id}       -> farmer details
POST   /api/admin/verifications/{user_id}/approve  -> approve
POST   /api/admin/verifications/{user_id}/reject   -> reject (remarks required)

# Produce (🔒 FARMER for create/update/delete, any JWT for read)
POST   /api/produce                          -> create listing (verified FARMER only)
GET    /api/produce                          -> list produce (with filters)
GET    /api/produce/{id}                     -> get single listing
PATCH  /api/produce/{id}                     -> update own listing
DELETE /api/produce/{id}                     -> delete own listing

# Orders (🔒 CONSUMER/BULK_BUYER create, various roles view/update)
POST   /api/orders                           -> create order (CONSUMER / BULK_BUYER)
GET    /api/orders                           -> list orders relevant to user
GET    /api/orders/{order_id}                -> get single order
PATCH  /api/orders/{order_id}/status         -> update order status

# Farmer Shipment View (🔒 FARMER only)
GET    /api/farmer/shipments                 -> list shipments for farmer
GET    /api/farmer/shipments/{shipment_id}   -> get one shipment
```

### Trying protected endpoints in Swagger

1. Click **Authorize** (top right).
2. Paste a token (get one via the example flow below or the "Try it out"
   button on `POST /api/auth/login`).
3. Call `GET /api/auth/me`, `/test-farmer`, `/test-admin` with the lock icons.

## 8. Run the tests

No PostgreSQL needed — tests use a disposable SQLite file:

```bash
pytest            # from the backend/ directory
```

To run against a real (dedicated test) PostgreSQL database instead:

```bash
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sih26033_test pytest
```

## 9. Example register / login / farmer flow

```bash
# Register a FARMER
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Farmer", "email": "farmer@example.com", "password": "password123", "role": "FARMER"}'

# Login -> returns {"access_token": "...", "user": {...}}
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "farmer@example.com", "password": "password123"}'

# Create farmer profile (replace <TOKEN>):
curl -X POST http://localhost:8000/api/farmer/profile \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"phone": "9876543210", "farm_name": "Green Acres", "farm_size_acres": 15.0}'

# Submit a verification document:
curl -X POST http://localhost:8000/api/verification/documents \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"document_type": "AADHAAR", "document_number": "1234-5678-9012"}'

# Check verification status:
curl http://localhost:8000/api/verification/status -H "Authorization: Bearer <TOKEN>"
```

## How authentication works

1. **Register** validates the input (name, email format, password length,
   valid `Role`), normalizes the email (`trim + lowercase`), checks for
   duplicates, bcrypt-hashes the password and stores the user. The
   `password_hash` column is excluded from every response schema, so it can
   never leak through the API.
2. **Login** looks up the user and runs `bcrypt.checkpw`. Wrong email and
   wrong password return the **same** `401 Incorrect email or password` so the
   endpoint can't be used to enumerate accounts.
3. On success a **JWT** is signed containing `sub` (user id) and `role`,
   expiring after `ACCESS_TOKEN_EXPIRE_MINUTES`.
4. Protected endpoints depend on `get_current_user`, which decodes/validates
   the `Authorization: Bearer <token>` header (signature, algorithm, expiry),
   loads the user from the DB and returns it. Missing/invalid/expired tokens
   → `401`.
5. The password hashing functions (`hash_password` / `verify_password`) and
   the JWT functions (`create_access_token` / `decode_access_token`) live in
   `app/core/security.py` — the single place every module uses.

## How RBAC works

`app/modules/auth/dependencies.py` provides a reusable dependency factory:

```python
from fastapi import Depends
from app.core.enums import Role
from app.modules.auth.dependencies import get_current_user, require_role

# Requires a valid JWT (any role):
def my_profile(user: User = Depends(get_current_user)): ...

# Only ADMIN:
def admin_panel(user: User = Depends(require_role(Role.ADMIN))): ...

# Any of several roles:
def buy(user: User = Depends(require_role(Role.CONSUMER, Role.BULK_BUYER))): ...
```

Behavior:

- No / invalid / expired JWT → **HTTP 401**
- Valid JWT but insufficient role → **HTTP 403**

The role is checked against the **database user**, not the token claim, so a
role change takes effect immediately even with an old token.

## Farmer Verification Workflow

1. Farmer registers via `POST /api/auth/register` with `role: FARMER`.
2. Farmer creates a profile via `POST /api/farmer/profile`.
3. Farmer submits verification documents via `POST /api/verification/documents`
   (AADHAAR, PAN, Land Record, etc.). Each submission creates a `PENDING` record.
4. Farmer checks overall status via `GET /api/verification/status`.
5. Admin reviews via `GET /api/admin/verifications` and `GET /api/admin/verifications/{user_id}`.
6. Admin approves (`POST /api/admin/verifications/{user_id}/approve`) or
   rejects with remarks (`POST /api/admin/verifications/{user_id}/reject`).
7. Farmer sees updated status via `GET /api/verification/status`.

**Overall status logic:**
- `PENDING` — at least one document is `PENDING`
- `APPROVED` — ALL documents are `APPROVED`
- `REJECTED` — at least one document is `REJECTED` (and none `PENDING`)

## Produce Listing Workflow

1. Farmer must be APPROVED before creating produce.
2. Farmer creates a listing via `POST /api/produce`.
3. Listing defaults to `ACTIVE` status.
4. Farmer can update (`PATCH`) or delete (`DELETE`) their own listings.
5. Any authenticated user can read (`GET`) listings — this is the SINGLE
   SOURCE OF TRUTH for Marketplace and Consumer modules.

**Produce statuses:** `ACTIVE` · `INACTIVE` · `SOLD_OUT`

**Ownership rules:**
- Only the owning farmer can update or delete their produce.
- Other farmers get `404` (not `403`) to avoid leaking resource existence.

**Verification requirement:**
- `PENDING` / `REJECTED` / unverified farmers → `403` with clear error.
- Only `APPROVED` farmers can create produce.

## Orders Workflow

1. Buyer (CONSUMER or BULK_BUYER) creates an order via `POST /api/orders`:
   - Provide `produce_id` and `quantity`.
   - Backend calculates `total_amount = quantity × unit_price`.
   - Backend gets `farmer_id` from the Produce listing owner.
   - Produce stock decreases after successful order.
2. Farmer views orders for their produce via `GET /api/orders`.
3. Buyer views their own orders via `GET /api/orders`.
4. Status transitions:
   - Buyer: `PENDING` → `CANCELLED` (restores stock)
   - Farmer: `PENDING` → `CONFIRMED`
   - Farmer: `CONFIRMED` → `COMPLETED`
   - Admin: any valid transition

**Order statuses:** `PENDING` · `CONFIRMED` · `CANCELLED` · `COMPLETED`

**Stock rules:**
- Stock decreases on order creation.
- Stock restores on cancellation.
- Stock cannot go negative.
- Farmer cannot order their own produce.

## Farmer Shipment View Workflow

1. Farmer has an order that is `CONFIRMED` (or later).
2. Farmer can view shipment status via:
   - `GET /api/farmer/shipments` — list all shipments for their orders
   - `GET /api/farmer/shipments/{shipment_id}` — get one shipment
3. A shipment is linked to an order, so the farmer sees only shipments for
   orders containing their own produce.
4. Shipment status: `PENDING` · `ASSIGNED` · `PICKED_UP` · `IN_TRANSIT` ·
   `DELIVERED` · `CANCELLED`

**Ownership rules:**
- Only the owning farmer can see their shipments.
- Other farmers get `404` (not `403`) to avoid leaking resource existence.
- Non-FARMER roles get `403`.

**P5 integration:** P5 (Logistics) will integrate with this model later for
route optimization and actual shipment processing. For now, the model provides
the farmer-facing view of shipment status.

## Notes for the team

- One users table, one hashing system, one JWT system, one RBAC system, one
  auth API. Future modules import `get_current_user` / `require_role` from
  `app.modules.auth.dependencies` — never copy auth logic.
- Admin verification endpoints (`/api/admin/verifications/...`) are
  ADMIN-only. They record `reviewed_by` (admin user id) and `reviewed_at`
  on each document they act on.
- **Produce is the SINGLE SOURCE OF TRUTH.** Marketplace, Consumer, and
  other modules must read from `GET /api/produce` — do NOT create duplicate
  product tables.
- **Orders is the SHARED order system.** Consumer, Bulk Buyer, and future
  modules reuse the same `/api/orders/*` endpoints — no separate order APIs.
- **Farmer Shipment View is the FARMER-FACING VIEW only.** P5 owns the
  logistics engine; this module does not implement route optimization or GPS
  tracking.
- **bcrypt vs passlib:** passlib is unmaintained and incompatible with
  current bcrypt (≥ 4.1). We use the maintained `bcrypt` package directly.
- bcrypt hashes at most 72 bytes of a password — enforced in the schemas.
- The `/api/auth/test-farmer` and `/api/auth/test-admin` endpoints are
  temporary RBAC demonstrations. Remove them once real modules exist.
- Database initialization is `create_all` at startup (safe, idempotent).
  Introduce Alembic migrations before the schema evolves past the prototype.
- Farmer module tables (`farmer_profiles`, `verification_documents`) are
  created automatically at startup via `create_all`.
