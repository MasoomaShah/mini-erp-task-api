
# Mini ERP Task API

A small REST API built with FastAPI, SQLite,
bearer token authentication and Docker.

## Architecture

Client / Postman
       |
       v
FastAPI Application
       |
       v
Bearer Token Authentication
       |
       v
SQLite Database
       |
       v
Docker Volume (Persistent Storage)

## Features

- GET: Retrieve tasks
- POST: Create tasks
- PATCH: Update tasks
- Bearer token authentication
- SQLite database persistence
- Docker containerization
- OpenAPI documentation

## Technologies

- Python
- FastAPI
- SQLite
- Docker
- Postman

## Run Locally

Install dependencies:

pip install -r requirements.txt

Set environment variables in PowerShell:

$env:API_TOKEN="your-secret-token"
$env:DB_PATH="data/tasks.db"

Start application:

python -m uvicorn main:app --reload

## Run with Docker

Build:

docker build -t mini-erp-task-api .

Run:

docker run -d --name mini-erp-api `
  -p 8000:8000 `
  -e API_TOKEN=your-secret-token `
  -e DB_PATH=/app/data/tasks.db `
  -v task_data:/app/data `
  mini-erp-task-api

## API Documentation

http://localhost:8000/docs

## Authentication

Protected endpoints require a bearer token.

Never commit actual API credentials.

## Database

SQLite stores task records.
A Docker named volume provides persistent storage.
