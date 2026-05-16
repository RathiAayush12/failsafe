# FailSafe — Early Student Failure Detection

An explainable AI system for faculty to identify at-risk students early
and generate personalised intervention plans.

---

## Tech Stack

**ML:** Python, XGBoost, SHAP, scikit-learn, Pandas, Matplotlib  
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT  
**Frontend:** React + Vite, Recharts  
**Deploy:** Docker, Docker Compose

---

## Project Structure

```
failsafe/
├── ml_pipeline/
│   ├── preprocess.py        # Data cleaning + feature engineering
│   ├── train.py             # XGBoost training + evaluation
│   ├── explain.py           # SHAP explainability
│   └── interventions.py     # Intervention plan generator
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── app/
│   │   ├── api/             # Route handlers
│   │   ├── models/          # SQLAlchemy models + DB session
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Auth + ML inference
│   ├── tests/               # pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Complete React application
│   │   ├── services/api.js  # API client
│   │   └── hooks/useAuth.jsx
│   ├── package.json
│   └── vite.config.js
├── data/                    # Gitignored — holds CSVs + model files
└── docker-compose.yml
```

---

## Setup

### 1. Download Dataset

Download `student-mat.csv` from:  
https://www.kaggle.com/datasets/uciml/student-alcohol-consumption

Place it at: `data/student-mat.csv`

### 2. Train the Model

```bash
cd failsafe
pip install -r backend/requirements.txt

python ml_pipeline/preprocess.py
python ml_pipeline/train.py
```

This generates:
- `data/processed/` — feature splits, scaler, encoders
- `data/model/model.pkl` — trained XGBoost model
- `data/model/feature_cols.pkl` — feature column list

### 3. Run with Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- API Docs: http://localhost:8000/docs

### 4. Run Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Set env vars
export DATABASE_URL="postgresql://failsafe:failsafe123@localhost:5432/failsafe_db"
export SECRET_KEY="your-secret-key"

uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 5. Create First User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@failsafe.edu",
    "password": "admin123",
    "full_name": "Admin Faculty",
    "role": "hod"
  }'
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/auth/me` | Current user |
| POST | `/api/predict/` | Predict from JSON |
| POST | `/api/predict/upload-csv` | Predict from CSV |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/students` | Student risk list |
| GET | `/api/dashboard/student/{id}` | Student detail |
| GET | `/api/interventions/` | List interventions |
| PATCH | `/api/interventions/{id}` | Update status/notes |

Full interactive docs: http://localhost:8000/docs

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `SECRET_KEY` | dev key | JWT signing key |
| `MODEL_PATH` | `data/model/model.pkl` | XGBoost model path |
| `FEATURES_PATH` | `data/model/feature_cols.pkl` | Feature columns |
| `SCALER_PATH` | `data/processed/scaler.pkl` | Scaler |
| `ENCODERS_PATH` | `data/processed/encoders.pkl` | Label encoders |
