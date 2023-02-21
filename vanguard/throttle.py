from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class OncePerMinuteAnonThrottle(AnonRateThrottle):
    rate = "1/minute"


class TwicePerMinuteAnonThrottle(AnonRateThrottle):
    rate = "2/minute"


class FivePerMinuteAnonThrottle(AnonRateThrottle):
    rate = "5/minute"


class TenPerMinuteAnonThrottle(AnonRateThrottle):
    rate = "10/minute"


class FifteenPerMinuteAnonThrottle(AnonRateThrottle):
    rate = "15/minute"


class TwentyPerMinuteAnonThrottle(AnonRateThrottle):
    rate = "20/minute"


class TwentyFivePerMinuteAnonThrottle(AnonRateThrottle):
    rate = "25/minute"


class ThirtyPerMinuteAnonThrottle(AnonRateThrottle):
    rate = "30/minute"


class MaxAnonThrottle(AnonRateThrottle):
    rate = "100/minute"


class DevTestingAnonThrottle(AnonRateThrottle):
    rate = "100/minute"
