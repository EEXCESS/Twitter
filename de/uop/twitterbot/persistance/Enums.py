from enum import Enum


class UserTweetStatus(Enum):
    new = "new"
    requested = "requested"
    done = "done"
    no_recommendation = "noRecommendation"


class UserStatus(Enum):
    normal = "normal"


class RecommendationStatus(Enum):
    new = "new"
    done = "done"
    duplicate = "duplicate"
    unable = "unable"