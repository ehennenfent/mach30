from enum import Enum


class ToolNoseRadiusCompensationDirection(Enum):
    LEFT = 41
    RIGHT = 42


class FeedRateMode(Enum):
    PER_MINUTE = 98
    PER_REVOLUTION = 99
