
---

### 2. `docs/architecture.md`

```markdown
# Project Architecture

## Overview
This project is a distributed system for real-time industrial data monitoring and management. It consists of three main components: a web-based frontend, a FastAPI backend, and a Raspberry Pi acting as an OPCUA server. The architecture is designed for scalability, reliability, and ease of maintenance.

## Components

### 1. Frontend with Forms and Dashboard
- **Technology**: JavaScript (e.g., React or Vue.js) with HTML/CSS.
- **Purpose**: Provides a user interface for interacting with the system, including forms for configuration (e.g., adding namespaces and variables) and a dashboard for real-time data visualization.
- **Communication**:
  - Uses HTTP requests (GET, POST, EDIT, DELETE) to interact with the FastAPI backend.
  - Utilizes WebSocket connections for real-time data updates from the backend.

### 2. FastAPI Backend
- **Technology**: Python with FastAPI.
- **Purpose**: Acts as an intermediary between the frontend and the Raspberry Pi OPCUA server, handling API requests, WebSocket connections, and OPCUA communication.
- **Communication**:
  - Receives HTTP requests from the frontend and translates them into OPCUA operations for the Raspberry Pi.
  - Sends real-time data updates to the frontend via WebSocket.
  - Communicates with the Raspberry Pi using the OPCUA protocol for read/write operations and subscriptions.

### 3. Raspberry Pi as OPCUA Server
- **Technology**: Python with an OPCUA library (e.g., `opcua` or `asyncua`).
- **Purpose**: Runs on a Raspberry Pi to serve as an OPCUA server, managing real-time industrial data, namespaces, and variables.
- **Communication**:
  - Handles OPCUA read/write operations and subscriptions initiated by FastAPI.
  - Provides real-time data updates to FastAPI via OPCUA subscriptions.

## Data Flow
- **Configuration**:
  - Users input namespace and variable configurations via frontend forms.
  - The frontend sends HTTP POST requests to FastAPI, which translates them into OPCUA write operations to the Raspberry Pi.
- **Data Retrieval**:
  - The frontend sends HTTP GET requests to FastAPI, which queries the Raspberry Pi via OPCUA read operations.
  - FastAPI returns the data to the frontend, which displays it on the dashboard.
- **Real-Time Updates**:
  - The Raspberry Pi pushes updates to FastAPI via OPCUA subscriptions.
  - FastAPI forwards these updates to the frontend via WebSocket, ensuring the dashboard reflects real-time changes.

## Diagram
Refer to the flowchart image or recreate it using the description provided in the project documentation:
- [Frontend with Forms and Dashboard] <--> [FastAPI] <--> [Raspberry Pi as OPCUA server]
- Labels on arrows:
  - Frontend ↔ FastAPI: "HTTP requests/responses (GET, POST, EDIT, DELETE), WebSocket for real-time updates"
  - FastAPI ↔ Raspberry Pi: "OPCUA read/write operations, subscriptions for updates"

## Scalability and Performance
- The architecture supports horizontal scaling by adding more Raspberry Pi instances or FastAPI servers behind a load balancer.
- Caching and asynchronous processing in FastAPI optimize performance for real-time data handling.
- Error handling, logging, and monitoring are integrated to ensure reliability.

## Future Enhancements
- Add authentication and authorization for secure access.
- Implement caching for frequently accessed data.
- Expand support for additional industrial protocols or devices.