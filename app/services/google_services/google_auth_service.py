import httpx
from urllib.parse import unquote
from google.oauth2 import id_token
from google.auth.transport.requests import Request

from app.core.config import settings


class GoogleAuthService:
    """
    Service for handling the OAuth2 code exchange with Google.
    """

    # --- NEW ---
    # This is the main method that orchestrates the token exchange.
    @staticmethod
    async def exchange_code_for_tokens(code: str) -> dict:
        """
        Exchanges an authorization code for Google access and refresh tokens.

        Args:
            code: The one-time authorization code from the frontend.

        Returns:
            A dictionary containing the user's profile and tokens.
        """
        async with httpx.AsyncClient() as client:
            # Decode the authorization code to handle URL-encoded characters like '%2F'
            decoded_code = unquote(code)

            # Step 1: Prepare the request to Google's token endpoint.
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": decoded_code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.PUBLIC_SERVER_URL}/apis/v1/auth/google",
                "grant_type": "authorization_code",
            }

            # --- NEW ---
            # Step 2: Make the server-to-server request to exchange the code.
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()  # Raise an exception if the request fails
            token_payload = response.json()

            # --- NEW ---
            # Step 3: Verify the ID token to get the user's profile information.
            id_info = id_token.verify_oauth2_token(
                token_payload["id_token"], Request(), settings.GOOGLE_CLIENT_ID
            )

            # --- NEW ---
            # Step 4: Return all the necessary information.
            return {
                "email": id_info.get("email"),
                "name": id_info.get("name"),
                "refresh_token": token_payload.get("refresh_token"),
            }
