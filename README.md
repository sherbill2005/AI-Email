# Project Overview
This project is an AI Email management system designed to streamline email processing and enhance user interaction through intelligent filtering and management.

# Features
## Core Functionality
- **Real-Time Email Processing:** Leveraging AI to filter and categorize emails effectively.
- **Gmail Integration:** Seamless connection with Gmail for user email management.

## Authentication
- **Multi-User Authentication:** Users can securely log in through Google OAuth2.

## Data Management
- **MongoDB Database:** Efficiently stores user emails and settings, supporting fast queries and scalability.

# Architecture
The system follows an MVC architecture:
- **Backend:** Built using FastAPI, providing robust and efficient API endpoints for communication.
- **Frontend:** Developed with React, ensuring a responsive and dynamic user interface.

# Quick Start Guide
1. Clone the repository.
2. Install the necessary dependencies in both the frontend and backend.
3. Set up your MongoDB and connect it to the backend.
4. Obtain and configure your Google OAuth2 credentials.
5. Start the FastAPI backend and React frontend.

# Technology Stack
- **Backend:** FastAPI
- **Frontend:** React
- **Database:** MongoDB
- **Real-Time Processing:** AI Filtering Algorithms
- **Authentication:** Google OAuth2

# API Endpoints
1. `POST /api/auth/login`: Authenticate user via Google OAuth2.
2. `GET /api/emails`: Retrieve user emails.
3. `POST /api/emails/filter`: Apply AI filtering to emails.

# Advanced Features
- **Weighted Scoring for Rule Prioritization:** Users can set priorities for rules based on their scores, enhancing the filtering process.
- **Gmail Push Notifications Integration:** Users are notified in real-time of incoming emails.

# Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)

This AI Email management system is designed to make your email handling smarter and more efficient, integrating cutting-edge technology with user-friendly interfaces.