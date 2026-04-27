# User Manual

## MIA Vehicle Health Predictor

MIA is a web application that predicts vehicle health scores for three major systems:

- Engine
- Drivetrain
- Electrical

The application lets a user create an account, add vehicles, enter driving conditions, run a wellness analysis, view maintenance recommendations, and review previous prediction history. The project is built with a Streamlit frontend, a FastAPI backend, machine learning models, and a Supabase PostgreSQL database.

This manual assumes the reader knows nothing about the project and needs to install, run, use, deploy, and maintain it.

## 1. Project Overview

### 1.1 Product Name

MIA Vehicle Health Predictor

### 1.2 Purpose

The purpose of MIA is to help vehicle owners estimate the condition of important vehicle components based on vehicle identity, mileage, driving habits, and pre-trained machine learning models. The system returns health scores from 5 to 100 and gives maintenance recommendations when component scores are low.

### 1.3 Main Features

- User registration and login
- Personal or business account types
- Vehicle dashboard
- Add vehicle by brand, model, year, mileage, and optional VIN
- Predict vehicle health using driving condition sliders
- View system scores and component scores
- View maintenance recommendations
- Save prediction history for each vehicle
- API health and database health checks
- Optional model retraining endpoint

### 1.4 Project Folder Structure

```text
finalproject/
  api/                 FastAPI backend
  app/                 Streamlit frontend
  data/processed/      Processed CSV data used by models and API
  models/              Trained joblib machine learning models
  src/                 Data generation and processing scripts
  train/               Model training script
  supabase/            PostgreSQL database schema
  DEPLOYMENT.md        Deployment instructions
  USER_MANUAL.md       This manual
  render.yaml          Render deployment blueprint
  requirements.txt     Python dependencies
```

## 2. Types of Users

### 2.1 Vehicle Owner

A vehicle owner uses the application to:

- Register or log in
- Add one or more personal vehicles
- Run a vehicle health analysis
- View recommendations for components that may need service
- Track prediction history over time

### 2.2 Business User

A business user, such as a small repair shop or fleet operator, can use the application to:

- Create a business account
- Track multiple vehicles
- Run analyses for different vehicles
- Review previous diagnostic results

### 2.3 Administrator or Developer

An administrator or developer maintains the technical side of the product:

- Configures Supabase
- Deploys the FastAPI API and Streamlit frontend
- Maintains environment variables
- Updates processed datasets
- Retrains machine learning models
- Troubleshoots deployment, database, or API problems

## 3. Dependencies

### 3.1 Operating Environment

The project can run on Windows, macOS, or Linux as long as Python and pip are installed. The project was developed in a Python environment and is intended to be deployed as web services.

Recommended environment:

- Python 3.11 for deployment
- pip package manager
- Git
- Internet connection for installing packages and connecting to Supabase
- Supabase PostgreSQL database
- Render account for deployment

No special hardware is required. A normal laptop or cloud web service instance is enough.

### 3.2 Software Dependencies

The Python dependencies are listed in `requirements.txt`.

Important packages include:

- `fastapi` for the backend API
- `uvicorn` for running the backend server
- `streamlit` for the frontend web interface
- `plotly` for result charts
- `requests` for frontend-to-backend API calls
- `pandas` and `numpy` for data processing
- `scikit-learn` for machine learning predictions
- `joblib` for loading trained model files
- `sqlalchemy` for database access
- `psycopg2-binary` for PostgreSQL connectivity
- `passlib` and `bcrypt` for password hashing
- `python-jose` for JWT authentication
- `python-dotenv` for local environment variables

### 3.3 Runtime Data and Model Files

The deployed backend requires these files:

```text
models/drivetrain_model.joblib
models/electrical_model.joblib
models/engine_model.joblib
data/processed/brand_model_reliability.csv
```

If model retraining is used, these training data files are also needed:

```text
data/processed/drivetrain_physics.csv
data/processed/electrical_physics.csv
data/processed/engine_physics.csv
```

### 3.4 Environment Variables

The backend and frontend require configuration through environment variables.

