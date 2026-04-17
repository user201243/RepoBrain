from src.services.auth_service import login_with_google

def login_route():
    return login_with_google()
