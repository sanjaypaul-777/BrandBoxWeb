"""
apps/coach/context_processors.py — Template context for coach unread / desk flags.
"""

from .models import CoachProfile


def coach_flags(request):
    user = getattr(request, "user", None)
    return {
        "user_is_coach": CoachProfile.user_is_coach(user) if user else False,
    }
