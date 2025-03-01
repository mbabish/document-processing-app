# Document Processing Application

A simple document processing application with a Flask backend and React frontend, all containerized using Docker.

## Project Structure

```
document-processing-app/
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── api/
│       ├── __init__.py
│       └── routes.py
└── frontend/
    ├── package.json
    ├── public/
    │   ├── index.html
    │   └── favicon.ico
    └── src/
        ├── App.js
        ├── index.js
        ├── components/
        │   ├── Dashboard.js
        │   └── ReportList.js
        └── types/
            └── report.types.ts
```

## Prerequisites

- Docker and Docker Compose installed on your machine

## Setup and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/document-processing-app.git
   cd document-processing-app
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose -f docker/docker-compose.yml up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Backend API Endpoints

- `GET /api/reports` - Get all document reports
- `GET /api/reports/<schema_id>` - Get reports for a specific schema
- `GET /` - Health check endpoint

## Development

### Backend

The backend is a Flask application with the following structure:
- `app.py` - Main application entry point
- `api/routes.py` - API route definitions
- `requirements.txt` - Python dependencies

To add new API endpoints, edit the `api/routes.py` file.

### Frontend

The frontend is a React application with the following key components:
- `Dashboard.js` - Main dashboard view with statistics and charts
- `ReportList.js` - Document listing with filtering capabilities

To modify the frontend:
1. Update components in the `frontend/src/components` directory
2. Type definitions are in `frontend/src/types/report.types.ts`

## Additional Notes

- The application uses mock data for demonstration purposes
- For production, you would need to add proper error handling, authentication, and data validation
