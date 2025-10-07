from fastapi import APIRouter, Depends, HTTPException
import httpx
from fastapi.responses import RedirectResponse

from app.services.google_services.google_auth_service import GoogleAuthService
from app.services.user_services.handler import UserService
from app.services.auth_services import create_access_token, get_fernet
from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient

from app.core.config import settings

# The address of our frontend application
FRONTEND_URL = settings.FRONTEND_URL

# Google Pub/Sub Topic Configuration
PROJECT_ID = "emailreader-472512"
TOPIC_ID = "gmail-inbox-changes"
TOPIC_NAME = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"

router = APIRouter()

@router.get("/auth/test")
async def auth_test():
    return {"message": "Auth router is working!"}


@router.get("/auth/google", tags=["Authentication"]) # Changed from POST to GET
async def auth_google(code: str, user_service: UserService = Depends()):
    """
    Handles the Google Sign-In callback, creates the user, and sets up the Gmail watch.
    """
    try:
        google_user_data = await GoogleAuthService.exchange_code_for_tokens(code)
    except httpx.HTTPStatusError as e:
        response_json = e.response.json()
        error_detail = response_json.get("error_description", str(e))
        return RedirectResponse(url=f"{FRONTEND_URL}?error={error_detail}")
    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=An-unexpected-error-occurred")

    email = google_user_data.get("email")
    name = google_user_data.get("name")
    refresh_token = google_user_data.get("refresh_token")

    if not email:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Could-not-retrieve-email-from-Google")

    user = await user_service.get_user_by_email(email)
    is_new_user = not user

    if is_new_user:
        user = await user_service.create_user(email=email, name=name)

    if refresh_token:
        fernet = get_fernet()
        encrypted_refresh_token = fernet.encrypt(refresh_token.encode()).decode()
        user_service.collection.update_one(
            {"_id": user._id},
            {"$set": {"encrypted_google_refresh_token": encrypted_refresh_token}}
        )
        
        # If this is a new user, automatically set up the watch for them.
        if is_new_user:
            try:
                print(f"New user {email} signed up. Setting up Gmail watch...")
                auth_handler = GoogleAuthHandler()
                # We use the encrypted refresh token to get credentials for the watch call
                credentials = auth_handler.get_credentials_from_refresh_token(encrypted_refresh_token)
                gmail_client = GmailClient(credentials)
                gmail_client.watch(topic_name=TOPIC_NAME)
                print("Gmail watch setup successful.")
            except Exception as e:
                print(f"ERROR: Failed to automatically set up Gmail watch for user {email}: {e}")
                # We don't block the login if this fails, but we should log it.
                # Redirect with an error to inform the user.
                return RedirectResponse(url=f"{FRONTEND_URL}?error=Login-succeeded-but-failed-to-setup-email-notifications")

    # Create a JWT access token for our API
    access_token = create_access_token(data={"sub": user.email})

    # Redirect the user back to the frontend, passing the token as a query parameter
    return RedirectResponse(url=f"{FRONTEND_URL}?token={access_token}")
