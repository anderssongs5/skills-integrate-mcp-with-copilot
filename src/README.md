# Mergington High School Activities API

A FastAPI application for viewing extracurricular activities and managing student registrations.

## Features

- View all available extracurricular activities
- View activity rosters without logging in
- Teacher login to register and unregister students
- Teacher credentials stored as password hashes in a local JSON file

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Provision a teacher account. From the `src` directory, run:

   ```
   python create_teacher.py
   ```

   This creates or updates `teachers.json`. The file is ignored by Git because it contains credential hashes. Do not commit it. Passwords must be at least 12 characters.

3. Run the application:

   ```
   uvicorn app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| GET    | `/auth/session`                                                   | Check whether the current browser has a teacher session              |
| POST   | `/auth/login`                                                     | Log in with a teacher username and password                          |
| POST   | `/auth/logout`                                                    | End the current teacher session                                      |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher registers a student for an activity                          |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher unregisters a student                                        |

Signup and unregister requests require a teacher session. The UI hides those controls from students, and the API independently enforces the same restriction. Teacher sessions use an HTTP-only cookie and expire after eight hours or when the server restarts. Activity rosters remain visible to unauthenticated visitors, including student email addresses.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activity data and teacher sessions are stored in memory, which means they reset when the server restarts. Teacher credentials are read from the local `teachers.json` file and are not committed to the repository.
