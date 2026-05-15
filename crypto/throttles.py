from rest_framework.throttling import UserRateThrottle


class AdminRateThrottle(UserRateThrottle):
    rate = "1000/minute"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_staff:
            return self.cache_format % {
                "scope": self.scope,
                "ident": self.get_ident(request),
            }
        return None  # не применяется к не-админам
