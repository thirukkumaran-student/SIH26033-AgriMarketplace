# SIH26033 AgriMarketplace — Integrated Backend (P1 + P2 + P3 + P4)

This README is the setup and integration handout for the **integrated backend** containing:

- **P1** — Farmer + Admin Verification
- **P2** — Consumer + Admin Disputes/Monitoring
- **P3** — Bulk Buyer + Shared Marketplace
- **P4** — Financier + Finance Integration

**P5 is not implemented in this backend.** This README therefore documents the exact contracts, existing shipment placeholders, shared database, authentication system, and integration points that a P5 developer must use when adding Logistics + AI + Route Optimization.

The backend is a **modular monolith**:

```text
One FastAPI application
        +
One PostgreSQL database
        +
One shared User/Auth/JWT/RBAC system
        +
Shared Produce + Order + Shipment entities
        +
Role-specific feature modules
```

Do not create a second backend, authentication system, marketplace, Produce table, Order table, or database.

---

# 1. Current Integrated Scope

| Module | Owner | Current status |
|---|---|---|
| P1 | Farmer + Admin Verification | Implemented |
| P2 | Consumer + Admin Disputes/Monitoring | Implemented |
| P3 | Bulk Buyer + Shared Marketplace | Implemented |
| P4 | Financier + Finance | Implemented |
| P5 | Logistics + AI + Route Optimization | **Integration target — not yet implemented** |

The current codebase contains P1–P4 modules plus the shared `Shipment` model and read-only shipment views intended to be consumed by P5.

---

# 2. Technology Stack

- Python 3.11+
- FastAPI
- Uvicorn
- PostgreSQL 14+
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- pydantic-settings
- psycopg 3
- bcrypt
- PyJWT
- pytest
- httpx

The installed dependencies are defined in `requirements.txt`.

---

# 3. Repository Structure

The current backend is at the repository root:

```text
SIH26033-AgriMarketplace/
│
├── alembic/
│   ├── versions/
│   │   ├── 70d7a0f1364c_initial_schema.py
│   │   └── f22e87c8b2a0_migrate_marketplace_money_fields_to_.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── enums.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── farmer.py
│   │   ├── consumer.py
│   │   ├── buyer.py
│   │   ├── financier.py
│   │   ├── produce.py
│   │   ├── order.py
│   │   ├── shipment.py
│   │   └── dispute.py
│   │
│   ├── schemas/
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── farmer/
│   │   ├── admin/
│   │   ├── produce/
│   │   ├── orders/
│   │   ├── consumer/
│   │   ├── buyer/
│   │   ├── financier/
│   │   └── finance/
│   │
│   └── main.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# 4. Clone the Repository

Use the integrated repository:

```bash
git clone https://github.com/thirukkumaran-student/SIH26033-AgriMarketplace.git
cd SIH26033-AgriMarketplace
```

For the current integrated development branch:

```bash
git checkout Integration
git pull origin Integration
```

If the branch is already checked out locally:

```bash
git pull
```

---

# 5. Python Environment Setup

Create a virtual environment from the repository root:

```bash
python -m venv .venv
```

## Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## Windows CMD

```cmd
.venv\Scripts\activate
```

## Linux/macOS

```bash
source .venv/bin/activate
```

Verify:

```bash
python --version
```

Python 3.11 or newer is recommended.

---

# 6. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 7. PostgreSQL Setup

## 7.1 Required database

The current integrated development database is:

```text
agri_marketplace
```

Use PostgreSQL on the default port:

```text
localhost:5432
```

Typical local configuration:

```text
Host:     localhost
Port:     5432
Database: agri_marketplace
User:     postgres
Password: <your PostgreSQL password>
```

Create the database once.

Using `psql`:

```bash
psql -U postgres -c "CREATE DATABASE agri_marketplace;"
```

If it already exists, do not create it again.

---

# 8. Environment Configuration

Copy the example environment file:

## PowerShell

```powershell
Copy-Item .env.example .env
```

## CMD

```cmd
copy .env.example .env
```

## Linux/macOS/Git Bash

```bash
cp .env.example .env
```

Edit `.env`.

Use:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/agri_marketplace

JWT_SECRET_KEY=YOUR_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Put the generated value into:

```text
JWT_SECRET_KEY
```

## Important

`.env` is ignored by Git.

Never commit:

- PostgreSQL passwords
- JWT secrets
- API keys
- private credentials

---

# 9. Database Configuration Notes

The application reads configuration through:

```text
app/core/config.py
```

The settings are:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL/SQLite connection string |
| `JWT_SECRET_KEY` | JWT signing secret |
| `JWT_ALGORITHM` | JWT algorithm; default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime |

The database engine/session are centralized in:

```text
app/core/database.py
```

Do not create another SQLAlchemy engine/session for P5.

P5 must use:

```python
from app.core.database import get_db
```

---

# 10. Initialize the Database with Alembic

The integrated backend has Alembic migrations.

Run:

```bash
alembic upgrade head
```

Verify:

```bash
alembic current
```

The database should be at the latest migration revision.

To inspect available revisions:

```bash
alembic history
```

## When P5 adds database tables

P5 must create a migration.

Example:

```bash
alembic revision --autogenerate -m "add p5 logistics tables"
```

Then inspect the generated migration before applying it:

```bash
alembic upgrade head
```

Do not manually create P5 tables in PostgreSQL and do not depend on `Base.metadata.create_all()` as the production schema-management mechanism.

---

# 11. Start the Backend

From the repository root:

```bash
uvicorn app.main:app --reload
```

Default server:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Root health check:

```text
http://localhost:8000/
```

Expected root response:

```json
{
  "message": "SIH26033 backend is running",
  "docs": "/docs"
}
```

---

# 12. Authentication and Authorization

Authentication is implemented once for the whole application.

Relevant files:

```text
app/core/security.py
app/modules/auth/routes.py
app/modules/auth/dependencies.py
app/models/user.py
app/core/enums.py
```

## Authentication flow

```text
POST /api/auth/register
        ↓
