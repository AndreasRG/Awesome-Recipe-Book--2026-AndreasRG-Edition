def require_login(request):
    """Check if user is logged in. Return None if logged in, else True if not."""
    user_id = request.cookies.get("user_id")
    if not user_id:
        # User is NOT logged in
        return True
    # User IS logged in
    return None
