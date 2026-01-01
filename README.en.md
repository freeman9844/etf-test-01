# Global ETF Portfolio Tracker & Dividend Calendar

[🇰🇷 한국어](README.md) | [🇺🇸 English](README.en.md)

[![Cloud Run Deployment](https://img.shields.io/badge/Deployed-Cloud%20Run-blue?logo=google-cloud&logoColor=white)](https://etf-tracker-904902969656.asia-northeast3.run.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)

A dashboard application to manage global ETF portfolios in real-time and predict future dividends.

## 🚀 Key Features

- **Real-time Portfolio Dashboard**: Performance tracking using `yfinance` API.
- **Dividend Calendar**: 12-month dividend projections visualized as grid cards.
- **Portfolio Management**: Easy CRUD for ETFs with category (Sector) classification.
- **Google Sheets Integration**: CSV Export/Import support compatible with Google Sheets templates.
- **Responsive Dark Mode UI**: Modern interface with sleek card-based design.

## 🛠 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python Web Framework)
- **Data Engine**: [Pandas](https://pandas.pydata.org/), [yfinance](https://github.com/ranaroussi/yfinance)
- **Database**: SQLite (Local storage)
- **Visualization**: Plotly Express
- **Deployment**: Google Cloud Run (Dockerized)

## 📦 Installation & Local Setup

### 1. Prerequisites
- Python 3.10 or higher.

### 2. Virtual Env & Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install required packages
pip install -r etf_tracker/requirements.txt
```

### 3. Run the App
```bash
streamlit run etf_tracker/app.py
```

## ☁️ Google Cloud Platform (GCP) Deployment Guide

This project is optimized for deployment to Google Cloud Run using Docker.

### 1. Pre-deployment Configuration
- Create a project on the [GCP Console](https://console.cloud.google.com/) and link a billing account.
- Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) on your local machine and authenticate.
```bash
gcloud auth login
gcloud config set project [YOUR_PROJECT_ID]
```

### 2. Deploy to Cloud Run
Run the following command from the project root. This will automatically build the container and deploy the service.

```bash
gcloud run deploy etf-tracker \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated
```
- `--source .`: Builds using source in the current directory (referencing `Dockerfile`).
- `--region`: `asia-northeast3` (Seoul) is recommended.
- `--allow-unauthenticated`: Makes the service publicly accessible.

### 3. Important Note (Data Persistence)
> [!WARNING]
> Cloud Run is a **Stateless** environment. This version uses local SQLite (`portfolio.db`), which means data will be reset whenever the service restarts or scales.
> - **Solution**: For production use, modify `src/database.py` to connect to a persistent database like **Cloud SQL (PostgreSQL)** or **Supabase**.

## 📄 License
This project is for educational and personal use only.
