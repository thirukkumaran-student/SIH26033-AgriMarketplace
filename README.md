# AgroSave — SIH26033 AgriMarketplace

AgroSave is a role-based agricultural marketplace for farmers, consumers, bulk buyers, financiers, logistics operators, and administrators. The current `Integration` branch contains one FastAPI backend and one React frontend. Produce, orders, finance, and shipments all use the existing shared database models; there is no duplicate marketplace or backend service.

## What is implemented

- Email/password registration and login with JWT bearer tokens
- Backend-derived current user and role through `GET /api/auth/me`
- Farmer profiles, verification documents, produce CRUD, orders, shipments, forecasts, and suggestions
- Consumer profiles, verified-produce marketplace, order review/placement, order history, shipment tracking, and disputes
- Bulk-buyer profiles, marketplace procurement, orders, financing requests/offers, relationships, and transactions
- Financier profiles and request approval/rejection workflows
- Logistics shipment creation, sequential status transitions, route optimization, and custody handoffs
- Admin farmer verification, dispute resolution, order monitoring, and service/database health
- React dashboards and navigation tailored to all six roles
- A focused FastAPI integration with CEDA Agri Market/Agmarknet price observations
- An optional, feature-detected WebMCP order tool for supported browsers; it reuses the same review/create APIs

The backend code is the source of truth. Earlier documentation that described logistics or forecasting as unimplemented was stale: both modules and their migrations are present on this branch.

## Architecture

```text
React + Vite (frontend/)
        |
        | JSON + Authorization: Bearer <JWT>
        v
FastAPI (app/main.py)
        |
        +-- SQLAlchemy models/services --> PostgreSQL
        +-- /api/market-prices ---------> CEDA Agri Market API
```

The backend is a modular monolith:

- `app/core/`: settings, database engine/session, enums, and JWT/password utilities
- `app/models/`: shared SQLAlchemy entities
- `app/schemas/`: request/response validation for core marketplace flows
- `app/modules/`: auth, farmer, produce, marketplace/consumer, orders, finance, financier, logistics, admin, forecast, suggestions, and market prices
- `alembic/versions/`: initial schema, decimal money migration, forecast table, and handoff table
- `tests/`: API, RBAC, integrity, end-to-end finance, logistics, and CEDA integration tests
- `frontend/src/api/`: small endpoint-focused client modules over one authenticated fetch client
- `frontend/src/pages/`: role and workflow pages
- `frontend/src/layouts/`: shared authenticated dashboard shell

## Data model

`users` is the shared identity table. Role-specific profile tables reference it. Farmers own `produce`; buyer users place `orders` for produce; shipments reference orders; disputes reference consumer orders; verification documents reference farmers. Finance requests can become buyer-financier relationships, which fund order-linked transactions. Forecasts store generated prediction results, while shipment handoffs store custody history.

The supported roles are:

- `FARMER`
- `CONSUMER`
- `BULK_BUYER`
- `FINANCIER`
- `LOGISTICS`
- `ADMIN`

Frontend route visibility is role-aware, but it is not a security boundary. FastAPI dependencies validate the JWT, load the current database user, and enforce role access. Forecast history/prediction and suggestions are limited to farmers, bulk buyers, and admins; model training is admin-only.

## Frontend

The frontend uses React, Vite, React Router, plain CSS, Lucide React, and Recharts. It deliberately does not use Redux, OAuth, WebSockets, or a large component framework.

Public pages include the landing page, login, registration, and a how-it-works section. Authenticated pages map only to backend capabilities:

- Farmer: dashboard, produce CRUD, orders, shipments, forecast/suggestions, verification, profile, and mandi reference prices
- Consumer: dashboard, marketplace/detail, order review and placement, orders, shipments, disputes, and profile
- Bulk buyer: dashboard, marketplace/detail, orders, financing, and profile
- Financier: dashboard, financing request decisions, and profile
- Logistics: dashboard, shipments/detail, assignment through delivery, handoffs, and route optimization
- Admin: dashboard, farmer verification, disputes, monitoring, and orders

Every API-driven view provides an explicit loading, failure, empty, or content state. The layouts are desktop-first and adapt to tablet/mobile widths.

## Authentication flow

1. The browser submits credentials to `POST /api/auth/login`.
2. The prototype stores the returned access token in `localStorage`.
3. The shared API client attaches `Authorization: Bearer <token>`.
4. The frontend calls `GET /api/auth/me` and uses that backend identity for routing.
5. A `401` clears the local token and returns the user to login.

