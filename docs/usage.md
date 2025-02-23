
---

### 5. `docs/usage.md`

```markdown
# Usage Guide

## Overview
This guide explains how to use the real-time OPCUA dashboard project, including interacting with the frontend, configuring the system, and monitoring real-time data. It is intended for both end-users and developers.

## Accessing the Frontend
1. Ensure the backend (FastAPI) and frontend are running (see `docs/setup.md`).
2. Open a web browser and navigate to `http://localhost:3000` (or the configured frontend URL).
3. You’ll see the main dashboard with real-time data and forms for configuration.

## Using the Dashboard
- **Dashboard View**:
  - The dashboard displays real-time data from the Raspberry Pi OPCUA server.
  - Updates are streamed via WebSocket, ensuring the data refreshes automatically.
  - Use the navigation or tabs to switch between data views or settings.

- **Interacting with Data**:
  - Click on data points or variables to view detailed information.
  - Use the refresh button (if available) to manually update the dashboard.

## Configuring Namespaces and Variables
1. Navigate to the "Settings" or "Configuration" page in the frontend.
2. Use the forms to add or edit namespaces and variables:
   - Enter a namespace (e.g., "namespace1").
   - Add variables with names and initial values (e.g., {"name": "variable1", "value": "initial_value"}).
3. Submit the form to send a POST request to the FastAPI backend.
4. The backend updates the Raspberry Pi OPCUA server via OPCUA write operations.
5. Verify the changes in the dashboard or via the GET /config API endpoint.

## Monitoring Real-Time Data
- The dashboard automatically updates with real-time data from the Raspberry Pi.
- To troubleshoot or debug, check the logs in `logs/backend.log` and `logs/opcua_server.log`.
- Use the WebSocket connection (ws://localhost:8000/ws) to monitor data updates programmatically.

## API Usage (For Developers)
- Refer to `docs/api.md` for a complete list of API endpoints.
- Use tools like Postman or curl to test endpoints:
  - Example GET request for data:
    ```bash
    curl http://localhost:8000/data