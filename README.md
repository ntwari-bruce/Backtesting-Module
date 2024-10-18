# Backtesting Module

## Overview

This project is a Django-based financial system that integrates with Alpha Vantage API to fetch stock price data, applies a backtesting strategy using historical data, and provides machine learning-powered stock price predictions. The project is deployed on Google Cloud Run using PostgreSQL as the database and includes a CI/CD pipeline with GitHub Actions for automated deployment.

## Features

- **Fetch Stock Data**: Retrieve daily stock prices from Alpha Vantage API and store them in a PostgreSQL database.
- **Backtesting Strategy**: Perform backtests based on moving averages for trading simulation.
- **Machine Learning Predictions**: Predict future stock prices using a pre-trained ML model.
- **Generate Reports**: Visualize stock prices and key metrics like ROI and max drawdown, with PDF export capability.
- **CI/CD Pipeline**: Automate deployment using GitHub Actions and Google Cloud Build.

## Prerequisites

- **Docker**: Install Docker for containerization.
- **Google Cloud SDK**: Required for deploying the application to Google Cloud.
- **Alpha Vantage API Key**: Sign up [here](https://www.alphavantage.co/support/#api-key) to get your API key.

## Setup Instructions

###Local Development
1. Clone the repository:
   ```bash
git clone https://github.com/ntwari-bruce/Backtesting-Module.git
cd Backtesting-Module

2. Build and Run Docker Containers: Make sure Docker is installed. Run the following command to build and start the containers:
   ```bash
docker-compose up --build

3. Run Database Migrations: Inside the Docker container, apply the migrations to create the necessary database tables:
   ```bash
docker-compose exec web python manage.py migrate

4. Access the Application: Open your browser and go to http://localhost:8080. Available API endpoints:
-**Fetch stock data:**- [http://localhost:8080/fetch-stock/<symbol>/]
-**Run backtest:**- [http://localhost:8080/backtest/?symbol=<symbol>&initial_investment=<amount>]
-**Generate report:**- [http://localhost:8080/generate-report/<symbol>/]

5. Running Tests
To run the test suite, use the following command:

   ```bash
Copy code
docker-compose exec web python manage.py test
Environment Variables

##Local Environment (.env)
For local development, you can configure the following environment variables in a .env file:

   ```bash
SECRET_KEY="your_secret_key"
DEBUG=True
ALLOWED_HOSTS="0.0.0.0,localhost,127.0.0.1"
# Database settings for PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=nkiramacumu8@
DB_PORT=5432

##Cloud Environment (env.yaml)
For cloud deployment, configure your environment variables in env.yaml:

```yaml
Copy code
SECRET_KEY: "your_secret_key"
DB_NAME: "postgres"
DB_USER: "postgres"
DB_PASSWORD: "nkiramacumu8@@"
DB_HOST: "/cloudsql/financial-439004:us-central1:financial-db-instance"
ALLOWED_HOSTS: "0.0.0.0,localhost,127.0.0.1,financial-system-785091501212.us-central1.run.app"
SQL_INSTANCE_CONNECTION_NAME: "financial-439004:us-central1:financial-db-instance"

##Cloud Deployment (Google Cloud Run)

1. Build Docker Image:
```bash
Copy code
docker build -t gcr.io/financial-439004/financial_system:latest .
2. Push Docker Image to Google Container Registry:
```bash
Copy code
docker push gcr.io/financial-439004/financial_system:latest

3. Submit Build to Google Cloud:
```bash
Copy code
gcloud builds submit --config=cloudbuild.yaml

4.Deploy to Google Cloud Run:
```bash
Copy code
gcloud run deploy financial-system \
   --image gcr.io/financial-439004/financial_system:latest \
   --platform managed \
   --region us-central1 \
   --allow-unauthenticated \
   --add-cloudsql-instances=financial-439004:us-central1:financial-db-instance \
   --env-vars-file=env.yaml


#API Endpoints

1. Fetch Stock Data:
```http
Copy code
GET /fetch-stock/<symbol>/
Example: [https://financial-system-785091501212.us-central1.run.app/fetch-stock/IBM]

2. Run Backtest:
```http
Copy code
GET /backtest/?symbol=<symbol>&initial_investment=<amount>
Example: [https://financial-system-785091501212.us-central1.run.app/backtest/?symbol=IBM&initial_investment=1000]
Generate Report:
http
Copy code
GET /generate-report/<symbol>/?pdf
Example: [https://financial-system-785091501212.us-central1.run.app/generate-report/IBM/?pdf]

#Technologies Used

-**Backend: Django**
-**Database: PostgreSQL (Cloud SQL)**
-**Machine Learning: Pre-trained model using scikit-learn**
-**Deployment: Google Cloud Run, Docker**
-**CI/CD: GitHub Actions, Google Cloud Build*
