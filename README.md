# Backtesting Financial System

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

### 1. Clone the Repository

```bash
git clone https://github.com/ntwari-bruce/Backtesting-Module.git
cd Backtesting-Module
## 2. Local Development
Build and Run Docker Containers:
bash
Copy code
docker-compose up --build
Apply Database Migrations:
bash
Copy code
docker-compose exec web python manage.py migrate
Access the Application: Open your browser and go to http://localhost:8080.