User created
        ↓
POST /api/auth/login
        ↓
JWT access token
        ↓
Authorization: Bearer <token>
        ↓
get_current_user()
        ↓
require_role(...)
        ↓
Protected endpoint
```

## JWT contents

The access token contains:

```text
sub  = user ID
role = user role
iat  = issued-at time
exp  = expiry time
```

The backend resolves the JWT user against the shared `users` table.

---

# 13. Roles

The shared role enum contains:

```text
FARMER
CONSUMER
BULK_BUYER
FINANCIER
LOGISTICS
ADMIN
```

`LOGISTICS` already exists specifically for P5.

P5 must use:

```python
from app.core.enums import Role
from app.modules.auth.dependencies import require_role
```

Example:

```python
current_user: User = Depends(
    require_role(Role.LOGISTICS)
)
```

Do not create:

```text
P5User
LogisticsUser
LogisticsRole
```

---

# 14. Swagger Authentication

To test protected APIs:

1. Register a user.
2. Login.
3. Copy `access_token`.
4. Open `/docs`.
5. Click **Authorize**.
6. Enter:

```text
Bearer YOUR_ACCESS_TOKEN
```

7. Authorize.
8. Call endpoints allowed for that role.

Expected authorization behavior:

| Condition | Result |
|---|---:|
| Missing token | `401` |
| Invalid/expired token | `401` |
| Valid token, wrong role | `403` |
| Valid token, correct role | Allowed |

---

# 15. Authentication Endpoints

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

Registration uses the shared `users` table.

There is no separate authentication database for P1, P2, P3, P4, or P5.

---

# 16. P1 Endpoints — Farmer + Verification

## Farmer profile

```http
POST /api/farmer/profile
GET  /api/farmer/profile
PUT  /api/farmer/profile
```

## Verification

```http
POST /api/verification/documents
GET  /api/verification/status
```

## Admin verification

```http
GET  /api/admin/verifications
GET  /api/admin/verifications/{user_id}
POST /api/admin/verifications/{user_id}/approve
POST /api/admin/verifications/{user_id}/reject
```

Farmer produce creation is gated by farmer verification.

---

# 17. P1 Produce Endpoints

```http
POST   /api/produce
GET    /api/produce
GET    /api/produce/{produce_id}
PATCH  /api/produce/{produce_id}
DELETE /api/produce/{produce_id}
```

Produce is the **single source of truth** for marketplace inventory.

Important fields include:

```text
id
farmer_id
crop
category
quantity
unit
price_per_unit
location
harvest_date
quality_grade
image
status
created_at
updated_at
```

Money uses `Decimal`/`Numeric(12,2)`.

The backend is authoritative for price at order time.

---

# 18. P2 Consumer + Marketplace Endpoints

## Consumer profile

```http
POST /api/consumer/profile
GET  /api/consumer/profile
PUT  /api/consumer/profile
```

## Marketplace

```http
GET /api/marketplace/produce
GET /api/marketplace/produce/{produce_id}
```

The marketplace reads the existing `Produce` table.

It does not create another catalog/product table.

Eligible marketplace produce is based on the existing farmer verification, produce status, and stock rules.

---

# 19. Shared Order System

The shared Order API is:

```http
POST  /api/orders
POST  /api/orders/review
GET   /api/orders
GET   /api/orders/{order_id}
PATCH /api/orders/{order_id}/status
```

The same `Order` model is used by:

```text
CONSUMER
BULK_BUYER
```

There is no:

```text
ConsumerOrder
BulkBuyerOrder
```

---

# 20. Order Lifecycle

Current allowed transitions:

```text
PENDING
   │
   ├──→ CONFIRMED
   │
   └──→ CANCELLED

