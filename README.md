# SIH26033 AgriMarketplace — Backend

Backend for the **SIH26033 AgriMarketplace** project.

This branch (`feature/p2-consumer-admin`) contains the complete backend work from **P1 + P2**:
- Shared Authentication + RBAC
- Farmer Profile + Verification
- Admin Farmer Verification
- Farmer Produce Management
- Shared Orders
- Farmer Shipment View
- Consumer Profile
- Consumer Marketplace
- Checkout / Order Review
- Consumer Orders
- Consumer Shipment Tracking
- Consumer Disputes
- Admin Dispute Management
- Admin Monitoring

> **Important:** This is a modular monolith: one FastAPI backend, one PostgreSQL database, and one shared authentication system. P2 reuses P1's models and APIs; it does not create duplicate Produce or Order systems.

---

## 1. Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL 14+
- SQLAlchemy 2
- Pydantic v2
- PyJWT
- bcrypt
- pytest + httpx
- Uvicorn

---

## 2. Roles

| Role | Main responsibility |
|---|---|
| `FARMER` | Profile, verification, produce, received orders, shipments |
| `CONSUMER` | Marketplace, checkout, orders, tracking, disputes |
| `BULK_BUYER` | Shared buyer order system |
| `FINANCIER` | Reserved for P4 |
| `LOGISTICS` | Reserved for P5 |
| `ADMIN` | Farmer verification, disputes, monitoring |

---

# 3. Requirements

Install these before starting:

### Windows
- Python 3.11 or newer
- PostgreSQL 14 or newer
- Git

Check:

```bash
python --version
psql --version
git --version
```

> PostgreSQL is required to run the actual backend.  
> The automated test suite uses a disposable SQLite database, so PostgreSQL is **not required just to run tests**.

---

# 4. Get the Project

Clone the repository:

```bash
git clone https://github.com/thenameisrghratgit/SIH26033-AgriMarketplace.git
cd SIH26033-AgriMarketplace/backend
```

If the repository has already been cloned:

```bash
git checkout feature/p2-consumer-admin
git pull origin feature/p2-consumer-admin
```

> The `feature/p2-consumer-admin` branch contains **P1 + P2**, so you do not need to separately download the P1 branch.

---

# 5. Create a Virtual Environment

From the `backend/` directory:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of the terminal prompt.

---

# 6. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 7. Create the PostgreSQL Database

Open **pgAdmin** or a PostgreSQL terminal and create a database named:

```text
sih26033
```

Using `psql`:

```bash
psql -U postgres -c "CREATE DATABASE sih26033;"
```

If the database already exists, do not create it again.

You can verify it in pgAdmin under:

```text
Servers
└── PostgreSQL
    └── Databases
        └── sih26033
```

---

# 8. Configure `.env`

Copy the example file:

### PowerShell

```powershell
Copy-Item .env.example .env
```

### CMD

```cmd
copy .env.example .env
```

### Git Bash / Linux / macOS

```bash
cp .env.example .env
```

Open `.env` and set your local PostgreSQL credentials.

Example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/sih26033
JWT_SECRET_KEY=YOUR_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure JWT secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Then put the generated value into `JWT_SECRET_KEY`.

> **Never commit `.env` or real passwords/secrets to GitHub.**

---

# 9. Start the Backend

Make sure you are inside:

```text
SIH26033-AgriMarketplace/backend
```

and that the virtual environment is active.

Run:

```bash
uvicorn app.main:app --reload
```

You should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

The database tables are created automatically on startup if they do not already exist.

---

# 10. Check That the Backend Works

Open:

### Health check
```text
http://localhost:8000/
```

### Swagger API documentation
```text
http://localhost:8000/docs
```

### ReDoc
```text
http://localhost:8000/redoc
```

**Swagger is the easiest way for a new developer to test the entire backend.**

---