Backend variables:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET_KEY=a-long-random-secret-value
DB_CONNECT_TIMEOUT=10
CREATE_DB_TABLES_ON_STARTUP=false
LOAD_MODELS_ON_STARTUP=false
```

Frontend variable:

```text
API_BASE=https://YOUR-API-SERVICE.onrender.com
```

For local development, `API_BASE` can be:

```text
API_BASE=http://localhost:8000
```

## 4. Installation

### 4.1 Obtain the Project Code

The project code should be obtained from the project GitHub repository or from the submitted project folder named `finalproject`.

If using Git:

```bash
git clone YOUR_REPOSITORY_URL
cd finalproject
```

If using the submitted folder, open a terminal in the `finalproject` directory.

### 4.2 Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Configure Local Environment

Create a `.env` file in the project root.

Example:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
API_BASE=http://localhost:8000
DB_CONNECT_TIMEOUT=10
CREATE_DB_TABLES_ON_STARTUP=false
LOAD_MODELS_ON_STARTUP=false
```

Do not commit `.env` to GitHub because it contains private credentials.

## 5. Database Setup

### 5.1 Database System

The project uses Supabase PostgreSQL.

The database stores:

- Users
- Vehicles
- Driving habit records
- Maintenance logs
- Wellness prediction history

### 5.2 Create the Database

1. Create a Supabase project.
2. Open the Supabase SQL Editor.
3. Run the schema from `supabase/schema.sql`.
4. Copy the Supabase PostgreSQL connection string.
5. Set that connection string as `DATABASE_URL` in the backend environment.

Use the Supabase Session Pooler connection string if the normal direct connection does not work from Render.

### 5.3 Database Tables

The database contains these tables:

- `users`
- `vehicles`
- `vehicle_habits`
- `maintenance_logs`
- `wellness_predictions`

### 5.4 Database SQL

The schema is stored in `supabase/schema.sql` and `dbtable.sql`. The main SQL structure is:

```sql
do $$
begin
    create type account_type_enum as enum ('personal', 'business', 'admin');
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type service_category_enum as enum ('engine', 'drivetrain', 'electrical', 'routine');
exception
    when duplicate_object then null;
end $$;

create table if not exists users (
    user_id varchar(36) primary key,
    email varchar(255) unique not null,
    password_hash varchar(255) not null,
    account_type account_type_enum not null default 'personal',
    business_name varchar(255),
    full_name varchar(255),
    created_at timestamp with time zone default now()
);

create table if not exists vehicles (
    vehicle_id varchar(36) primary key,
    owner_id varchar(36) not null references users(user_id) on delete cascade,
    vin varchar(17),
    brand varchar(50) not null,
    model varchar(50) not null,
    year integer not null,
    current_mileage integer not null,
    added_on timestamp with time zone default now()
);

create table if not exists vehicle_habits (
    habit_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    rough_scale double precision default 0.0,
    torque_scale double precision default 0.0,
    stop_scale double precision default 0.0,
    temp_scale double precision default 0.0,
    habit_scale double precision default 0.0,
    idle_scale double precision default 0.0,
    last_updated timestamp with time zone default now()
);

create table if not exists maintenance_logs (
    log_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    service_category service_category_enum not null,
    component_replaced varchar(100) not null,
    mileage_at_service integer not null,
    service_date date not null,
    performed_by varchar(100),
    service_notes text
);

create table if not exists wellness_predictions (
    prediction_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    overall_score double precision not null,
    engine_score double precision not null,
    drivetrain_score double precision not null,
    electrical_score double precision not null,
    calculated_at timestamp with time zone default now()
);

create index if not exists idx_vehicles_owner_id on vehicles(owner_id);
create index if not exists idx_predictions_vehicle_id on wellness_predictions(vehicle_id);
create index if not exists idx_predictions_calculated_at on wellness_predictions(calculated_at desc);
```

## 6. Running the Project Locally

The project has two running services:

- FastAPI backend
- Streamlit frontend

### 6.1 Start the Backend API

From the project root:

```bash
uvicorn api.main:app --reload
```

The API should run at:

```text
http://localhost:8000
```

