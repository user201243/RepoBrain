from app.services.retry_handler import enqueue_payment_retry


class AuthService:
    async def start_google_login(self) -> dict[str, str]:
        return {"provider": "google", "redirect": "https://accounts.google.com/o/oauth2/auth"}

    async def handle_google_callback(self, code: str) -> dict[str, object]:
        token = exchange_code_for_token(code)
        profile = fetch_google_profile(token)
        return {"provider": "google", "profile": profile}


def exchange_code_for_token(code: str) -> str:
    return f"token:{code}"


def fetch_google_profile(token: str) -> dict[str, str]:
    enqueue_payment_retry({"token": token, "retry_count": 0})
    return {"token": token, "email": "user@example.com"}
