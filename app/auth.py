def require_login(request):
    """Return None when authenticated, True when not.

    This helper is used for simple page gating where a truthy value
    indicates the user should be redirected or shown a login prompt.
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        # User is NOT logged in
        return True
    # User IS logged in
    return None