# 11. API Modules

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
GET  /api/auth/test-farmer
GET  /api/auth/test-admin
```

`/test-farmer` and `/test-admin` are development/RBAC demonstration endpoints.

---

## Farmer Profile

```text
POST /api/farmer/profile
GET  /api/farmer/profile
PUT  /api/farmer/profile
```

---

## Farmer Verification

```text
POST /api/verification/documents
GET  /api/verification/status
```

---

## Admin Verification

```text
GET  /api/admin/verifications
GET  /api/admin/verifications/{user_id}
POST /api/admin/verifications/{user_id}/approve
POST /api/admin/verifications/{user_id}/reject
```

---

## Produce

```text
POST   /api/produce
GET    /api/produce
GET    /api/produce/{id}
PATCH  /api/produce/{id}
DELETE /api/produce/{id}
```

Only an **APPROVED farmer** can create produce.

Produce is the **single source of truth** for marketplace listings.

---

## Shared Orders

```text
POST  /api/orders
GET   /api/orders
GET   /api/orders/{order_id}
PATCH /api/orders/{order_id}/status
POST  /api/orders/review
```

The same Order system is reused by consumers and bulk buyers.

The backend calculates the order total from the database price:

```text
total = quantity × unit_price
```

The client cannot choose the final price or farmer ID.

---

## Farmer Shipment View

```text
GET /api/farmer/shipments
GET /api/farmer/shipments/{shipment_id}
```

---

## Consumer Profile

```text
POST /api/consumer/profile
GET  /api/consumer/profile
PUT  /api/consumer/profile
```

---

## Consumer Marketplace

```text
GET /api/consumer/marketplace
```

Supports marketplace filtering such as:
- Crop
- Location
- Maximum price
- Combined filters

Only eligible listings are exposed to the consumer marketplace:
- Farmer is approved
- Produce is active
- Quantity is greater than zero

---

## Consumer Shipment Tracking

```text
GET /api/consumer/shipments
GET /api/consumer/shipments/{shipment_id}
```

A consumer can only view shipments belonging to their own orders.

---

## Consumer Disputes

```text
POST /api/consumer/disputes
```

---

## Admin Disputes

```text
GET  /api/admin/disputes
GET  /api/admin/disputes/{dispute_id}
POST /api/admin/disputes/{dispute_id}/resolve
```

---

## Admin Monitoring

```text
GET /api/admin/monitoring
```

Checks backend/database availability and returns an appropriate status.

---

# 12. Recommended Demo / Testing Flow

If you are a new developer or evaluator and want to verify the complete P1 + P2 backend, use this order.

## Step 1 — Start the server

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

## Step 2 — Create a Farmer

In Swagger:

```text
POST /api/auth/register
```

Use:

```json
{
  "name": "Test Farmer",
  "email": "farmer@example.com",
  "password": "password123",
  "role": "FARMER"
}
```

Then use:

```text
POST /api/auth/login
```

Copy the returned `access_token`.

Click **Authorize** in Swagger and enter:

```text
Bearer YOUR_TOKEN
```

---

## Step 3 — Create Farmer Profile

Call:

```text
POST /api/farmer/profile
```

Example:

```json
{
  "phone": "9876543210",
  "farm_name": "Green Acres",
  "farm_size_acres": 15.0,
  "farm_location": "Chennai",
  "soil_type": "Loamy",
  "irrigation_type": "Drip"
}
```

---

## Step 4 — Submit Verification

Call:

```text
POST /api/verification/documents
```

Example:

```json
{
  "document_type": "AADHAAR",
  "document_number": "TEST-AADHAAR-1234"
}
```

The document initially becomes:

```text
PENDING
```

---

## Step 5 — Create an Admin

Log out/change authorization and register:

```json
{
  "name": "Test Admin",
  "email": "admin@example.com",
  "password": "password123",
  "role": "ADMIN"
}
```

Login as the admin and authorize Swagger with the admin token.

---

## Step 6 — Approve the Farmer

Admin calls:

```text
GET /api/admin/verifications
```

Find the farmer's `user_id`.

Then:

```text
POST /api/admin/verifications/{user_id}/approve
```

The farmer's verification status should now be:

```text
APPROVED
```

---

## Step 7 — Create Produce as the Farmer

Switch back to the farmer token.

Call:

```text
POST /api/produce
```

Example:

```json
{
  "crop_name": "Tomato",
  "quantity": 100,
  "unit": "kg",
  "price_per_unit": 40,
  "harvest_date": "2026-09-01",
  "location": "Chennai"
}
```

The listing should be created as:

```text
ACTIVE
```

---

## Step 8 — Create a Consumer

Register:

```json
{
  "name": "Test Consumer",
  "email": "consumer@example.com",
  "password": "password123",
  "role": "CONSUMER"
}
```

Login and authorize Swagger with the consumer token.

---

## Step 9 — Create Consumer Profile

Call:

```text
POST /api/consumer/profile
```

Example:

```json
{
  "phone": "9876543211",
  "address": "Test Address",
  "city": "Chennai",
  "state": "Tamil Nadu",
  "pincode": "600001"
}
```

---

## Step 10 — Check Marketplace

Call:

```text
GET /api/consumer/marketplace
```

The approved farmer's active produce should appear.

Try the filters as well.

---

## Step 11 — Review Checkout

Call:

```text
POST /api/orders/review
```

Provide the `produce_id` and desired quantity.

The response should show the price and calculated total.

**This endpoint is read-only and does not reduce stock.**

---

## Step 12 — Place the Order

Call:

```text
POST /api/orders
```

Example:

```json
{
  "produce_id": 1,
  "quantity": 5
}
```

The backend should:
- Validate the produce
- Validate farmer approval
- Validate available stock
- Calculate the total
- Determine the farmer automatically
- Reduce stock
- Create the order

---

## Step 13 — Check Consumer Orders

As the consumer:

```text
GET /api/orders
```

You should see the order.

---

## Step 14 — Confirm the Order as Farmer

Switch to the farmer token.

Call:

```text
GET /api/orders
```

Find the order and update it:

```text
PATCH /api/orders/{order_id}/status
```

Set:

```json
{
  "status": "CONFIRMED"
}
```

Then later:

```text
COMPLETED
```

---

## Step 15 — Check Shipments

Farmer:

```text
GET /api/farmer/shipments
```

Consumer:

```text
GET /api/consumer/shipments
```

Each role only receives shipments it is authorized to view.

---

## Step 16 — Test a Consumer Dispute

As the consumer:

```text
POST /api/consumer/disputes
```

Then switch to admin and check:

```text
GET /api/admin/disputes
```

Open the dispute:

```text
GET /api/admin/disputes/{dispute_id}
```

Resolve it:

```text
POST /api/admin/disputes/{dispute_id}/resolve
```

---

## Step 17 — Check Admin Monitoring

As admin:

```text
GET /api/admin/monitoring
```

It should return a healthy/OK response when the backend and database are available.

---

# 13. Authentication in Swagger

For protected endpoints:

1. Call `POST /api/auth/login`.
2. Copy the `access_token`.
3. Click **Authorize** in the top-right of Swagger.
4. Enter the token using the format:

```text
Bearer YOUR_ACCESS_TOKEN
```

5. Click **Authorize**.
6. You can now call endpoints allowed for that role.

### Expected authorization behavior

| Situation | Response |
|---|---:|
| No token | `401` |
| Invalid/expired token | `401` |
| Valid token, wrong role | `403` |
| Valid token, correct role | Allowed |

---

# 14. Farmer Verification Rules

A farmer must complete verification before creating produce.

```text
Register Farmer
      ↓
