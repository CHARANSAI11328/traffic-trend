# TRAFFIC TREND — ROAD SAFETY INTELLIGENCE PLATFORM
### Full-Stack Web Application | Python Data Science | Interactive Analytics | Modern UI/UX

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Neon_PostgreSQL-18.6-336791.svg?logo=postgresql&logoColor=white)](https://neon.tech/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Apache ECharts](https://img.shields.io/badge/Apache_ECharts-5.5-AA344D.svg?logo=apache-echarts&logoColor=white)](https://echarts.apache.org/)
[![Tests](https://img.shields.io/badge/Backend_Tests-13%2F13_Passed-brightgreen.svg)](TEST_REPORT.md)

---

## 1. Executive Platform Overview

**TRAFFIC TREND** is an institutional-grade, full-stack road safety intelligence and accident analytics platform engineered for transportation ministries, urban planning agencies, highway authorities, and academic data science researchers.

The platform bridges enterprise data science with high-frequency interactive analytics, providing deep visibility into spatiotemporal accident patterns, severity determinants, casualty dynamics, risk indices, data hygiene auditing, and automated publication-quality executive briefs.

> **Operational Notice:** Configured in **Historical / Uploaded Data Mode**. Live government feeds (MoRTH/Vahan/NHTSA APIs) are purposefully decoupled behind a connector interface until official streaming credentials and rate limits are provisioned.

---

## 2. System Architecture

```text
TRAFFIC-TREND/
│
├── frontend/                                # Next.js 14 App Router (React, TypeScript, Tailwind)
│   ├── app/                                 # App Router Route Segments
│   │   ├── (dashboard)/
│   │   │   ├── overview/                    # Executive KPI cards, YoY trends, regional rankings
│   │   │   ├── accidents/                   # Searchable tabular explorer with modal deep-dive
│   │   │   ├── geography/                   # Spatial heatmaps, cluster maps, state/district rankings
│   │   │   ├── trends/                      # Longitudinal, seasonality, diurnal 24hr, heatmaps
│   │   │   ├── severity/                    # Severity distributions, casualty matrices, vehicle shares
│   │   │   ├── intelligence/                # Statistical anomalies, risk indexing, OLS forecasts
│   │   │   ├── data-management/             # Upload engine, 4D scorecard, cleaning pipeline
│   │   │   ├── reports/                     # ReportLab PDF & multi-tab Excel workbook downloads
│   │   │   └── system/                      # Telemetry, DB health, latency, live SSE event feed
│   │   ├── login/                           # JWT credentials authentication portal
│   │   ├── layout.tsx                       # Root layout with QueryClient & Global Theme
│   │   └── page.tsx                         # Brand landing page & dataset quick stats
│   ├── components/
│   │   ├── layout/                          # Sidebar, TopNav, GlobalFilterBar
│   │   ├── dashboard/                       # Reusable KPICard, StatusBadge
│   │   ├── charts/                          # Apache ECharts wrapper (EChartComponent)
│   │   └── maps/                            # MapLibre GL JS vector map wrapper
│   ├── services/api.ts                      # Centralized typed Axios/Fetch API client
│   └── types/index.ts                       # Shared TypeScript interfaces
│
├── backend/                                 # Python 3.11+ / FastAPI Analytics Engine
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/                      # auth, dashboard, analytics, datasets, reports, system
│   │   │   └── dependencies.py              # Repository injection & JWT auth guards
│   │   ├── core/                            # config.py, security.py (pure bcrypt + JWT)
│   │   ├── data/                            # loader.py, cleaner.py, profiler.py, validator.py
│   │   ├── analytics/                       # kpis.py, trends.py, geography.py, severity.py,
│   │   │                                    # correlation.py, anomalies.py, forecasting.py
│   │   ├── database/                        # connection.py (Neon Postgres + SQLite), models.py, repository.py
│   │   ├── reports/                         # pdf_generator.py (ReportLab), excel_exporter.py (OpenPyXL)
│   │   ├── monitoring/                      # health.py, data_freshness.py, logger.py
│   │   └── schemas/                         # Pydantic V2 request & response schemas
│   └── tests/test_api.py                    # Pytest backend API integration suite (13/13 passing)
│
├── data/
│   ├── raw/                                 # Read-only benchmark dataset (3,500 records)
│   ├── processed/                           # Sanitized & normalized Parquet/CSV storage
│   └── exports/                             # Generated PDF and Excel workbooks
│
├── legacy_streamlit/                        # Archived legacy prototype (preserved intact)
├── notebooks/Traffic_Trend_Analysis.ipynb   # Comprehensive Jupyter research notebook
├── docs/                                    # Architectural & analytical documentation
│   ├── PROJECT_AUDIT.md
│   ├── DATA_DICTIONARY.md
│   ├── ANALYTICAL_METHODOLOGY.md
│   └── ARCHITECTURE.md
├── docker-compose.yml                       # Multi-container orchestration (FastAPI + Next.js + Postgres + Redis)
└── README.md
```

---

## 3. Technology Stack & Key Libraries

### Frontend
- **Framework:** Next.js 14.2.23 (App Router, React 18, TypeScript)
- **Styling:** Tailwind CSS 3.4 with Deep Midnight Navy palette (`#080c14`, `#0f172a`), Cyan accents (`#06b6d4`), Amber warning (`#f59e0b`), Red critical risk (`#ef4444`)
- **Charting:** Apache ECharts (`echarts`, `echarts-for-react`) for GPU-accelerated interactive visualizations
- **Geospatial Maps:** MapLibre GL JS for interactive vector tiles and coordinate clusters
- **Data Fetching:** TanStack React Query V5 with caching and background revalidation
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI 0.115+ (Asynchronous ASGI runtime)
- **Data Science:** Pandas 2.2+, NumPy 2.0+, SciPy 1.14+, Scikit-learn
- **Database & ORM:** SQLAlchemy 2.0+ with connection pooling, Alembic migrations
- **Databases Supported:** Remote Neon PostgreSQL 18.6 (Primary) + SQLite dual fallback
- **Authentication:** OAuth2 password flow with pure `bcrypt` hashing and PyJWT tokens (`HS256`)
- **Reporting:** ReportLab (vector PDF briefs) and OpenPyXL (multi-tab formatted spreadsheets)
- **Live Updates:** Server-Sent Events (SSE) streaming live platform telemetry

---

## 4. Key Functional Modules

| Module | Route | Capabilities |
| :--- | :--- | :--- |
| **Landing & Brand Portal** | `/` | Platform value proposition, architecture overview, dataset health indicator, and navigation entry points. |
| **Executive Overview** | `/overview` | Dynamic KPI cards (Accidents, Fatalities, Injuries, Fatality Rate %, Casualty Rate per Crash), YoY trends, regional density rankings, and auto-generated analytical findings. |
| **Accident Analysis** | `/accidents` | Searchable, paginated record explorer (25-100 rows/page) with severity badges, casualty tallies, weather/road filters, and record inspection drawer. |
| **Geographical Intelligence** | `/geography` | Interactive MapLibre GL map, state/district casualty distribution charts, and composite Risk Priority Index ($RPI$) rankings. |
| **Trend Analytics** | `/trends` | Longitudinal annual trends, monthly seasonality decomposition, day-of-week distributions, and 24-hour diurnal heatmaps. |
| **Severity Analysis** | `/severity` | Severity pyramid (*Fatal*, *Grievous Injury*, *Minor Injury*, *Property Damage Only*), casualty share breakdowns, and vehicle vulnerability proportions. |
| **Risk & Predictive Intelligence** | `/intelligence` | Multi-dimensional Pearson correlation matrix, Tukey IQR and Z-score anomaly detectors, and Ordinary Least Squares (OLS) trend projection with 95% confidence intervals. |
| **Data Management** | `/data-management` | Universal CSV/Excel drag-and-drop file ingestion, 4D quality scorecard (Completeness, Uniqueness, Validity, Consistency), and cleaning audit logs. |
| **Executive Reports** | `/reports` | One-click downloadable printable PDF briefs and multi-tab Excel workbooks. |
| **System Diagnostics** | `/system` | Database connection latency monitor, disk storage, audit event log table, and live SSE event stream. |
| **Authentication** | `/login` | Secure JWT credentials login granting administrative upload and data cleaning privileges. |

---

## 5. Getting Started & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20 or Node 24 supported)
- Git

### Quick Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/your-org/traffic-trend.git
cd traffic-trend
```

#### 2. Configure Backend Virtual Environment
```bash
# Create and activate Python virtual environment
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### 3. Environment Variables
Create `.env` in the root directory (or use `.env.example`):
```ini
PROJECT_NAME="TRAFFIC TREND"
SECRET_KEY="traffic-trend-super-secret-production-key-2026"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL="postgresql+psycopg2://<user>:<password>@<host>/neondb?sslmode=require"
ADMIN_DEFAULT_EMAIL="admin@traffictrend.io"
ADMIN_DEFAULT_PASSWORD="TrafficTrend2026!"
```

#### 4. Run Backend Server
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger API Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

#### 5. Install & Run Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:3001` in your browser.
*(Port 3001 is the default configured port to prevent collision with local processes).*

---

## 6. Default Credentials

The platform seeds an initial administrative user on first startup:
- **Email:** `admin@traffictrend.io`
- **Password:** `TrafficTrend2026!`

---

## 7. Automated Testing & Verification

The platform includes comprehensive test suites across both backend APIs and frontend static pages:

### Run Backend API Suite (Pytest)
```bash
pytest backend/tests/test_api.py -v
```
*Result: 13/13 passing against live PostgreSQL database in ~48s.*

### Run Core Analytical Suite
```bash
pytest tests/ -v
```
*Result: 19/19 passing in ~3.2s.*

### Run Frontend Production Build Check
```bash
cd frontend
npm run build
```
*Result: 14/14 static pages generated with zero errors.*

---

## 8. Docker Deployment

To launch the complete containerized stack using Docker Compose:
```bash
docker-compose up --build
```
This orchestrates:
- **Frontend Container:** Next.js on port 3000
- **Backend Container:** FastAPI on port 8000
- **Database Container:** PostgreSQL 16 on port 5432
- **Cache / Worker Container:** Redis 7 on port 6379

---

## 9. Academic & Presentation Highlights

- **Anti-Hallucination Assurance:** 100% of analytical metrics, KPIs, and forecasts are computed directly from database rows using Python data science algorithms. Zero fabricated stats.
- **Casualty vs Crash Integrity:** Strict mathematical and visual separation between collision incident totals and human casualties (fatalities and injuries).
- **Dual Database Architecture:** Zero-configuration local SQLite fallback ensures offline presentation resilience even in venues without internet connectivity.
- **Publication Exports:** ReportLab generates vectorized PDF briefs suitable for stakeholder submission; OpenPyXL exports multi-tab formatted workbooks with column autofit and styling.

---

## 10. License & Citation

Developed for academic and professional road safety intelligence.  
For methodology citations, refer to [ANALYTICAL_METHODOLOGY.md](docs/ANALYTICAL_METHODOLOGY.md) and [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).