CONFIRMED
   │
   └──→ COMPLETED
```

The existing order module owns these order-state rules.

P5 must not introduce a parallel order state machine.

---

# 21. P3 Bulk Buyer

## Buyer profile

```http
POST /api/buyer/profile
GET  /api/buyer/profile
PUT  /api/buyer/profile
```

The buyer profile contains:

```text
financing_preference
```

with:

```text
NONE
PLATFORM
```

A buyer selecting `NONE` can procure without platform financing.

A buyer selecting `PLATFORM` must establish an applicable active financing relationship before a financed order.

---

# 22. P4 Financier Endpoints

## Financier profile

```http
POST /api/financier/profile
GET  /api/financier/profile
PUT  /api/financier/profile
GET  /api/financier/
```

The discovery endpoint is used by a bulk buyer to find eligible approved financiers.

---

# 23. P4 Finance Endpoints

```http
GET  /api/finance/relationships/me

POST /api/finance/requests
GET  /api/finance/requests

POST /api/finance/requests/{request_id}/approve
POST /api/finance/requests/{request_id}/reject
POST /api/finance/requests/{request_id}/select

POST /api/finance/transactions
GET  /api/finance/transactions
GET  /api/finance/transactions/{transaction_id}

POST /api/finance/transactions/{transaction_id}/repayment
```

---

# 24. Financing Architecture

Financing is **relationship-first**.

```text
Bulk Buyer
    ↓
Discover approved financier
    ↓
Financing Request
    ↓
Financier approves/rejects
    ↓
Buyer selects approved offer
    ↓
ACTIVE FinancingRelationship
    ↓
Multiple orders can use the same relationship
    ↓
Each financed order gets its own FinancingTransaction
```

A financing relationship represents the standing credit arrangement.

A financing transaction represents financing for one specific order.

---

# 25. P3 ↔ P4 Order/Finance Contract

For a financed order:

```text
POST /api/orders
```

can use an applicable:

```text
relationship_id
```

The order workflow:

```text
Produce
   ↓
calculate authoritative unit price
   ↓
quantity × unit price
   ↓
Order created
   ↓
FinancingTransaction created
```

P3 does not calculate:

- interest
- financing capacity
- repayment

Those are P4 responsibilities.

---

# 26. Financing Transaction Contract

The direct finance transaction endpoint accepts:

```json
{
  "relationship_id": 1,
  "order_id": 123,
  "principal": 250.00
}
```

The backend validates:

- financing relationship exists
- relationship belongs to the buyer
- relationship is active
- order exists
- order belongs to the buyer
- order does not already have a financing transaction
- sufficient financing capacity exists

The transaction is linked to the existing order.

---

# 27. Finance Money Rules

Financial amounts use precise decimal arithmetic.

Relevant fields use:

```text
Numeric(12,2)
```

Examples:

```text
credit_limit
interest
principal
total_repayment
```

Interest calculation:

```text
interest = principal × annual_rate × days / 365
```

Total repayment:

```text
total_repayment = principal + interest
```

No real bank/NBFC transaction occurs.

The platform does not become the lender.

---

# 28. Cancellation + Finance

If a financed order is cancelled while the financing transaction is active:

```text
Order
  ↓
CANCELLED

FinancingTransaction
  ↓
VOIDED

Produce.quantity
  ↓
restored

Outstanding financing
  ↓
released
```

`VOIDED` means the financed order was cancelled before repayment.

P5 must not alter this financing behavior.

---

# 29. Current Shipment Placeholder

P5 integration starts from an existing `Shipment` model.

Current entity:

```text
Shipment
├── id
├── order_id
├── status
├── pickup_location
├── destination
├── estimated_delivery
├── logistics_cost
├── created_at
└── updated_at
```

`Shipment.order_id` references the shared `orders` table.

The current shipment status vocabulary is:

```text
PENDING
ASSIGNED
PICKED_UP
IN_TRANSIT
DELIVERED
CANCELLED
```

**Do not create another shipment table.**

---

# 30. Existing Shipment Read APIs

These APIs already exist and are intended to consume P5-managed shipment state.

## Farmer

```http
GET /api/farmer/shipments
GET /api/farmer/shipments/{shipment_id}
```

The farmer can only see shipments connected to orders for their own produce.

## Consumer

```http
GET /api/consumer/shipments
GET /api/consumer/shipments/{shipment_id}
```

The consumer can only see shipments connected to their own orders.

These APIs are read views.

P5 should update the shared `Shipment` entity rather than replacing these views.

---

# 31. What Is NOT Currently Implemented

The following are intentionally open for P5:

```text
POST /api/logistics/shipments
GET  /api/logistics/shipments
GET  /api/logistics/shipments/{id}

