import typing as t
from typing import SupportsFloat as maybe_float

from .enums import (
    CircularMotionDirection,
    CutterCompensationDirection,
    MotionPlane,
    PositionMode,
    ToolLengthCompensation,
    Units,
    WorkOffset,
)
from .models import Code, CodeType, GCode, GGroups


class G00(GCode):
    code_number: int = 0
    group: GGroups = GGroups.MOTION
    description: str = "Rapid Move"
    args: t.List[CodeType] = ["X", "Y", "Z"]


Rapid = G00


class G01(GCode):
    code_number: int = 1
    group: GGroups = GGroups.MOTION
    description: str = "Linear Move"
    args: t.List[CodeType] = ["X", "Y", "Z", "F"]

    @classmethod
    def with_feedrate(cls, feedrate: float | int, *args, **kwargs) -> "G01":
        sub_codes = kwargs.get("sub_codes", [])
        sub_codes.append(Code(code_type="F", code_number=feedrate))
        return cls(sub_codes=sub_codes, *args, **kwargs)

    @property
    def feedrate(self) -> float | int | None:
        for code in self.sub_codes:
            if code.code_type == "F":
                return code.code_number
        return None


LinearFeed = G01


class G02(GCode):
    code_number: int = CircularMotionDirection.CLOCKWISE.value
    group: GGroups = GGroups.MOTION
    description: str = "Clockwise Circular Move"
    args: t.List[CodeType] = ["X", "Y", "Z", "I", "J", "K", "R"]

    @classmethod
    def with_feedrate(cls, feedrate: float | int, *args, **kwargs) -> "G02":
        sub_codes = kwargs.get("sub_codes", [])
        sub_codes.append(Code(code_type="F", code_number=feedrate))
        return cls(sub_codes=sub_codes, *args, **kwargs)

    @property
    def feedrate(self) -> float | int | None:
        for code in self.sub_codes:
            if code.code_type == "F":
                return code.code_number
        return None


CWFeed = G02


class G03(GCode):
    code_number: int = CircularMotionDirection.COUNTERCLOCKWISE.value
    group: GGroups = GGroups.MOTION
    description: str = "Counterclockwise Circular Move"
    args: t.List[CodeType] = ["X", "Y", "Z", "I", "J", "K", "R"]

    @classmethod
    def with_feedrate(cls, feedrate: float | int, *args, **kwargs) -> "G03":
        sub_codes = kwargs.get("sub_codes", [])
        sub_codes.append(Code(code_type="F", code_number=feedrate))
        return cls(sub_codes=sub_codes, *args, **kwargs)

    @property
    def feedrate(self) -> float | int | None:
        for code in self.sub_codes:
            if code.code_type == "F":
                return code.code_number
        return None


CCWFeed = G03


def CircularFeed(direction: CircularMotionDirection, feedrate: float | int) -> GCode:
    if direction == CircularMotionDirection.CLOCKWISE:
        return CWFeed.with_feedrate(feedrate=feedrate)
    return CCWFeed.with_feedrate(feedrate=feedrate)


