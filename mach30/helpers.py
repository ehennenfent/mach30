import typing as t

from .gcode import (
    CannedCycle,
    SetCutterCompensation,
    SetMotionPlane,
    SetPositionMode,
    SetToolLengthCompensation,
    SetUnits,
)
from .models import Code, MotionPlane, PositionMode, Units

StandardPreamble: t.List[Code] = [
    CannedCycle.exit_code,
    SetCutterCompensation.exit_code,
    SetToolLengthCompensation.exit_code,
    SetUnits(Units.INCHES).enter_code,
    SetMotionPlane(MotionPlane.XY).enter_code,
    SetPositionMode(PositionMode.ABSOLUTE).enter_code,
]
