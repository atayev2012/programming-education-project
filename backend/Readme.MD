# Backend for Programming Education Project

This repository contains the backend implementation of a web service designed to help users learn programming languages through gamification elements. The backend is built to handle user data, manage progress tracking, and provide APIs for the frontend.

## Features

- **User Management**: Registration, authentication, and profile management.
- **Gamification**: Tracks user progress, awards points, badges, and achievements.
- **Programming Challenges**: Provides coding exercises and validates user submissions.
- **Leaderboard**: Displays rankings based on user performance.
- **API Integration**: RESTful APIs for seamless communication with the frontend.

## Technologies Used

- **Programming Language**: [Python](https://www.python.org/)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Authentication**: [OAuth2](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) with JWT for secure user sessions
- **Testing**: [Pytest](https://docs.pytest.org/) for unit and integration tests

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/atayev2012/programming-education-project.git
    cd programming-education-project/backend
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory and configure the following:
    ```
    PORT=8000
    DATABASE_URL=postgresql://user:password@localhost/dbname
    JWT_SECRET=your-secret-key
    ```

5. Apply database migrations:
    ```bash
    alembic upgrade head
    ```

6. Start the server:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

| Method | Endpoint           | Description                     |
|--------|--------------------|---------------------------------|
| POST   | `/api/auth/signup` | Register a new user             |
| POST   | `/api/auth/login`  | Authenticate a user             |
| GET    | `/api/users`       | Fetch user profile              |
| POST   | `/api/challenges`  | Submit a programming challenge  |
| GET    | `/api/leaderboard` | Retrieve leaderboard rankings   |
