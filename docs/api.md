# API Documentation

## Overview
This document describes the API endpoints provided by the FastAPI backend for interacting with the frontend and the Raspberry Pi OPCUA server. The API supports HTTP requests for configuration, data operations, and real-time updates via WebSocket.

## Base URL
- `http://localhost:8000` (default, configurable via environment variables)

## Authentication
- Currently, no authentication is required, but you can add token-based authentication (e.g., JWT) in the future. Refer to `backend/app/config.py` for configuration options.

## Endpoints

### 1. Data Operations
#### GET /data
- **Description**: Retrieve real-time data from the Raspberry Pi OPCUA server.
- **Response**: JSON object containing data values.
  ```json
  {
    "status": "success",
    "data": {
      "variable1": "value1",
      "variable2": "value2"
    }
  }