Create Farmer Profile
      ↓
Submit Verification Document
      ↓
PENDING
      ↓
Admin Review
   ↙       ↘
REJECTED   APPROVED
              ↓
        Create Produce
```

Only `APPROVED` farmers can create produce.

Marketplace listings also require the farmer to be approved.

---

# 15. Produce Rules

Produce statuses:

```text
ACTIVE
INACTIVE
SOLD_OUT
```

Important rules:
- Create requires an approved farmer.
- Quantity must be greater than zero when creating a listing.
- A listing belongs to its farmer.
- Only the owning farmer can update/delete it.
- Stock is used by the shared order system.
- Marketplace reads the same Produce data; there is no duplicate product table.

---

# 16. Order Rules

Buyer roles:

```text
CONSUMER
BULK_BUYER
```

Order flow:

```text
PENDING → CONFIRMED → COMPLETED
    │
    └────────→ CANCELLED
```

- Buyer can cancel a pending order.
- Cancellation restores stock.
- Farmer can confirm a pending order.
- Farmer can complete a confirmed order.
- Backend calculates totals.
- Farmer ID comes from the Produce owner.
- A farmer cannot order their own produce.
- Stock cannot be intentionally set by the client.

---

# 17. Consumer Marketplace Rules

The consumer marketplace uses the existing Produce model.

It does **not** create another product table.

A listing is shown when:

```text
Farmer verification = APPROVED
AND
Produce status = ACTIVE
AND
Quantity > 0
```

Sensitive farmer information such as internal user IDs, verification documents, and unnecessary contact information is not exposed through the marketplace response.

---

# 18. Dispute Rules

Consumers can raise disputes against their own orders.

The backend prevents:
- Users disputing someone else's order
- Multiple open disputes for the same order
- Disputes against cancelled orders

Admin can resolve an open dispute as:

```text
ACCEPTED
REJECTED
PARTIAL
```

This prototype does **not** perform real payment refunds.

---

# 19. Run the Automated Tests

The test suite uses a disposable SQLite database.

You can run it without PostgreSQL:

```bash
pytest
```

For a shorter output:

```bash
pytest -q
```

Run a specific module:

```bash
pytest tests/test_auth.py
pytest tests/test_produce.py
pytest tests/test_orders.py
pytest tests/test_consumer.py
pytest tests/test_marketplace.py
pytest tests/test_consumer_orders.py
pytest tests/test_checkout.py
pytest tests/test_consumer_tracking.py
pytest tests/test_disputes.py
pytest tests/test_monitoring.py
```

The complete P1 + P2 suite should pass before making major changes.

---

# 20. Test What Each Suite Covers

| Test file | Main coverage |
|---|---|
| `test_auth.py` | Registration, login, JWT, RBAC |
| `test_farmer.py` | Farmer profile + verification |
| `test_admin.py` | Admin farmer verification |
| `test_produce.py` | Produce CRUD + ownership + approval rules |
| `test_orders.py` | Shared order rules + stock |
| `test_shipment.py` | Farmer shipment access |
| `test_consumer.py` | Consumer profile |
| `test_marketplace.py` | Marketplace visibility + filters |
| `test_consumer_orders.py` | Consumer ordering integration |
| `test_checkout.py` | Read-only order review |
| `test_consumer_tracking.py` | Consumer shipment access |
| `test_disputes.py` | Consumer disputes + admin resolution |
| `test_monitoring.py` | Admin monitoring |

---

# 21. Database Tables

The backend uses one shared PostgreSQL database.

Main tables include:

```text
users
farmer_profiles
verification_documents
consumer_profiles
produce
orders
shipments
disputes
```

All roles use the same `users` table.

Do not create separate authentication or order systems for individual roles.

---

# 22. Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── enums.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── farmer.py
│   │   ├── consumer.py
│   │   ├── produce.py
│   │   ├── order.py
│   │   ├── shipment.py
│   │   └── dispute.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── farmer.py
│   │   ├── consumer.py
│   │   ├── admin.py
│   │   ├── produce.py
│   │   ├── order.py
│   │   ├── shipment.py
│   │   └── dispute.py
│   └── modules/
│       ├── auth/
│       ├── farmer/
│       ├── consumer/
│       ├── produce/
│       ├── orders/
│       └── admin/
├── tests/
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# 23. Important Development Rules

### Shared authentication

Use:

```python
get_current_user
require_role(...)
```

from:

```text
app/modules/auth/dependencies.py
```

Do not create another JWT/authentication system.

### Shared Produce

Produce is the **single source of truth**.

Marketplace and consumer features must read the existing Produce model/API.

### Shared Orders

Orders are shared across buyer roles.

Do not create:
- `ConsumerOrder`
- `BulkBuyerOrder`
- another duplicate order table

### Logistics

The current shipment endpoints provide role-specific shipment views.

P5 owns future logistics/route optimization functionality.

---

# 24. Current Prototype Limitations

These are intentionally outside the current P1/P2 scope:

- Production database migrations/Alembic
- Concurrent stock reservation/overselling protection
- Real payment gateway/refunds
- Real KYC verification API
- Live GPS tracking
- Full logistics route optimization
- Production-grade background jobs
- Redis/Kafka/microservices
- Advanced observability

These should be added only when the relevant team module requires them.

---

# 25. Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and dependencies are installed:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### PostgreSQL connection error

Check:
1. PostgreSQL service is running.
2. Database `sih26033` exists.
3. Username/password in `.env` are correct.
4. PostgreSQL is listening on the expected port, normally `5432`.

### `Address already in use`

Another Uvicorn process may already be running.

Stop it or use another port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://localhost:8001/docs
```

