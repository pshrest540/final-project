# Deployment Guide

This project deploys as three pieces:

1. Supabase PostgreSQL for auth users, saved vehicles, and prediction history.
2. FastAPI backend for `/health`, `/brands`, `/predict`, `/auth`, and `/vehicles`.
3. Streamlit frontend for the MIA UI.

The simplest setup is Supabase plus two Render web services from this repo.

Useful official references:

- Supabase connection strings: https://supabase.com/docs/reference/postgres/connection-strings
- Render Blueprints: https://render.com/docs/blueprint-spec
- Render FastAPI deployment: https://render.com/docs/deploy-fastapi

## 1. Prepare Supabase

1. Create a Supabase project.
2. In Supabase, open **Connect** and copy a PostgreSQL connection string.
3. Prefer the **Session pooler** connection string for hosted app servers if direct IPv6 connectivity is not available.
4. Replace `[YOUR-PASSWORD]` in the string with the database password.
5. Optional but recommended: open the Supabase SQL editor and run `supabase/schema.sql`.

The FastAPI app also calls `Base.metadata.create_all()` on startup, so it can create missing tables if the database user has permission.

## 2. Commit Runtime Artifacts

The deployed API needs these files at runtime:

- `models/drivetrain_model.joblib`
- `models/electrical_model.joblib`
- `models/engine_model.joblib`
- `data/processed/brand_model_reliability.csv`

If you want `/retrain` to work in production, also commit:

- `data/processed/drivetrain_physics.csv`
- `data/processed/electrical_physics.csv`
- `data/processed/engine_physics.csv`

The `.gitignore` now allows `models/*.joblib` and `data/processed/*.csv` to be committed while keeping raw data ignored.

## 3. Deploy On Render

1. Push this repo to GitHub.
2. In Render, create a new **Blueprint** from the repo. Render will read `render.yaml`.
3. When prompted for `finalproject-api` environment variables, set:
   - `DATABASE_URL`: your Supabase PostgreSQL URL.
   - `JWT_SECRET_KEY`: Render can generate this from `render.yaml`.
4. Let the API deploy, then open:
   - `https://YOUR-API-SERVICE.onrender.com/health`
   - `https://YOUR-API-SERVICE.onrender.com/docs`
5. Set the `finalproject-streamlit` service environment variable:
   - `API_BASE=https://YOUR-API-SERVICE.onrender.com`
6. Redeploy the Streamlit service.

## 4. Smoke Test

After both services are live:

1. Open the Streamlit URL.
2. Register a new account.
3. Add a vehicle.
4. Run an analysis.
5. Open vehicle details and confirm the prediction history appears.

If the API fails while loading model files, check the deploy logs for a scikit-learn model persistence warning or missing artifact path. The current deployment pin uses `scikit-learn==1.6.1`, matching the version recorded in the existing joblib files.
