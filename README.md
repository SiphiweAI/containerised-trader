# Cloud Trader

[![CI](https://github.com/siphiweai/containerised-trader/actions/workflows/ci.yml/badge.svg)](https://github.com/siphiweai/containerised-trader/actions/workflows/ci.yml)
[![Fly.io Deploy](https://img.shields.io/badge/Deployed-Fly.io-blue)](https://fly.io/)
[![GitHub release](https://img.shields.io/github/v/release/siphiweai/containerised-trader?include_prereleases)](https://github.com/siphiweai/containerised-trader/releases)
[![Docker](https://img.shields.io/badge/Image-GitHub%20Packages-green)](https://github.com/siphiweai?tab=packages)

A containerized trading automation environment that integrates **n8n**, **PostgreSQL**, and **Python microservices** on **Fly.io** for automated trade processing and analytics.

---

## Features

- **Flask API** endpoint (`/webhook`) to receive trade alerts  
- **Celery** background task queue (with Redis broker)  
- **PostgreSQL** persistence for trade logs  
- **Dynamic candle fetching** via Twelve Data API  
- **Docker + Supervisor** setup for running Flask, Celery, and Cron together  
- Deployable on [Fly.io](https://fly.io)

---

## Project Structure
cloud_trader/
├── Dockerfile
├── fly.toml
├── supervisord.conf
├── requirements.txt
├── trade_track/
│ ├── app.py
│ ├── helper_funcs.py
│ ├── load.py
│ ├── log_config.py
│ ├── tasks.py
│ ├── .env
│ └── init.py
└── tests/
└── init.py


---

## Environment Variables

Create a `.env` file inside `trade_track/`:

```bash
# Flask
FLASK_ENV=production

# Database
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=5432

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0

# Twelve Data API
API_KEY=your-twelvedata-api-key