For a production browser deployment, consider an HttpOnly cookie/session strategy and CSRF protection. The present storage choice is intentionally simple for the SIH prototype.

## CEDA / Agmarknet market prices

`GET /api/market-prices` is a focused, authenticated backend adapter. It accepts human-readable `commodity`, `state`, `district`, optional `market`, `from_date`, and `to_date` values. The backend resolves CEDA IDs using the documented commodity, geography, and market endpoints, then requests price observations and returns this normalized shape:

```json
{
  "source": "CEDA Agri Market Data (Agmarknet)",
  "attribution": "Centre for Economic Data & Analysis, Ashoka University",
  "price_unit": "INR_PER_QUINTAL",
  "commodity": "Tomato",
  "state": "Tamil Nadu",
  "district": "Chennai",
  "latest_observation": "2026-09-06",
  "age_days": 1,
  "stale_cache": false,
  "markets": [
    {
      "market": "Koyambedu",
      "market_id": 1001,
      "date": "2026-09-06",
      "min_price": 2400.0,
      "max_price": 3100.0,
      "modal_price": 2800.0
    }
  ]
}
```

The numbers above illustrate the response contract used by automated mocks; they are not claimed as current market observations. The UI labels the actual returned observation date and age, keeps the farmer's listing price separate, and never changes a listing automatically. A small in-process last-success cache is used only for the same filter/date query; cached fallback is clearly marked. If no key or cache is available, the panel reports that market prices are unavailable without breaking the dashboard.

The API key is backend-only. Never add it to `frontend/.env` or any `VITE_` variable.

## Configuration

Copy the examples, then replace placeholders:

```powershell
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
```

Backend variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy PostgreSQL URL |
| `JWT_SECRET_KEY` | Secret used to sign access tokens |
| `JWT_ALGORITHM` | JWT algorithm; defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime |
| `FRONTEND_ORIGIN` | Browser origin allowed by CORS |
| `CEDA_API_KEY` | CEDA bearer key; optional, untracked, backend-only |
| `CEDA_API_BASE_URL` | Defaults to `https://api.ceda.ashoka.edu.in/v1` |

Frontend variables:

| Variable | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | FastAPI origin, default `http://127.0.0.1:8000` |

## Run locally

Backend (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env, create the PostgreSQL database, then:
.venv\Scripts\alembic.exe upgrade head
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend, in another terminal:

```powershell
Set-Location frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`. FastAPI documentation is at `http://127.0.0.1:8000/docs`.

## Tests and build

Backend tests use a disposable SQLite database unless `TEST_DATABASE_URL` names a dedicated PostgreSQL test database. They never require live CEDA access.

```powershell
.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm run lint
npm run build
```

## Current limitations and planned work

- A real CEDA observation cannot be verified without a valid `CEDA_API_KEY`; automated tests mock documented responses.
- CEDA publishes the cleaned Agri Market dataset on a monthly update cadence, so the application reports observation date/age rather than calling it live data.
- The in-memory market-price fallback is process-local and resets on restart.
- Bulk-buyer shipment retrieval is not exposed by the backend, so that dashboard shows order status without inventing shipment data.
- Route optimization accepts a supplied integer distance matrix; it does not geocode addresses or persist routes.
- Forecasting is an activity-derived decision-support signal, not a guarantee of future consumer demand.
- Public registration remains compatible with the existing backend contract. Operational roles should be provisioned under a stricter production policy.
- Automated frontend unit/browser tests are not configured; the verified checks are ESLint, a production build, and manual route/shell inspection.
- The preview browser did not provide a usable WebMCP validation context, so tool registration could not be contract-tested there; unsupported browsers simply ignore it.
- Payments, notifications, password reset, media upload/storage, production deployment, and websocket updates are outside this integration.

## API overview

Major route groups consumed by the frontend are `/api/auth`, `/api/farmer`, `/api/consumer`, `/api/buyer`, `/api/financier`, `/api/verification`, `/api/produce`, `/api/marketplace`, `/api/orders`, `/api/finance`, `/api/logistics`, `/api/forecast`, `/api/suggestions`, `/api/admin`, and `/api/market-prices`.

See [README_Integrated_Backend.md](README_Integrated_Backend.md) for the backend route and lifecycle summary.
