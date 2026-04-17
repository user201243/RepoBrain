from app.services.auth_service import AuthService


router = {"prefix": "/auth"}


async def login_with_google() -> dict[str, object]:
    service = AuthService()
    return await service.start_google_login()


async def auth_callback(code: str) -> dict[str, object]:
    service = AuthService()
    return await service.handle_google_callback(code)
