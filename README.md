# 🌾 DirectFarm — Intelligent Farm-to-Market Marketplace

> **Connecting farmers directly with consumers and bulk buyers through an integrated marketplace, financing, logistics, and AI-driven decision support platform.**

[![SIH 2026](https://img.shields.io/badge/SIH-2026-blue)](#)
[![Problem Statement](https://img.shields.io/badge/PS-SIH26033-green)](#)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB)](#)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)](#)
[![AI](https://img.shields.io/badge/AI-Scikit--learn-orange)](#)
[![Optimization](https://img.shields.io/badge/Optimization-OR--Tools-red)](#)

---

## 📌 About the Project

**DirectFarm** is a digital agricultural marketplace developed for **Smart India Hackathon 2026 – Problem Statement SIH26033**.

The platform addresses a fundamental inefficiency in agricultural supply chains:

> **Multiple intermediaries can reduce farmers' earnings while increasing the price paid by consumers.**

DirectFarm creates a digital connection between:

**Farmers / FPOs → Consumers / Bulk Buyers**

while providing the supporting infrastructure required to make the transaction practical:

- Produce discovery and direct purchasing
- Bulk procurement
- Existing buyer-financier relationships
- Financing workflow
- Logistics coordination
- Route optimization
- Shipment handoff tracking
- Demand forecasting
- AI-driven operational suggestions
- Verification and administrative oversight

The result is a unified digital workflow from **produce listing to final delivery**.

---

# 🎯 Problem We Address

Traditional agricultural supply chains may involve several layers between the producer and the final buyer.

```text
Farmer → Intermediary → Wholesaler → Distributor → Retailer → Consumer

        ↓

Lower farmer realization
Higher consumer price
Limited price transparency
Fragmented logistics
```

DirectFarm introduces a direct digital marketplace:

```text
                 ┌───────────────┐
                 │  Farmer / FPO │
                 └───────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │   DIRECTFARM    │
                │    MARKETPLACE  │
                └───────┬─────────┘
                       /                       /                        ▼     ▼
               Consumer   Bulk Buyer
                            │
                            ▼
                       Financier

                         +

                      Logistics
                         │
                         ▼
                        Buyer
```

The platform therefore addresses not only **market access**, but also the operational processes required after an order is placed.

---

# 💡 Our Solution

| Capability | Purpose |
|---|---|
| **Digital Marketplace** | Direct connection between producers and buyers |
| **Produce Management** | Farmers/FPOs can list and manage available produce |
| **Direct Ordering** | Consumers and bulk buyers can place orders |
| **Financing Workflow** | Supports bulk purchases through existing financier relationships |
| **Logistics Management** | Coordinates pickup, transportation and delivery |
| **Route Optimization** | Generates efficient delivery routes using OR-Tools |
| **Demand Forecasting** | Estimates future demand from historical data |
| **AI Suggestions** | Converts predictions and logistics information into actionable recommendations |
| **Verification** | Establishes trusted platform participants |
| **Handoff Tracking** | Maintains shipment-stage records for traceability |
| **Dispute Management** | Provides a structured mechanism for operational disputes |

---

# 🚜 End-to-End Workflow

```text
Farmer / FPO Registration
          ↓
     Verification
          ↓
    Produce Listing
          ↓
      Marketplace
          ↓
   ┌──────┴──────┐
   ▼             ▼
Consumer      Bulk Buyer
                  ↓
          Existing Financier
                  ↓
          Financing Approval
                  ↓
             Order Created
                  ↓
         Transaction Recorded
                  ↓
         Logistics Assignment
                  ↓
          Route Optimization
                  ↓
                Pickup
                  ↓
             In Transit
                  ↓
               Delivery
                  ↓
          Order Completion
                  ↓
       Demand Forecast + AI
```

---

# 👥 Platform Roles

### 👨‍🌾 Farmer / FPO
- Register and submit verification documents
- Create and manage produce listings
- Manage available quantity and pricing
- View orders
- Coordinate with logistics

### 🛒 Consumer
- Browse available produce
- View product information
- Place orders
- Track order status

### 🏢 Bulk Buyer
- Discover available produce
- Place bulk orders
- Maintain financier relationships
- Request financing for eligible purchases
- Track procurement

### 🏦 Financier
- Maintain financing relationships with buyers
- Review financing requests
- Approve or reject requests
- Define financing terms

### 🚚 Logistics Partner
- Manage shipments
- Accept assignments
- Perform pickup
- Update shipment status
- Record handoffs
- Complete delivery
- Optimize routes

### 🛡️ Admin / Operations
- Review verification requests
- Approve or reject participants
- Monitor operational workflows
- Review disputes

---

# 🤖 AI & Optimization

DirectFarm uses AI and optimization for **operational decision support**, rather than as a decorative chatbot layer.

## Demand Forecasting

```text
Historical Demand
       ↓
Data Cleaning
       ↓
Aggregation
       ↓
Feature Preparation
       ↓
Machine Learning Model
       ↓
Demand Prediction
```

Prototype technologies:

- Pandas
- Scikit-learn
- Gradient Boosting Regression
- Joblib

## AI Suggestion Engine

Forecasting, marketplace and logistics data are converted into deterministic, explainable recommendations.

Examples:

> **High demand:** Tomato demand is predicted to increase. Consider increasing available supply for the forecast period.

> **Low demand:** Predicted demand is relatively low. Avoid significantly increasing additional inventory.

> **Logistics opportunity:** Multiple shipments have nearby pickup locations. Consider consolidating them into an optimized route.

---

# 🚚 Intelligent Logistics

Shipment lifecycle:

```text
CREATED
   ↓
ASSIGNED
   ↓
PICKED_UP
   ↓
IN_TRANSIT
   ↓
DELIVERED
```

Shipment records include:

- Pickup location
- Delivery location
- Logistics partner
- Distance
- Logistics cost
- Route sequence
- Shipment status

## Route Optimization

The prototype uses **Google OR-Tools** to generate feasible optimized routes.

```text
Shipment Locations
        ↓
Route Optimization
        ↓
Feasible Route
        ↓
Logistics Partner
        ↓
Pickup → Transport → Delivery
```

Optimization can consider pickup locations, delivery locations, distance, vehicle capacity and shipment sequence.

---

# 💰 Financing Model

DirectFarm **does not act as a lender**.

A bulk buyer must have an existing relationship with a financier before entering the financed purchasing workflow.

Possible financier categories include:

- Banks
- NBFCs
- Cooperatives
- NGOs
- Government institutions
- Other eligible financing organizations

Example financing terms:

```text
Credit Limit     : ₹5,00,000
Interest Rate    : 12% annually
Tenure           : 30 days
Relationship     : ACTIVE
```

Interest:

```text
Interest = Principal × Annual Rate × Days / 365
```

Workflow:

```text
Bulk Order
    ↓
Transaction Initiated
    ↓
Existing Financier Relationship Verified
    ↓
Financing Request
    ↓
Financier Approval
    ↓
Interest Calculation
    ↓
Order Confirmation
```

### Prototype Boundary

Financing approval is simulated in the prototype. The platform does not perform actual loan disbursement, bank transfers, UPI/card payments, debt collection, or assume buyer credit risk.

---

# 📦 Transaction & Pricing Model

Product pricing, logistics and financing are kept separate.

```text
Farmer
   ├── Produce Price
   └── Logistics Cost → Logistics Partner

Bulk Buyer
   └── Financing → Financier
```

### Platform Commission

```text
Platform Commission = ₹0
```

The platform does not add a marketplace commission to the farmer's produce price.

---

# 🔐 Trust & Verification

```text
Registration
     ↓
Document Submission
     ↓
Admin Review
     ↓
Approved / Rejected
     ↓
Role-Specific Access
```

This provides a basic trust layer while keeping external KYC and government integrations outside the prototype scope.

---

# 📋 Order Lifecycle

### Consumer

```text
CREATED
   ↓
TRANSACTION_INITIATED
   ↓
CONFIRMED
   ↓
LOGISTICS_CREATED
   ↓
PICKED_UP
   ↓
IN_TRANSIT
   ↓
DELIVERED
   ↓
COMPLETED
```

### Bulk Buyer

```text
CREATED
   ↓
TRANSACTION_INITIATED
   ↓
FINANCING_PENDING
   ↓
FINANCING_APPROVED
   ↓
CONFIRMED
   ↓
LOGISTICS_CREATED
   ↓
PICKED_UP
   ↓
IN_TRANSIT
   ↓
DELIVERED
   ↓
COMPLETED
```

The backend is authoritative for stock validation, order totals, financing calculations, permissions and state transitions.

---

# 🔗 Shipment Handoff & Traceability

```text
Farmer
  │
  │ Handoff
  ▼
Logistics Partner
  │
  │ Transport
  ▼
Buyer
```

A handoff can record:

- Actor
- Timestamp
- Location
- Shipment stage
- Condition note
- Evidence

This provides an auditable history of shipment movement.

---

# ⚖️ Dispute Management

Supported dispute categories:

- Quality
- Quantity
- Damage
- Delivery

Lifecycle:

```text
OPEN
  ↓
UNDER_REVIEW
  ↓
ACCEPTED / REJECTED / PARTIAL
```

The prototype records resolution information but does not implement actual payment refunds.

---

# 🏗️ System Architecture

DirectFarm uses a **modular monolith** for the hackathon prototype. This preserves clear module boundaries without introducing unnecessary distributed-system complexity.

```text
                    ┌──────────────────────┐
                    │        Users         │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    React Frontend    │
                    └──────────┬───────────┘
                               │ REST / JSON
                               ↓
              ┌─────────────────────────────────┐
              │          FastAPI Backend         │
              │                                 │
              │  Auth        Catalog            │
              │  Orders      Finance            │
              │  Logistics   Forecasting        │
              │  Admin       Disputes           │
              └───────────────┬─────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ↓                         ↓
        ┌─────────────────┐      ┌──────────────────┐
        │   PostgreSQL    │      │ AI & Optimization│
        │                 │      │                  │
        │ Users           │      │ Pandas           │
        │ Produce         │      │ Scikit-learn     │
        │ Orders          │      │ Gradient Boosting│
        │ Finance         │      │ OR-Tools         │
        │ Shipments       │      │ AI Suggestions   │
        └─────────────────┘      └──────────────────┘
```

---

# 🧩 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | FastAPI / Python |
| API | REST / JSON |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT |
| Password Security | bcrypt / Passlib |
| Data Processing | Pandas |
| Machine Learning | Scikit-learn |
| Forecast Model | GradientBoostingRegressor |
| Optimization | Google OR-Tools |
| Testing | Pytest / HTTPX |

---

# 📁 Repository Structure

```text
DirectFarm/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── catalog/
│   │   │   ├── orders/
│   │   │   ├── finance/
│   │   │   ├── logistics/
│   │   │   ├── disputes/
│   │   │   ├── admin/
│   │   │   └── forecasting/
│   │   ├── ai/
│   │   │   ├── forecasting/
│   │   │   └── routing/
│   │   └── seed/
│   ├── tests/
│   └── uploads/
│
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── routes/
│       └── utils/
│
├── docs/
│   └── api/
│
├── .env.example
├── .gitignore
└── README.md
```

---

# 🚀 Prototype Scope

- [x] User registration
- [x] JWT authentication
- [x] Role-based access control
- [x] Verification workflow
- [x] Farmer produce listing
- [x] Marketplace
- [x] Consumer ordering
- [x] Bulk ordering
- [x] Buyer-financier relationship
- [x] Financing approval workflow
- [x] Interest calculation
- [x] Shipment lifecycle
- [x] Shipment handoffs
- [x] Route optimization
- [x] Demand forecasting
- [x] AI-based suggestions
- [x] Basic dispute workflow
- [x] Administrative verification

---

# 🚧 Prototype Limitations

The current prototype intentionally excludes production integrations that are not required to demonstrate the core solution.

- Real payment gateway
- UPI/card processing
- Actual bank/NBFC API integration
- Government KYC integration
- Aadhaar/GST verification
- Real-time GPS tracking
- Driver mobile application
- SMS/WhatsApp infrastructure
- Debt recovery
- Platform credit-risk assumption
- Production-scale event streaming
- Advanced deep-learning models

These can be introduced during productionization.

---

# 🔮 Future Roadmap

### Phase 1 — Prototype

```text
Marketplace + Orders + Financing
+ Logistics + AI
```

### Phase 2 — Integrations

```text
Payment Gateways
Bank / NBFC APIs
Government Verification
Notification Services
GPS / Mapping
```

### Phase 3 — Intelligence

```text
Advanced Demand Forecasting
Dynamic Pricing
Supply-Demand Matching
Advanced Route Optimization
Risk Analytics
```

### Phase 4 — Scale

```text
Event-Driven Architecture
Distributed Processing
Real-Time Tracking
Scalable Storage
Microservices where justified
```

---

# 🧪 Validation & Testing

Critical business-rule tests include:

```text
✓ Unverified users cannot perform restricted operations
✓ Verified farmers can list produce
✓ Orders exceeding available stock are rejected
✓ Consumer orders create transaction records
✓ Bulk buyers without a financier relationship cannot
  enter the financed workflow
✓ Financing requests require financier approval
✓ Interest is calculated from stored financing terms
✓ Shipment states follow valid transitions
✓ Route optimization returns a feasible route
✓ Pickup and delivery create handoff records
✓ Logistics cost remains separate from produce price
✓ Forecasting produces demand predictions
✓ AI suggestions use actual platform data
```

---

# 🛠️ Local Development

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Git

## Clone

```bash
git clone <repository-url>
cd DirectFarm
```

## Backend

```bash
cd backend
python -m venv venv
```

### Windows

```bash
venv\Scriptsctivate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `.env.example`, then run:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🔑 Security & Configuration

Environment-specific secrets are not committed to the repository.

Use `.env.example` as the configuration template.

Sensitive values such as database credentials and JWT secrets should be supplied through environment variables.

---

# 👨‍💻 Engineering Principles

- **Backend-authoritative business logic**
- **Clear module ownership**
- **Contract-first integration**
- **JWT-based authentication and RBAC**
- **Decimal/Numeric for monetary values**
- **UTC timestamps**
- **Explainable AI**
- **External financing rather than platform lending**
- **Zero platform commission**
- **Modular monolith for prototype simplicity**
- **Production scalability considered without premature infrastructure**

---

# 🏆 Smart India Hackathon 2026

**Problem Statement ID:** `SIH26033`

**Problem Statement:**

> **Multiple intermediaries reduce farmers' earnings and increase consumer prices.**

### Proposed Solution

A digital agricultural marketplace connecting:

```text
Farmers / FPOs
       ↕
Consumers
       ↕
Bulk Buyers
       ↕
Financiers
       ↕
Logistics Partners
```

with AI-assisted demand forecasting and logistics optimization.

---

# 👥 Team

| Member | Responsibility |
|---|---|
| **P1** | Farmer & Admin Verification |
| **P2** | Consumer & Admin Disputes |
| **P3** | Bulk Buyer & Marketplace |
| **P4** | Financier & Financing |
| **P5** | Logistics, AI & Route Optimization |

---

# 📜 License

This project is developed as part of **Smart India Hackathon 2026**.

Add the applicable project license before public distribution.

---

# 📌 Vision

> **Reduce unnecessary intermediaries. Improve market access. Coordinate the supply chain. Use data to make better decisions.**

### DirectFarm

**From farm to buyer, through a transparent and intelligent digital supply chain.**
