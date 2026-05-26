# metrics.py
# Application-level Prometheus counters for observability.
from prometheus_client import Counter

RECIPES_CREATED_TOTAL = Counter("recipes_created_total", "Number of recipes created")

RECIPE_VIEWS_TOTAL = Counter(
    "recipe_views_total", "Number of times a recipe was viewed"
)

USER_SIGNUPS_TOTAL = Counter("user_signups_total", "Number of users created")

LOGIN_ATTEMPTS_TOTAL = Counter("login_attempts_total", "Number of login attempts")
