# DrugRecall Check API

Pharmacies, healthcare providers, and medtech apps need real-time access to FDA drug recalls, safety alerts, and enforcement reports, but the FDA's open data portal requires developers to navigate complex JSON dumps with no dedicated API key or rate limits suitable for production use. There is no simple, well-documented REST API that returns recall data by drug name, NDC code, manufacturer, or date range with proper pagination and webhook notifications when new recalls hit. Developers building pharmacy management software or patient safety apps hack together scrapers or batch downloads.

## Quick Start

```bash
pip install -r requirements.txt
API_KEY=your-secret-key uvicorn main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/recalls/search | Search drug recalls |
| POST | /v1/webhooks/recalls | Register a webhook for new recall notifications |

## Authentication
All endpoints (except `/health`) require an `x-api-key` header.

## Deployment
This API is ready for Railway deployment. Push to GitHub and connect.
