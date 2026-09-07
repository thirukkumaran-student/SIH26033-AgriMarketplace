# Integrated Backend Reference

This file describes the backend that is actually present on the `Integration` branch. The backend remains the original FastAPI modular monolith; the React application in `frontend/` is a client of these contracts.

## Startup and security

`app/main.py` creates the single FastAPI application and includes every module router. `app/core/config.py` reads `.env`; `app/core/database.py` creates the SQLAlchemy engine/session; `app/core/security.py` hashes passwords with bcrypt and signs/validates JWTs. Role checks use `require_role(...)` and query the current database user rather than accepting a role from the browser.

The configured frontend origin is allowed by CORS. Authentication is bearer-token based:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

## Major route groups

| Area | Prefix / endpoints | Authorized roles |
| --- | --- | --- |
| Farmer profile | `/api/farmer/profile` | Farmer |
| Verification | `/api/verification/documents`, `/api/verification/status` | Farmer |
| Produce | `/api/produce` CRUD | Authenticated read; approved owning farmer write |
| Marketplace | `/api/marketplace/produce` | Consumer, bulk buyer |
| Orders | `/api/orders/review`, `/api/orders`, `/api/orders/{id}`, status update | Consumer, bulk buyer, farmer, admin as enforced per operation |
| Consumer profile/tracking | `/api/consumer/profile`, `/api/consumer/shipments` | Consumer |
| Disputes | `/api/consumer/disputes`, `/api/admin/disputes` | Consumer/admin respectively |
| Bulk-buyer profile | `/api/buyer/profile` | Bulk buyer |
| Financier profile/list | `/api/financier` | Financier profile; authenticated approved-list access |
| Finance | `/api/finance/requests`, relationships, transactions, repayment | Bulk buyer/financier by ownership and operation |
| Farmer shipments | `/api/farmer/shipments` | Farmer owning the related order |
| Logistics | `/api/logistics/shipments`, status actions, route optimizer, handoffs | Logistics |
| Forecast | `/api/forecast/`, `/predict`, `/train` | Farmer/bulk buyer/admin; training admin-only |
| Suggestions | `/api/suggestions/` | Farmer/bulk buyer/admin |
| Admin | `/api/admin/verifications`, monitoring, orders, disputes | Admin |
| Mandi prices | `GET /api/market-prices` | Farmer, consumer, bulk buyer, admin |

Use `/docs` or `/openapi.json` on a running server for the exact request and response schemas.

## Core lifecycles

### Marketplace and orders

Only active, in-stock produce from farmers whose verification documents are all approved appears in the marketplace. A buyer first calls order review; the server reads the authoritative unit price and stock. Order placement repeats validation, creates the order, and reduces stock transactionally. Farmers and buyers can perform only the status transitions allowed by the existing state machine.

### Finance

A bulk buyer sends a request to an approved financier. The assigned financier rejects it or approves terms. The owning buyer may select an approved offer, creating an active relationship. Platform-financed order creation validates relationship ownership and available credit and creates the finance transaction in the same database transaction. Repayment updates the transaction and restores credit according to the service rules.

### Shipments, routes, and handoffs

A logistics user creates a shipment for an existing order. The supported path is `PENDING -> ASSIGNED -> PICKED_UP -> IN_TRANSIT -> DELIVERED`; invalid jumps are rejected. Farmers and consumers have ownership-scoped read views. Logistics operators can append custody handoffs. Route optimization uses OR-Tools over a caller-supplied square integer distance matrix.

### Forecasting

The forecast service derives a machine-learning prediction from the existing order/activity data and stores generated forecast records. Prediction history is available to farmers, bulk buyers, and admins. Suggestions combine a forecast result with supplied available quantity. These values are decision support and are not represented as guaranteed demand.

### CEDA market prices

`app/modules/market_prices/` is the only new backend integration module. The endpoint accepts human-readable filters, resolves IDs through the documented CEDA Agmarknet lookup endpoints, calls the price endpoint with a bearer key held only in backend configuration, validates the response, and normalizes price observations as rupees per quintal. It is a focused adapter, not a general proxy.

Failure behavior:

- Missing `CEDA_API_KEY`: `503` with a clear configuration message
- Unknown commodity/geography/market: `404`
- CEDA network or schema failure with no cache: `502`
- Failure after an identical successful query: return the process-local cached response with `stale_cache: true`

## Database and migrations

Production configuration targets PostgreSQL through `DATABASE_URL`; SQLAlchemy 2.x is the ORM and Alembic manages the schema. Current migrations are:

- `70d7a0f1364c_initial_schema.py`
- `f22e87c8b2a0_migrate_marketplace_money_fields_to_.py`
- `315606f9e7b2_add_forecasts_table.py`
- `76f7011ef89e_add_handoffs_table.py`

No migration is required for CEDA because the small fallback cache is in memory.

## Verification

Run from the repository root:

```powershell
.venv\Scripts\python.exe -m compileall -q app tests
.venv\Scripts\python.exe -m pytest -q
```

The CEDA tests mock lookup and price payloads, assert normalization, reject malformed payloads, check authentication, and verify graceful missing-key/upstream-failure behavior. Live external access is intentionally not required by the test suite.

For setup, frontend details, environment variables, and current limitations, use the root [README.md](README.md).
