# Study Track - Intelligent Student Analytics Platform

Study Track is a comprehensive web application designed to track student study habits, analyze performance, and provide personalized recommendations. It combines a robust FastAPI backend with a modern Next.js frontend, leveraging data science techniques (K-Means Clustering) to categorize students and offer tailored insights.

## Problem Statement
Students often struggle to track their study habits effectively. They may spend hours studying but achieve low retention due to distractions or inefficient methods. Without data-driven feedback, it is difficult for them to identify areas for improvement.

**Study Track** solves this by:
1.  **Tracking** detailed study sessions (hours, methods, distractions).
2.  **Analyzing** performance patterns using AI.
3.  **Categorizing** students to identify those who need intervention.
4.  **Recommending** specific, actionable strategies to improve grades.

## algorithmic Logic & Clustering

The project uses a **hybrid approach** combining Unsupervised Learning (K-Means) and Rule-Based logic.

### 1. K-Means Clustering
We use the **K-Means algorithm** to segment students into distinct groups based on their study behavior.
*   **Number of Clusters (K)**: 3
*   **Features Used**:
    *   Study Hours
    *   Distraction Time
    *   Quiz Score
    *   Efficiency (Study Hour / Distraction)
    *   Quiz per Hour
*   **Cluster Labels**:
    1.  **High Achiever**: High study hours, high scores, low distraction.
    2.  **Balanced**: Consistent effort and scores.
    3.  **Needs Focus**: High distraction or low scores.

### 2. Rule-Based Recommendation Engine
While clustering provides the high-level profile, our recommendation engine uses specific **If-Else rules** to give granular advice:
*   **If Distraction > 30 mins**: Suggests "Pomodoro Technique" or silencing phone.
*   **If Study Time < 2 hours**: Suggests gradually increasing daily study time.
*   **If Quiz Score < 60%**: Suggests revising basics and practicing easier questions first.

## Features

### For Students
*   **Personalized Dashboard**: View your study progress, quiz scores, and efficiency metrics.
*   **Smart Recommendations**: Get actionable advice based on your learning style and recent performance.
*   **Secure Access**: One-Time Password (OTP) based login and signup system.

### For Administrators
*   **Analytics Dashboard**: Visual overview of global student performance, subject distribution, and quiz trends.
*   **Clustering Insights**: Group students into categories (e.g., "High Efficiency," "Needs Focus") using machine learning to identify at-risk students.
*   **Data Management**: View and manage student records and study logs.

## Tech Stack

### Frontend
*   **Framework**: [Next.js](https://nextjs.org/) (React)
*   **Styling**: Tailwind CSS
*   **Charting**: Chart.js / Recharts

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy
*   **Data Science**: Scikit-learn (for Clustering), Pandas

## Project Structure

```bash
Study_track/
├── backend/            # FastAPI application logic
│   ├── app/            # Main app package (models, schemas, api, auth)
│   ├── seed_data.py    # Script to populate DB with CSV data
│   ├── create_admin.py # Script to create admin credentials
│   └── requirements.txt
├── frontend/           # Next.js web application
│   ├── src/            # React components and pages
│   └── package.json
├── data/               # Dataset files (students.csv, study_logs.csv)
├── .env                # Environment variables configuration
└── README.md           # Project documentation
```

## Prerequisites

Ensure you have the following installed:
*   **Python 3.9+**
*   **Node.js 18+** & **npm**
*   **PostgreSQL** (Running locally)

## Getting Started

### 1. Environment Setup
Create a `.env` file in the root `Study_track` directory with your database and email credentials. You can use the `env.example` as a template if available, or follow this format:

```ini
# .env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/study_reco_db

# Email Configuration (for OTPs)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_FROM="Study Insights <your-email@gmail.com>"
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Database Initialization
Run the application for the first time or use the seed script to create tables and load data.

```bash
# Load initial data from ../data/students.csv and ../data/study_logs.csv
python seed_data.py

# (Optional) Create an admin user
python create_admin.py
```

#### Run the Server
Start the FastAPI development server.
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Docs are available at `http://localhost:8000/docs`.

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory.

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The application will be running at `http://localhost:3000`.

## Usage

1.  **Student Login**: Go to `http://localhost:3000`. Sign up or login with your email. You will receive an OTP for verification.
2.  **Admin Login**: Navigate to the login page and select "Admin". Use the credentials created via `create_admin.py` (or verify in DB).
3.  **Run Analysis**: In the Admin Dashboard, click "Run Clustering" to categorize students and update the global analytics charts.
