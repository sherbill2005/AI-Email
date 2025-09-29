# Multi-User Authentication & Authorization

## 1. Overview

This document outlines the implementation of a multi-user authentication and authorization system based on a JWT + Google OAuth2 architecture. The goal is to allow multiple users to sign up, connect their Gmail accounts, and have their own separate sets of rules and processed emails, ensuring strict data isolation between users.

## 2. Core Concepts

-   **Application-level Authentication (JWT):** The primary login mechanism will be **"Sign in with Google."** Upon successful authentication, the application will generate its own JWT-based access token. This token will be used to authenticate all subsequent API requests from the user.

-   **Service-level Authorization (OAuth2):** To access a user's Gmail data, the user must grant our application permission via the Google OAuth2 consent flow. We will securely store each user's **encrypted refresh token** to maintain this access without requiring the user to log in repeatedly.

-   **Multi-Tenant Data Architecture:** All user-specific data (rules, processed emails, user settings) will be partitioned by `user_id` in the database to ensure strict data isolation.

## 3. Authentication & Authorization Flow

1.  **User Login**: A user clicks "Sign in with Google" on the frontend.
2.  **Google OAuth Consent**: The user is redirected to Google, authenticates, and grants permission for the application to access their Gmail data.
3.  **Authorization Code**: Google redirects back to the frontend with a one-time `authorization_code`.
4.  **Backend Login Endpoint**: The frontend sends this `authorization_code` to a `POST /login/google` endpoint.
5.  **Token Exchange & User Provisioning**: The backend exchanges the code for a Google `id_token` and a `refresh_token`.
    -   It verifies the `id_token` to get the user's profile (email, name).
    -   It searches the database for a user with that email. If one doesn't exist, it creates a new user.
    -   The Google `refresh_token` is **encrypted** and stored securely in that user's document in the database.
6.  **Application JWT Issued**: The backend generates its own application-specific JWT (access token) and returns it to the frontend.
7.  **Authenticated Requests**: The frontend includes this JWT in the `Authorization` header for all future API calls to protected endpoints.

## 4. Real-time Processing Flow (Multi-User)

1.  **Pub/Sub Notification**: Google Pub/Sub sends a notification containing the `emailAddress` and `historyId` to the `/gmail-webhook` endpoint.
2.  **User Lookup**: The webhook looks up the user in the database using the `emailAddress`.
3.  **Gmail Client Instantiation**: It retrieves the user's encrypted Google `refresh_token`, decrypts it, and uses it to instantiate a temporary `GmailClient` for that specific user.
4.  **Fetch & Process**: The `GmailClient` fetches the new messages from the user's inbox.
5.  **Per-User Rules**: The orchestration service retrieves the filtering rules associated with that `user_id`.
6.  **Store Data**: The email is processed, and if it meets the criteria, the results are stored in the `processed_emails` collection with the corresponding `user_id`.

## 5. Data Model Changes

-   **`users` collection**:
    -   Add `encrypted_google_refresh_token: str` to store the user-specific token for accessing Gmail.
-   **`rules` collection**:
    -   Add a `user_id: ObjectId` field to each rule document to associate it with a user.
-   **`processed_emails` collection**:
    -   Add a `user_id: ObjectId` field to each document.

## 6. Implementation Steps

### Step 1: Update Dependencies
-   Add to `requirements`:
    -   `python-jose[cryptography]`: For application JWTs.
    -   `httpx`: For server-to-server Google API calls.
    -   `cryptography`: For encrypting and decrypting the Google refresh tokens.

### Step 2: Configure Settings (`app/core/config.py`)
-   Add:
    -   `GOOGLE_CLIENT_ID`
    -   `GOOGLE_CLIENT_SECRET`
    -   `JWT_SECRET_KEY`: A new, strong, random secret for signing application JWTs.
    -   `JWT_ALGORITHM`
    -   `ENCRYPTION_KEY`: A new, strong, random secret for encrypting refresh tokens.

### Step 3: Update Models & Schemas
-   `app/models/user_model.py`: Add `encrypted_google_refresh_token: str | None = None`.
-   `app/models/rules_model.py`: Add `user_id: str`.
-   `app/schemas/processed_email_schema.py`: Add `user_id: str`.
-   `app/schemas/auth_schema.py`: Create `Token` and `TokenData` schemas.

### Step 4: Create/Update Services
-   **`app/services/auth_service.py`** (New):
    -   Functions for creating and validating application JWTs.
    -   Functions for encrypting and decrypting Google refresh tokens.
    -   `get_current_user` dependency for protected routes.
-   **`app/services/google_auth_service.py`** (New):
    -   Logic to exchange the `authorization_code` for Google tokens and user info.
-   **`app/services/rules_services.py`**:
    -   Update all methods (`get_all_rules`, `create_rule`, etc.) to accept a `user_id` and operate only on that user's data.
-   **`app/services/orchestration_service.py`**:
    -   Update `process_incoming_email_notification` to handle the multi-user flow described above.

### Step 5: Create/Update API Routes
-   **`app/apis/v1/auth_routes.py`** (New):
    -   `POST /login/google`: Handles the login flow.
    -   `GET /users/me`: Returns details for the logged-in user.
-   **`app/apis/v1/rules_routes.py`**:
    -   Update all routes to use the `get_current_user` dependency and pass the `user_id` to the service layer.

### Step 6: Update Main Application (`main.py`)
-   Include the new router from `app/apis/v1/auth_routes.py`.