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

## Local Development
1. Clone the repository:

   ```bash
         git clone https://github.com/ntwari-bruce/Backtesting-Module.git

3. Build and Run Docker Containers: Make sure Docker is installed. Run the following command to build and start the containers:

   ```bash
         docker-compose up --build

4. Run Database Migrations: Inside the Docker container, apply the migrations to create the necessary database tables:

   ```bash
         docker-compose exec web python manage.py migrate

6. Access the Application: Open your browser and go to http://localhost:8080. Available API endpoints:
   -**Fetch stock data:**- [http://localhost:8080/fetch-stock/<symbol>/]
   -**Run backtest:**- [http://localhost:8080/backtest/?symbol=<symbol>&initial_investment=<amount>]
   -**Generate report:**- [http://localhost:8080/generate-report/<symbol>/]

7. Running Tests
 To run the test suite, use the following command:

         ```bash
         docker-compose exec web python manage.py test
         Environment Variables

## Local Environment (.env)
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

         ```bash
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
      docker build -t gcr.io/financial-439004/financial_system:latest .
      2. Push Docker Image to Google Container Registry:
      ```bash
      Copy code
      docker push gcr.io/financial-439004/financial_system:latest

3. Submit Build to Google Cloud:

      ```bash
      gcloud builds submit --config=cloudbuild.yaml

5. Deploy to Google Cloud Run:

   ```bash
   gcloud run deploy financial-system \
      --image gcr.io/financial-439004/financial_system:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --add-cloudsql-instances=financial-439004:us-central1:financial-db-instance \
      --env-vars-file=env.yaml


#API Endpoints

1. Fetch Stock Data:

   ```
      Copy code
      GET /fetch-stock/<symbol>/
      Example: [https://financial-system-785091501212.us-central1.run.app/fetch-stock/IBM]

3. Run Backtest:

      ```
      GET /backtest/?symbol=<symbol>&initial_investment=<amount>
      Example: [https://financial-system-785091501212.us-central1.run.app/backtest/?symbol=IBM&initial_investment=1000]

   
Generate Report:
      
      ```
      Copy code
      GET /generate-report/<symbol>/?pdf
      Example: [https://financial-system-785091501212.us-central1.run.app/generate-report/IBM/?pdf]

      
#CI/CD Pipeline with GitHub Actions

This project includes a CI/CD pipeline setup using GitHub Actions to automate the build, push, and deployment process to Google Cloud Run. The workflow triggers on every push to the main branch, building the Docker container, pushing it to Google Container Registry (GCR), and deploying it to Google Cloud Run.

##Steps in the GitHub Actions Workflow
-**Checkout the code:** The workflow starts by checking out the latest code from the repository.
-**Build Docker services using docker-compose:** The workflow runs docker-compose to build the necessary services defined in docker-compose.yml.
-**Tag and push Docker image:** After building the Docker image, it tags the image and pushes it to Google Container Registry (GCR).
-**Submit build to Google Cloud:** The workflow submits the build to Google Cloud Build for further processing.
-**Deploy to Google Cloud Run:** Finally, the workflow deploys the application to Google Cloud Run, making it available to the public.

##GitHub Actions Configuration
To automate this process, we use a GitHub Actions workflow defined in [.github/workflows/deploy.yml]. Below is an outline of the key parts of the workflow:

      ```
      Copy code
      name: CI/CD Pipeline
      
      on:
        push:
          branches:
            - main
      
      jobs:
        deploy:
          runs-on: ubuntu-latest
      
          steps:
          - name: Checkout code
            uses: actions/checkout@v2
      
          - name: Set up Docker Buildx
            uses: docker/setup-buildx-action@v1
      
          - name: Authenticate to Google Cloud
            run: echo "${{ secrets.GCP_SA_KEY }}" | docker login -u _json_key --password-stdin https://gcr.io
      
          - name: Build Docker services using docker-compose
            run: |
              docker-compose -f docker-compose.yml build
      
          - name: Tag and Push Docker image
            run: |
              docker tag your-service-name gcr.io/financial-439004/financial_system:latest
              docker push gcr.io/financial-439004/financial_system:latest
      
          - name: Submit build to Google Cloud
            run: |
              gcloud builds submit --config=cloudbuild.yaml
      
          - name: Deploy to Cloud Run
            run: |
              gcloud run deploy financial-system \
              --image gcr.io/financial-439004/financial_system:latest \
              --platform managed \
              --region us-central1 \
              --allow-unauthenticated \
              --add-cloudsql-instances=financial-439004:us-central1:financial-db-instance \
              --env-vars-file=env.yaml
      
##Setting Up GitHub Secrets
To secure sensitive information like Google Cloud authentication, you need to set up GitHub Secrets:

1. **GCP_SA_KEY**: Add your Google Cloud service account key in JSON format. This is required for authentication with Google Cloud to push images to the Google Container Registry (GCR) and deploy to Google Cloud Run.
To add a secret in GitHub:

1. Go to your GitHub repository.
2. Click on **Settings** > **Secrets** and **variables** > **Actions**.
3. Click New repository secret and add the name **GCP_SA_KEY**.
4. Paste the JSON content of your service account key into the value field.
   
## Triggering the Workflow
The workflow is automatically triggered on every push to the **main** branch. You can manually trigger it or make any changes to the code, push to **main**, and the workflow will execute automatically.

## Continuous Deployment Flow
1. Make changes to your code.
2. Commit and push to the **main** branch.
3. GitHub Actions will build the Docker image, push it to GCR, and deploy it to Google Cloud Run.
4. The new version of the application will be live on Google Cloud Run.

##Technologies Used

-**Backend: Django**
-**Database: PostgreSQL (Cloud SQL)**
-**Machine Learning: Pre-trained model using scikit-learn**
-**Deployment: Google Cloud Run, Docker**
-**CI/CD: GitHub Actions, Google Cloud Build*