Test the API health endpoint:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "message": "Vehicle Maintenance API is running."
}
```

### 6.2 Start the Streamlit Frontend

In a second terminal:

```bash
streamlit run app/Vehicle_Input.py
```

The Streamlit application usually opens at:

```text
http://localhost:8501
```

### 6.3 API Documentation

FastAPI automatically provides API documentation at:

```text
http://localhost:8000/docs
```

This page can be used by developers to inspect and test API endpoints.

## 7. Deployment

### 7.1 Hosted Services

The recommended deployment uses:

- Supabase for PostgreSQL
- Render for the FastAPI backend
- Render for the Streamlit frontend

After deployment, the public URLs will usually look like:

```text
Backend API:
https://finalproject-api.onrender.com

Frontend App:
https://finalproject-streamlit.onrender.com
```

If Render changes the service names, use the actual `.onrender.com` URLs shown in the Render dashboard.

### 7.2 Deploy with Render Blueprint

This project includes `render.yaml`, which defines two services:

- `finalproject-api`
- `finalproject-streamlit`

Deployment steps:

1. Push the project to GitHub.
2. Open Render.
3. Create a new Blueprint from the GitHub repository.
4. Let Render detect `render.yaml`.
5. Set environment variables when prompted.
6. Deploy the API first.
7. Copy the API URL.
8. Set the frontend `API_BASE` environment variable to the API URL.
9. Redeploy the Streamlit service.

### 7.3 Required Render Environment Variables

For the API service:

```text
DATABASE_URL=your Supabase PostgreSQL connection string
JWT_SECRET_KEY=a long random value
DB_CONNECT_TIMEOUT=10
CREATE_DB_TABLES_ON_STARTUP=false
LOAD_MODELS_ON_STARTUP=false
```

For the Streamlit service:

```text
API_BASE=https://YOUR-API-SERVICE.onrender.com
```

Do not include `/health` or `/docs` in `API_BASE`.

Correct:

```text
API_BASE=https://finalproject-api.onrender.com
```

Incorrect:

```text
API_BASE=https://finalproject-api.onrender.com/health
```

## 8. Using the Application

### 8.1 Open the Frontend

Open the Streamlit frontend URL:

```text
https://finalproject-streamlit.onrender.com
```

If running locally, open:

```text
http://localhost:8501
```

### 8.2 Register a New Account

1. Open the app.
2. Click the register link.
3. Enter an email address.
4. Enter a password with at least 8 characters.
5. Confirm the password.
6. Select an account type:
   - Personal
   - Business
7. If Business is selected, enter a business name.
8. Click Create Account.

After registration, the application logs the user in and redirects to the dashboard.

### 8.3 Log In

1. Open the app.
2. Enter the registered email address.
3. Enter the password.
4. Click Login.

If the credentials are correct, the dashboard opens.

### 8.4 Dashboard

The dashboard shows:

- The logged-in user's email or name
- A list of saved vehicles
- An Add Vehicle button
- Analyze and Details buttons for each vehicle
- A Logout button

If no vehicles have been added, the dashboard shows an empty state.

### 8.5 Add a Vehicle

1. Click Add Vehicle.
2. Select the brand.
3. Select the model.
4. Enter the year.
5. Enter the current mileage.
6. Optionally enter the VIN.
7. Click Save Vehicle.

The vehicle is saved to the database and appears on the dashboard.

### 8.6 Run a Vehicle Health Analysis

1. From the dashboard, click Analyze for a vehicle.
2. Confirm or change the vehicle information.
3. Adjust the driving condition sliders:
   - Road Roughness
   - Towing / Heavy Load
   - Stop-and-Go Traffic
   - Extreme Temperatures
   - Driving Aggressiveness
   - Extended Idling
4. Click Analyze Vehicle Health.

The app sends the request to the FastAPI backend. The backend loads the trained models, runs predictions, saves the result if a vehicle ID is present, and returns the scores.

### 8.7 Results Page

The results page displays:

- Overall health score
- Engine system score
- Drivetrain system score
- Electrical system score
- Component-level scores
- Gauge charts
- Maintenance recommendations

Score meaning:

```text
65 to 100: Good
40 to 64: Monitor
5 to 39: Service Soon
```

### 8.8 Vehicle Details and Prediction History

From the dashboard:

1. Click Details for a saved vehicle.
2. View the vehicle profile.
3. Review previous wellness predictions.
4. Click Analyze to run a new analysis.

Prediction history is stored in the `wellness_predictions` table.

### 8.9 Log Out

Click Logout from the dashboard or analysis page. The app removes the session token and returns to the login flow.

## 9. Backend API Reference

The main API endpoints are:

```text
GET  /health
GET  /db/health
GET  /brands
POST /predict
POST /auth/register
POST /auth/login
GET  /auth/me
GET  /vehicles
POST /vehicles
GET  /vehicles/{vehicle_id}
GET  /vehicles/{vehicle_id}/predictions
POST /retrain
```

### 9.1 Health Check

```text
GET /health
```

Checks whether the API is running.

### 9.2 Database Health Check

```text
GET /db/health
```

Checks whether the API can connect to Supabase.

### 9.3 Brands

```text
GET /brands
```

Returns available brands and models from `brand_model_reliability.csv`.

### 9.4 Prediction

```text
POST /predict
```

Accepts vehicle identity, mileage, driving condition scales, and optional `vehicle_id`. Returns engine, drivetrain, electrical, and overall health scores.

### 9.5 Authentication

```text
POST /auth/register
POST /auth/login
GET /auth/me
```

These endpoints manage accounts and JWT login sessions.

### 9.6 Vehicles

```text
GET /vehicles
POST /vehicles
GET /vehicles/{vehicle_id}
GET /vehicles/{vehicle_id}/predictions
```

These endpoints manage saved vehicles and prediction history.

## 10. Administration and Maintenance

### 10.1 Routine Maintenance Tasks

An administrator should regularly:

- Confirm the API `/health` endpoint works
- Confirm the database `/db/health` endpoint works
- Check Render deployment logs after changes
- Confirm Supabase is active and not paused
- Back up database data if it becomes important for real users
- Keep `.env` secrets private
- Confirm `models/*.joblib` files are present before deployment
- Confirm `data/processed/brand_model_reliability.csv` is present

### 10.2 Updating Dependencies

Dependencies are controlled by `requirements.txt`.

If dependencies are changed:

1. Update `requirements.txt`.
2. Test locally.
3. Redeploy the API and frontend.
4. Confirm `/health`, `/brands`, login, add vehicle, and prediction all work.

Be careful when changing `scikit-learn`. The model files were saved with scikit-learn and may not load correctly with incompatible versions.

### 10.3 Retraining Models

The model training script is:

```text
train/train_models.py
```

To retrain locally:

```bash
python train/train_models.py
```

This reads:

```text
data/processed/drivetrain_physics.csv
data/processed/electrical_physics.csv
data/processed/engine_physics.csv
```

It writes:

```text
models/drivetrain_model.joblib
models/electrical_model.joblib
models/engine_model.joblib
```

After retraining:

1. Test predictions locally.
2. Commit updated model files if they are part of the deployment.
3. Redeploy the API.

### 10.4 Updating Brand and Model Data

The frontend brand/model dropdowns use:

```text
data/processed/brand_model_reliability.csv
```

If new brands or models are added:

1. Update the CSV.
2. Confirm `/brands` returns the new values.
3. Redeploy the API.
4. Refresh the frontend.

### 10.5 Updating NHTSA Complaint Data

NHTSA complaint score generation is handled by:

```text
src/nhtsa_complaints_dataset.py
src/nhtsa_config.py
```

To change which vehicles are included, edit:

```text
src/nhtsa_config.py
```

Then run:

```bash
python src/nhtsa_complaints_dataset.py
```

This produces processed complaint score files in:

```text
data/processed/
```

### 10.6 Moving to a New Host

To move the project to another hosting service:

1. Confirm the host supports Python web services.
2. Install dependencies from `requirements.txt`.
3. Set the same environment variables.
4. Start the API with:

```bash
uvicorn api.main:app --host 0.0.0.0 --port PORT_NUMBER
```

5. Start the Streamlit frontend with:

```bash
streamlit run app/Vehicle_Input.py --server.address 0.0.0.0 --server.port PORT_NUMBER --server.headless true
```

6. Set the frontend `API_BASE` value to the hosted API URL.
7. Confirm database access from the new host.

## 11. Troubleshooting

### 11.1 Render App Is Stuck Loading

Check the API first:

```text
https://YOUR-API-SERVICE.onrender.com/health
```

If `/health` does not load:

- Check Render logs for the API service.
- Confirm `DATABASE_URL` is set on the API service.
- Confirm `JWT_SECRET_KEY` is set.
- Confirm the service installed dependencies successfully.
- Confirm the required model and data files are committed.

If `/health` works but login or vehicle pages fail:

```text
https://YOUR-API-SERVICE.onrender.com/db/health
```

If `/db/health` fails:

- Use the Supabase Session Pooler connection string.
- Confirm the database password is correct.
- Confirm Supabase is not paused.
- Confirm `sslmode=require` is included or added automatically.

### 11.2 Frontend Cannot Reach API

In Render, open the Streamlit service and check:

```text
API_BASE=https://YOUR-API-SERVICE.onrender.com
```

Do not include a trailing endpoint such as `/health`.

### 11.3 Login or Register Fails

Possible causes:

- API service is down
- Supabase connection failed
- Database schema was not created
- `JWT_SECRET_KEY` is missing
- User email already exists

Check:

```text
/health
/db/health
```

### 11.4 Prediction Fails

Possible causes:

- Missing `.joblib` model files
- Missing `brand_model_reliability.csv`
- Incompatible scikit-learn version
- Invalid request data

Confirm these files exist:

```text
models/drivetrain_model.joblib
models/electrical_model.joblib
models/engine_model.joblib
data/processed/brand_model_reliability.csv
```

### 11.5 Brands Do Not Load

The `/brands` endpoint depends on:

```text
data/processed/brand_model_reliability.csv
```

If this file is missing, the frontend cannot populate the brand and model dropdowns.

## 12. Security Notes

- Passwords are hashed before storage.
- JWT tokens are used for authenticated API access.
- The `.env` file must not be committed.
- `JWT_SECRET_KEY` should be long and random in production.
- Database credentials should only be stored in hosting environment variables.
- Supabase database access should be limited to the application and trusted administrators.

## 13. Accessibility

The app is web-based and can be accessed through a normal browser. Streamlit provides standard form inputs such as text fields, select boxes, sliders, and buttons.

Current accessibility strengths:

- Browser-based interface
- Keyboard-accessible form controls
- Clear page separation for login, dashboard, vehicle entry, and results
- Large visual score displays

Current accessibility limitations:

- Some results rely on color differences.
- Some custom-styled text may be harder for screen readers to interpret.
- The dark visual theme should be tested for contrast on different displays.

Suggested accessibility improvements:

- Add more text labels for chart values.
- Avoid using color alone to communicate status.
- Test the app with screen readers.
- Add clearer error messages for failed API and database calls.

## 14. Suggested Future Enhancements

Possible enhancements include:

- Allow users to edit and delete vehicles.
- Add maintenance log entry screens.
- Add admin dashboard for user and database management.
- Add email reminders for low component scores.
- Add VIN decoding.
- Add more vehicle makes and models.
- Add charts showing score changes over time.
- Add downloadable PDF diagnostic reports.
- Improve accessibility and mobile layout.
- Add automated tests for API routes and prediction logic.

## 15. Quick Start Summary

For local use:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
streamlit run app/Vehicle_Input.py
```

For deployment:

1. Create Supabase project.
2. Run `supabase/schema.sql`.
3. Deploy with Render using `render.yaml`.
4. Set `DATABASE_URL` and `JWT_SECRET_KEY` on the API service.
5. Set `API_BASE` on the Streamlit service.
6. Test `/health`, `/db/health`, registration, vehicle creation, and prediction.

## 16. Important File Reference

```text
api/main.py                         FastAPI app setup
api/db/session.py                   Database connection
api/db/models.py                    SQLAlchemy database models
api/routers/auth.py                 Register/login routes
api/routers/vehicles.py             Vehicle and prediction history routes
api/routers/predict.py              Prediction route
api/services/predictor.py           Prediction logic
api/models/loader.py                Model loading
app/Vehicle_Input.py                Main Streamlit analysis page
app/pages/Login.py                  Login page
app/pages/Register.py               Register page
app/pages/Home.py                   Dashboard
app/pages/AddVehicle.py             Add vehicle page
app/pages/Results.py                Prediction results page
app/pages/VehicleDetail.py          Prediction history page
train/train_models.py               Model training script
src/nhtsa_complaints_dataset.py     NHTSA complaint dataset generator
supabase/schema.sql                 Supabase database schema
render.yaml                         Render deployment blueprint
requirements.txt                    Python dependencies
```
