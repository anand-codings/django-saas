"""Custom throttling classes with plan-tier awareness."""

from rest_framework.throttling import UserRateThrottle


class PlanBasedThrottle(UserRateThrottle):
    """Throttle based on the user's subscription plan.

    Looks up the user's active subscription and applies the plan's
    API rate limit. Falls back to a default rate.
    """

    scope = "plan_based"
    default_rate = "1000/hour"

    def get_rate(self):
        # In a full implementation, this would look up the user's plan
        # and return the plan's rate limit.
        return self.default_rate
