from .gcode import (
    CannedCycle,
    SetCutterCompensation,
    SetMotionPlane,
    SetPositionMode,
    SetToolLengthCompensation,
    SetUnits,
)
from .mcode import ToolChange
from .models import (
    MotionPlane,
    PositionMode,
    ProgramBuilder,
    ToolLengthCompensation,
    Units,
)


def standard_preamble(builder: ProgramBuilder) -> None:
    builder.add(CannedCycle.cancel)
    builder.add(SetCutterCompensation.cancel)
    builder.add(SetToolLengthCompensation.cancel)

    builder.add(SetUnits(builder=builder, units=Units.INCHES).enter_code)
    builder.add(SetMotionPlane(builder=builder, motion_plane=MotionPlane.XY).enter_code)
    builder.add(SetPositionMode(builder=builder, position_mode=PositionMode.ABSOLUTE).enter_code)


def use_tool(
    builder: ProgramBuilder, tool_number: int, direction: ToolLengthCompensation = ToolLengthCompensation.ADD
) -> SetToolLengthCompensation:
    builder.add(ToolChange(tool_number=tool_number))
    return SetToolLengthCompensation(builder=builder, direction=direction, h=7)
