from enum import Enum

from .lathe.enums import FeedRateMode as FeedRateMode
from .lathe.enums import (
    ToolNoseRadiusCompensationDirection as ToolNoseRadiusCompensationDirection,
)
from .mill.enums import CutterCompensationDirection as CutterCompensationDirection
from .mill.enums import ToolLengthCompensation as ToolLengthCompensation


class MotionPlane(Enum):
    XY = 17
    XZ = 18
    YZ = 19


class SpindleDirection(Enum):
    FORWARD = 3
    REVERSE = 4
    OFF = 5


class CircularMotionDirection(Enum):
    CLOCKWISE = 2
    COUNTERCLOCKWISE = 3


class Units(Enum):
    INCHES = 20
    MILLIMETERS = 21


class PositionMode(Enum):
    ABSOLUTE = 90
    INCREMENTAL = 91


class WorkOffset(Enum):
    ONE = 54
    TWO = 55
    THREE = 56
    FOUR = 57
    FIVE = 58
    SIX = 59


class GGroups(Enum):
    # nonmodal, obvs
    NONMODAL = 0
    # Real modes
    MOTION = 1
    PLANE_SELECTION = 2
    DISTANCE_MODE = 3
    FEEDRATE_MODE = 5
    UNITS = 6
    CUTTER_COMPENSATION = 7
    TOOL_LENGTH_OFFSET = 8
    CANNED_CYCLE = 9
    CANNED_CYCLE_RETURN_MODE = 10
    SCALING = 11
    COORDINATE_SYSTEM = 12
    EXACT_STOP = 15
    ROTATION = 16
    DYNAMIC_WORK_OFFSET = 23