shipment assignment
pickup transition
transit transition
delivery transition
logistics cancellation

route optimization
handoff tracking
demand forecasting
farmer forecast/advisory
bulk buyer shipment tracking
```

There is currently no separate P5 logistics engine in the integrated backend.

---

# 32. P5 Integration Boundary

The intended ownership is:

```text
P1
 └── Farmer / Produce / verification

P2
 └── Consumer / Marketplace / disputes / monitoring

P3
 └── Bulk Buyer / shared order behavior

P4
 └── Financing relationships / transactions / repayment

P5
 └── Shipment lifecycle / logistics / route optimization / AI
```

The central integration point is:

```text
                 Produce
                    │
                    ▼
                 Order
                    │
                    ▼
              ┌───────────┐
              │    P5     │
              │ Logistics │
              └─────┬─────┘
                    │
                    ▼
                 Shipment
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Farmer             Consumer
       tracking           tracking
```

P5 operates on the existing Order/Shipment relationship.

---

# 33. Recommended P5 Module Structure

Create:

```text
app/modules/logistics/
├── __init__.py
├── routes.py
├── schemas.py
├── service.py
├── routing.py
└── forecasting.py
```

Purpose:

| File | Responsibility |
|---|---|
| `routes.py` | P5 HTTP endpoints |
| `schemas.py` | P5 request/response schemas |
| `service.py` | Shipment lifecycle/business rules |
| `routing.py` | OR-Tools route optimization |
| `forecasting.py` | Demand forecasting |
| `__init__.py` | Module package |

Keep this lightweight. Do not add unnecessary repository/factory/service layers.

---

# 34. Recommended P5 Logistics APIs

## Shipment creation

```http
POST /api/logistics/shipments
```

Suggested request:

```json
{
  "order_id": 123,
  "pickup_location": "Farmer Farm, Coimbatore",
  "destination": "Buyer Warehouse, Chennai"
}
```

Initial state:

```text
PENDING
```

The endpoint must verify that the referenced order exists.

---

## Shipment listing

```http
GET /api/logistics/shipments
```

Role:

```text
LOGISTICS
```

Purpose:

Return shipments requiring logistics operations.

---

## Shipment detail

```http
GET /api/logistics/shipments/{shipment_id}
```

Role:

```text
LOGISTICS
```

---

## Assignment

```http
PATCH /api/logistics/shipments/{shipment_id}/assign
```

Expected transition:

```text
PENDING → ASSIGNED
```

---

## Pickup

```http
PATCH /api/logistics/shipments/{shipment_id}/pickup
```

Expected transition:

```text
ASSIGNED → PICKED_UP
```

---

## Transit

```http
PATCH /api/logistics/shipments/{shipment_id}/transit
```

Expected transition:

```text
PICKED_UP → IN_TRANSIT
```

---

## Delivery

```http
PATCH /api/logistics/shipments/{shipment_id}/deliver
```

Expected transition:

```text
IN_TRANSIT → DELIVERED
```

---

## Cancellation

```http
PATCH /api/logistics/shipments/{shipment_id}/cancel
```

Only allow cancellation states agreed by the team.

Do not automatically cancel the Order unless the shared order contract is deliberately changed.

---

# 35. Shipment State Machine

P5 should enforce:

```text
             ┌─────────────┐
             │   PENDING   │
             └──────┬──────┘
                    │ assign
                    ▼
             ┌─────────────┐
             │  ASSIGNED   │
             └──────┬──────┘
                    │ pickup
                    ▼
             ┌─────────────┐
             │ PICKED_UP   │
             └──────┬──────┘
                    │ transit
                    ▼
             ┌─────────────┐
             │ IN_TRANSIT  │
             └──────┬──────┘
                    │ deliver
                    ▼
             ┌─────────────┐
             │  DELIVERED  │
             └─────────────┘

PENDING / ASSIGNED / IN_TRANSIT
             │
             ▼
         CANCELLED
