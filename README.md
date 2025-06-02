# File Sharing Web Application

A modern file sharing web application built with React.js frontend and Python backend.

## Features

- User Authentication (Signup/Login)
- File Upload and Download
- File Sharing with Other Users
- File Management (Delete, Rename)
- User Dashboard

## Project Structure

```
file-sharing-app/
├── frontend/          # React.js frontend
├── backend/           # Python backend
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Technologies Used

- Frontend:
  - React.js
  - Material-UI
  - Axios
  - React Router

- Backend:
  - Python
  - Flask
  - SQLite
  - Flask-SQLAlchemy
  - Flask-CORS
  - Flask-JWT-Extended

## License

MIT 