class G04(GCode):
    code_number: int = 4
    group: GGroups = GGroups.NONMODAL
    description: str = "Dwell"
    args: t.List[CodeType] = ["P"]

    def __init__(self, p: maybe_float, is_millis: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if is_millis:
            self.sub_codes.append(
                Code(code_type="P", code_number=int(float(p)))
            )  # double cast needed to make mypy happy
        else:
            self.sub_codes.append(Code(code_type="P", code_number=float(p)))


Dwell = G04


class G17(GCode):
    code_number: int = MotionPlane.XY.value
    group: GGroups = GGroups.PLANE_SELECTION
    description: str = "XY Plane Selection"


UseXY = G17


class G20(GCode):
    code_number: int = Units.INCHES.value
    group: GGroups = GGroups.UNITS
    description: str = "Inches Units"


UseInches = G20


class G21(GCode):
    code_number: int = Units.MILLIMETERS.value
    group: GGroups = GGroups.UNITS
    description: str = "Millimeters Units"


UseMillimeters = G21


class G28(GCode):
    code_number: int = 28
    group: GGroups = GGroups.NONMODAL
    description: str = "Return to Home Position"


Home = G28


class G40(GCode):
    code_number: int = 40
    group: GGroups = GGroups.CUTTER_COMPENSATION
    description: str = "Cancel Cutter Compensation"


CancelCutterComp = G40


class G41(GCode):
    code_number: int = CutterCompensationDirection.LEFT.value
    group: GGroups = GGroups.CUTTER_COMPENSATION
    description: str = "Cutter Compensation Left"


CutterCompLeft = G41


class G42(GCode):
    code_number: int = CutterCompensationDirection.RIGHT.value
    group: GGroups = GGroups.CUTTER_COMPENSATION
    description: str = "Cutter Compensation Right"


CutterCompRight = G42


class G43(GCode):
    code_number: int = ToolLengthCompensation.ADD.value
    group: GGroups = GGroups.TOOL_LENGTH_OFFSET
    description: str = "Tool Length Compensation Add"


ToolLengthCompAdd = G43


class G44(GCode):
    code_number: int = ToolLengthCompensation.SUB.value
    group: GGroups = GGroups.TOOL_LENGTH_OFFSET
    description: str = "Tool Length Compensation Subtract"


ToolLengthCompSub = G44


class G49(GCode):
    code_number: int = 49
    group: GGroups = GGroups.TOOL_LENGTH_OFFSET
    description: str = "Cancel Tool Length Compensation"


CancelToolLengthComp = G49


class G53(GCode):
    code_number: int = 53
    group: GGroups = GGroups.NONMODAL
    description: str = "Use Machine Coordinate System"


UseMachineCoord = G53


class G54(GCode):
    code_number: int = WorkOffset.ONE.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 1"


WorkOffset1 = G54


class G55(GCode):
    code_number: int = WorkOffset.TWO.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 2"


WorkOffset2 = G55


class G56(GCode):
    code_number: int = WorkOffset.THREE.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 3"


WorkOffset3 = G56


class G57(GCode):
    code_number: int = WorkOffset.FOUR.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 4"


WorkOffset4 = G57


class G58(GCode):
    code_number: int = WorkOffset.FIVE.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 5"


WorkOffset5 = G58


class G59(GCode):
    code_number: int = WorkOffset.SIX.value
    group: GGroups = GGroups.COORDINATE_SYSTEM
    description: str = "Use Work Offset 6"


WorkOffset6 = G59


class G80(GCode):
    code_number: int = 80
    group: GGroups = GGroups.CANNED_CYCLE
    description: str = "Cancel Canned Cycle"


CancelCannedCycle = G80


class G81(GCode):
    code_number: int = 81
    group: GGroups = GGroups.CANNED_CYCLE
    description: str = "Drill Cycle"


DrillCycle = G81


class G82(GCode):
    code_number: int = 82
    group: GGroups = GGroups.CANNED_CYCLE
    description: str = "Spot Drill Cycle"


SpotDrillCycle = G82


class G83(GCode):
    code_number: int = 83
    group: GGroups = GGroups.CANNED_CYCLE
    description: str = "Peck Drill Cycle"


PeckDrillCycle = G83


class G84(GCode):
    code_number: int = 84
    group: GGroups = GGroups.CANNED_CYCLE
    description: str = "Tap Cycle"


TapCycle = G84


class G90(GCode):
    code_number: int = PositionMode.ABSOLUTE.value
    group: GGroups = GGroups.DISTANCE_MODE
    description: str = "Absolute Distance Mode"


AbsoluteDist = G90


class G91(GCode):
    code_number: int = PositionMode.INCREMENTAL.value
    group: GGroups = GGroups.DISTANCE_MODE
    description: str = "Incremental Distance Mode"


IncrementalDist = G91


class G98(GCode):
    code_number: int = 98
    group: GGroups = GGroups.CANNED_CYCLE_RETURN_MODE
    description: str = "Initial Point Return"


CannedCycleInitialPointReturn = G98


class G99(GCode):
    code_number: int = 99
    group: GGroups = GGroups.CANNED_CYCLE_RETURN_MODE
    description: str = "R Point Return"


CannedCycleRPointReturn = G99