```

Do not permit arbitrary status jumps.

---

# 36. Route Optimization

Recommended endpoint:

```http
POST /api/logistics/routes/optimize
```

Suggested request:

```json
{
  "shipment_ids": [10, 11, 12]
}
```

The route optimizer should:

```text
Shipment IDs
     ↓
Load Shipment records
     ↓
Read pickup/destination
     ↓
Convert locations to coordinates
     ↓
OR-Tools
     ↓
Optimized route
```

The prototype does not require live GPS tracking.

Use fixed/sample coordinates if necessary.

Do not introduce a live maps/GPS dependency unless the team explicitly decides to do so.

---

# 37. Handoff Tracking

If P5 implements handoffs, create a separate entity rather than overloading `Shipment`.

Recommended:

```text
app/models/handoff.py
```

Possible fields:

```text
id
shipment_id
from_party
to_party
timestamp
remarks
```

Recommended endpoint:

```http
POST /api/logistics/shipments/{shipment_id}/handoffs
```

If a new table is introduced:

1. Add the model.
2. Register it with the application's model metadata.
3. Create an Alembic migration.
4. Add tests.
5. Run the full suite.

---

# 38. Bulk Buyer Shipment Tracking

P3 owns the bulk buyer workflow, but the current backend does not have a bulk-buyer shipment tracking API.

A useful P5/P3 integration is:

```http
GET /api/buyer/shipments
GET /api/buyer/shipments/{shipment_id}
```

Authorization:

```text
BULK_BUYER
```

Ownership:

```text
Shipment
   ↓
Order
   ↓
Order.buyer_id == current_user.id
```

Do not expose shipments belonging to another buyer.

---

# 39. AI Demand Forecasting

P5's forecasting pipeline is:

```text
Existing platform data
        ↓
Pandas
        ↓
Feature preparation
        ↓
GradientBoostingRegressor
        ↓
Demand prediction
        ↓
