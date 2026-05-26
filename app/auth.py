from fastapi.responses import RedirectResponse


def require_login(request):
    """Redirect to login page if user is not authenticated."""
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/auth/login", status_code=302)
    return None