### Tables are missing

Restart the backend:

```bash
uvicorn app.main:app --reload
```

The prototype creates missing tables automatically on startup.

### Swagger gives `401`

You probably have not authorized the current token.

Click **Authorize** and enter:

```text
Bearer YOUR_TOKEN
```

### Swagger gives `403`

The token is valid, but that role is not allowed to access the endpoint.

For example, a consumer cannot call an admin-only endpoint.

---

# 26. Quick Start

For an experienced developer, the minimum commands are:

```bash
git clone https://github.com/thenameisrghratgit/SIH26033-AgriMarketplace.git
cd SIH26033-AgriMarketplace/backend

git checkout feature/p2-consumer-admin

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# Create PostgreSQL database: sih26033
# Configure .env

uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/docs
```

To run all automated tests:

```bash
pytest -q
```

---

# 27. P1 + P2 Branch

The branch:

```text
feature/p2-consumer-admin
```

contains the completed **P1 + P2 backend implementation**.

So a reviewer only needs this branch to inspect the combined work.

```text
P1 Farmer/Admin
       ↓
feature/p1-farmer-admin
       ↓
P2 Consumer/Admin
       ↓
feature/p2-consumer-admin
       ↑
   P1 + P2
```

---

## Final verification checklist

Before considering the backend ready for review:

- [ ] PostgreSQL database created
- [ ] `.env` configured
- [ ] Dependencies installed
- [ ] Backend starts successfully
- [ ] `/docs` opens
- [ ] Farmer registration/login works
- [ ] Farmer verification workflow works
- [ ] Admin approval works
- [ ] Produce creation works after approval
- [ ] Consumer registration/login works
- [ ] Marketplace displays eligible produce
- [ ] Checkout review works
- [ ] Order placement works
- [ ] Farmer can view/update orders
- [ ] Consumer can view orders
- [ ] Shipment access works for both sides
- [ ] Consumer dispute works
- [ ] Admin dispute resolution works
- [ ] Admin monitoring works
- [ ] `pytest -q` passes

---

**For the complete P1 + P2 backend, start with the Quick Start section, open Swagger, and follow the Recommended Demo / Testing Flow.**