Farmer advisory
```

Prototype data shape:

```text
date
crop
region
quantity
```

Prefer deriving historical information from the existing platform rather than creating a duplicate order dataset.

Useful existing data includes:

```text
Order.created_at
Order.quantity
Produce.crop
Produce.location
```

---

# 40. Recommended Forecast Endpoint

```http
POST /api/forecast/demand
```

Suggested request:

```json
{
  "crop": "Wheat",
  "region": "Tamil Nadu",
  "forecast_days": 30
}
```

Suggested response:

```json
{
  "crop": "Wheat",
  "region": "Tamil Nadu",
  "forecast_days": 30,
  "predicted_quantity": 1250
}
```

A farmer advisory endpoint can also be added:

```http
GET /api/farmer/forecast
```

The AI should provide recommendations.

It should not silently modify:

- produce price
- inventory
- orders
- financing
- shipment state

---

# 41. P5 Files Allowed to Be Added

Preferred:

```text
app/modules/logistics/
```

and, if required:

```text
app/models/handoff.py
app/schemas/handoff.py
```

P5 tests:

```text
tests/test_logistics.py
tests/test_routing.py
tests/test_forecasting.py
tests/test_p5_integration.py
```

If P5 needs a new shared entity, coordinate before changing shared models.

---

# 42. Shared Files Requiring Coordination

These files affect multiple modules:

```text
app/main.py
app/core/enums.py
app/core/database.py
app/models/__init__.py
app/models/order.py
app/models/shipment.py
app/schemas/order.py
app/schemas/shipment.py
requirements.txt
alembic/versions/*
```

Do not independently rewrite them.

Small integration edits are fine after agreement.

The repository's development rule is:

> Do not silently change shared API fields, database fields, enums, or status names.

---

# 43. P5 Must NOT Duplicate

Do not create:

```text
LogisticsUser
P5User
LogisticsOrder
BulkBuyerOrder
P5Produce
LogisticsProduce
P5Shipment
P5Auth
P5JWT
P5Database
```

Use the existing entities:

```text
User
Produce
Order
Shipment
```

and the existing infrastructure:

```text
get_db
get_current_user
require_role
```

---

# 44. Database Schema

The current integrated database is:

```text
agri_marketplace
```

Core relationship graph:

```text
users
  │
  ├──────── farmer_profiles
  │
  ├──────── consumer_profiles
  │
  ├──────── buyer_profiles
  │
  ├──────── financier_profiles
  │
  ├──────── verification_documents
  │
  ├──────── produce
  │             │
  │             ▼
  │           orders
  │          /  |  \
  │         /   |   \
  │        ▼    ▼    ▼
  │    disputes shipments
  │
  └──────── financing_relationships
                    │
                    ▼
          financing_transactions
                    │
                    └── order_id → orders
```

---

# 45. Database Tables

## `users`

```text
id                  PK
name
email               UNIQUE
password_hash
role
created_at
```

Role constraint:

```text
FARMER
CONSUMER
BULK_BUYER
FINANCIER
LOGISTICS
ADMIN
```

---

## `farmer_profiles`

```text
id                  PK
user_id             FK → users.id
phone
farm_name
farm_size_acres
farm_location
soil_type
irrigation_type
bank_account_number
ifsc_code
created_at
updated_at
```

---

## `verification_documents`

```text
id                  PK
user_id             FK → users.id
document_type
document_number
file_url
status
remarks
submitted_at
reviewed_by         FK → users.id
reviewed_at
```

Used by farmer/financier verification and admin review.

---

## `consumer_profiles`

```text
id                  PK
user_id             FK → users.id
phone
address
city
state
pincode
created_at
updated_at
```

---

## `buyer_profiles`

```text
id                  PK
user_id             FK → users.id
phone
address
city
state
pincode
financing_preference
created_at
updated_at
```

`financing_preference`:

```text
NONE
PLATFORM
```

---

## `financier_profiles`

```text
id                  PK
user_id             FK → users.id
institution_name
institution_type
phone
address
city
state
pincode
created_at
updated_at
```

---

## `produce`

```text
id                  PK
farmer_id           FK → users.id
crop
category
quantity
unit
price_per_unit      NUMERIC(12,2)
location
harvest_date
quality_grade
image
status
created_at
updated_at
```

This is the single source of truth for produce.

---

## `orders`

```text
id                  PK
produce_id          FK → produce.id
buyer_id            FK → users.id
farmer_id           FK → users.id
quantity
unit_price          NUMERIC(12,2)
total_amount        NUMERIC(12,2)
status
created_at
updated_at
```

`buyer_id` may refer to:

```text
CONSUMER
BULK_BUYER
```

---

## `shipments`

```text
id                  PK
order_id            FK → orders.id
status
pickup_location
destination
estimated_delivery
logistics_cost      NUMERIC(12,2)
created_at
updated_at
```

This is the principal P5 integration table.

---

## `disputes`

```text
id                  PK
order_id            FK → orders.id
raised_by           FK → users.id
reason
description
status
resolution
admin_remarks
resolved_by         FK → users.id
created_at
updated_at
resolved_at
```

---

## `financing_relationships`

```text
id                  PK
buyer_id            FK → users.id
financier_id        FK → users.id
credit_limit        NUMERIC(12,2)
interest_rate       NUMERIC(5,2)
tenure_days
status
```

---

## `financing_requests`

```text
id                  PK
buyer_id            FK → users.id
financier_id        FK → users.id
status
credit_limit        NUMERIC(12,2)
interest_rate       NUMERIC(5,2)
tenure_days
```

---

## `financing_transactions`

```text
id                  PK
relationship_id     FK → financing_relationships.id
order_id            FK → orders.id UNIQUE
principal           NUMERIC(12,2)
interest            NUMERIC(12,2)
total_repayment     NUMERIC(12,2)
status
```

Transaction statuses:

```text
ACTIVE
COMPLETED
VOIDED
```

---

# 46. Important Database Relationships for P5

The most important P5 query path is:

```text
Shipment
   │
   └── order_id
          │
          ▼
        Order
       /     \
      /       \
farmer_id   buyer_id
    │           │
    ▼           ▼
 Farmer      Buyer
```

P5 should use this relationship for authorization and tracking.

For example, to ensure a farmer owns a shipment:

```text
shipment.order_id
        ↓
order.farmer_id
        ↓
current_user.id
```

For a bulk buyer:

```text
shipment.order_id
        ↓
order.buyer_id
        ↓
current_user.id
```

---

# 47. Alembic Rules for P5

If P5 adds a table:

```bash
alembic revision --autogenerate -m "add p5 handoffs"
```

Inspect the generated migration.

Then:

```bash
alembic upgrade head
```

Check:

```bash
alembic current
```

Do not commit a migration that contains unrelated table creation/deletion.

The migration should contain only the intended P5 schema changes.

---

# 48. Testing

The test suite uses a disposable SQLite database by default.

Run:

```bash
pytest -q
```

The current integrated backend baseline is:

```text
325 passed
11 warnings
```

The warnings are non-failing dependency/deprecation warnings.

P5 must preserve the existing suite.

---

# 49. Test Database Configuration

The test fixture is:

```text
tests/conftest.py
```

By default:

```text
sqlite:///./test_auth.db
```

Tests use:

```text
Base.metadata.drop_all()
Base.metadata.create_all()
```

against the disposable test database.

This is intentionally different from production schema management.

To test against a dedicated PostgreSQL database:

```bash
TEST_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/agri_marketplace_test pytest
```

Do not point destructive test fixtures at the production/development database.

---

# 50. Recommended P5 Test Cases

At minimum:

## Shipment

```text
POST shipment for valid order
reject non-existent order
reject duplicate shipment if one-per-order is enforced
GET logistics shipments
GET logistics shipment detail
```

## Authorization

```text
non-LOGISTICS cannot perform logistics operations
farmer cannot view another farmer's shipment
buyer cannot view another buyer's shipment
consumer cannot view another consumer's shipment
```

## State transitions

```text
PENDING → ASSIGNED
ASSIGNED → PICKED_UP
PICKED_UP → IN_TRANSIT
IN_TRANSIT → DELIVERED
invalid transitions rejected
```

## Existing integration

```text
P5 shipment update appears in farmer tracking
P5 shipment update appears in consumer tracking
P5 shipment belongs to correct Order
```

## Routing

```text
valid shipment set produces route
empty/invalid shipment input is rejected
```

## Forecasting

```text
historical data loads
features are generated
model produces prediction
forecast endpoint returns expected response shape
```

---

# 51. Complete Integration Test Flow

The final P1–P5 demonstration should be:

```text
FARMER
  │
  ├── Register/Login
  ├── Create Profile
  ├── Submit Verification
  │
  ▼
ADMIN
  │
  └── Approve Farmer
  │
  ▼
FARMER
  │
  └── Create Produce
  │
  ▼
MARKETPLACE
  │
  ▼
BULK BUYER
  │
  ├── Register/Login
  ├── Buyer Profile
  ├── Browse Produce
  │
  ├── Optional:
  │     Financing Request
  │          ↓
  │     Financier Approval
  │          ↓
  │     ACTIVE Relationship
  │
  └── Place Order
          │
          ▼
        ORDER
          │
          ├── optional FinancingTransaction
          │
          ▼
        P5
          │
          ├── Create Shipment
          ├── Assign
          ├── Pickup
          ├── Route Optimize
          ├── Transit
          ├── Handoff
          └── Deliver
                  │
          ┌───────┴───────┐
          ▼               ▼
       Farmer           Buyer
       Tracking         Tracking
```

Parallel AI flow:

```text
Existing Order/Produce history
            ↓
          Pandas
            ↓
        ML features
            ↓
GradientBoostingRegressor
            ↓
      Demand forecast
            ↓
     Farmer advisory
```

---

# 52. P5 Integration Checklist

Before merging P5:

## Environment

- [ ] Python environment created
- [ ] `requirements.txt` updated if P5 adds dependencies
- [ ] PostgreSQL configured
- [ ] `agri_marketplace` database exists
- [ ] `.env` configured
- [ ] `alembic upgrade head` succeeds

## Authentication

- [ ] P5 uses shared `users`
- [ ] P5 uses shared JWT
- [ ] P5 uses `Role.LOGISTICS`
- [ ] No second auth implementation exists

## Logistics

- [ ] Existing `Shipment` model reused
- [ ] Shipment creation works
- [ ] Shipment lifecycle works
- [ ] Invalid transitions rejected
- [ ] Ownership/authorization checks work
- [ ] Farmer tracking still works
- [ ] Consumer tracking still works
- [ ] Bulk buyer tracking works if included

## Routing

- [ ] OR-Tools integrated
- [ ] Route endpoint works
- [ ] Sample/fixed coordinates used where required
- [ ] No unnecessary live GPS dependency

## AI

- [ ] Historical platform data reused
- [ ] Pandas preprocessing works
- [ ] GradientBoostingRegressor works
- [ ] Forecast endpoint works
- [ ] Farmer advisory works
- [ ] AI does not silently modify business state

## Database

- [ ] New P5 tables have migrations
- [ ] No unrelated migration changes
- [ ] Foreign keys are correct
- [ ] Existing P1–P4 tables remain intact

## Regression

```bash
pytest -q
```

must remain green.

---

# 53. Troubleshooting

## PostgreSQL connection failure

Check:

```text
PostgreSQL service running
        ↓
database agri_marketplace exists
        ↓
username/password correct
        ↓
DATABASE_URL correct
        ↓
port 5432 available
```

Example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@localhost:5432/agri_marketplace
```

---

## `401 Unauthorized`

Check that the request contains:

```text
Authorization: Bearer <access_token>
```

The token may also be expired.

Login again.

---

## `403 Forbidden`

The JWT is valid but the user's role does not satisfy the endpoint's RBAC requirement.

Example:

```text
CONSUMER
   ↓
POST /api/logistics/shipments
   ↓
403
```

---

## `alembic upgrade head` failure

First inspect:

```bash
alembic current
alembic heads
```

Do not manually delete migration history.

If the database is shared, coordinate before resetting it.

---

## Port already in use

Run on another port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then:

```text
http://localhost:8001/docs
```

---

# 54. Development Rules

## Rule 1 — One backend

All P1–P5 code stays in this repository.

## Rule 2 — One database

Use:

```text
agri_marketplace
```

for the current integrated development environment.

## Rule 3 — One authentication system

Reuse:

```text
app/modules/auth/
app/core/security.py
app/core/enums.py
```

## Rule 4 — One Produce source

Use:

```text
app/models/produce.py
```

Do not create another produce/catalog table.

## Rule 5 — One Order source

Use:

```text
app/models/order.py
```

Do not create `BulkBuyerOrder`, `LogisticsOrder`, or another order table.

## Rule 6 — One Shipment source

P5 should use:

```text
app/models/shipment.py
```

Do not create `P5Shipment`.

## Rule 7 — Backend is authoritative

The backend owns:

- authorization
- stock
- order totals
- financing constraints
- financing calculations
- state transitions

P5 should follow the same rule for shipment state and logistics operations.

## Rule 8 — Shared-file coordination

Coordinate before changing:

```text
app/main.py
app/core/enums.py
app/models/shipment.py
app/models/order.py
app/models/__init__.py
requirements.txt
alembic/versions/*
```

---

# 55. Quick Start

For a developer who already knows the architecture:

```bash
git clone https://github.com/thirukkumaran-student/SIH26033-AgriMarketplace.git
cd SIH26033-AgriMarketplace

git checkout Integration
git pull origin Integration

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Create PostgreSQL database:

```text
agri_marketplace
```

Configure `.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/agri_marketplace
JWT_SECRET_KEY=YOUR_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Apply migrations:

```bash
alembic upgrade head
```

Start:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Run tests:

```bash
pytest -q
```

---

# 56. P5 Developer — Start Here

If you are the P5 developer, do not begin by creating a new database or new FastAPI application.

Read these files first:

```text
app/core/enums.py
app/core/database.py
app/core/security.py

app/modules/auth/dependencies.py

app/models/user.py
app/models/order.py
app/models/shipment.py
app/models/produce.py

app/modules/orders/routes.py
app/modules/farmer/shipments_routes.py
app/modules/consumer/tracking_routes.py

app/main.py
alembic/env.py
```

Then implement P5 in this order:

```text
1. Logistics module
       ↓
2. Shipment creation
       ↓
3. Shipment state transitions
       ↓
4. Logistics authorization
       ↓
5. Bulk buyer tracking
       ↓
6. Handoff tracking, if required
       ↓
7. OR-Tools routing
       ↓
8. Demand forecasting
       ↓
9. Farmer advisory
       ↓
10. Alembic migration
       ↓
11. P5 tests
       ↓
12. Full regression: pytest -q
```

The central rule is:

```text
P1–P4 already own the business entities.

P5 owns what happens to a shipment
after an Order becomes a logistics concern.
```

---

# 57. Final Architecture

```text
                         SHARED AUTH
                             │
                             ▼
                           USERS
                             │
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
        ▼                    ▼                     ▼
      FARMER             BUYER / CONSUMER       FINANCIER
        │                    │                     │
        ▼                    ▼                     ▼
     PRODUCE  ───────────► ORDER ◄──────── FINANCING
        │                    │
        │                    ▼
        │                 SHIPMENT
        │                    │
        │              ┌─────┴─────┐
        │              ▼           ▼
        │          LOGISTICS     TRACKING
        │              │
        │              ├── Assignment
        │              ├── Pickup
        │              ├── Transit
        │              ├── Delivery
        │              ├── Handoff
        │              └── Route Optimization
        │
        └───────────────────────────────┐
                                        ▼
                              HISTORICAL PLATFORM DATA
                                        │
                                        ▼
                                      PANDAS
                                        │
                                        ▼
                              ML FEATURE ENGINEERING
                                        │
                                        ▼
                            GradientBoostingRegressor
                                        │
                                        ▼
                                DEMAND FORECAST
                                        │
                                        ▼
                                FARMER ADVISORY
```

**This is the integration contract for the current P1 + P2 + P3 + P4 backend and the intended P5 extension.**
