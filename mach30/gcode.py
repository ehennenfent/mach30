import typing as t
from typing import SupportsFloat as maybe_float

from .models import (
    Code,
    CodeType,
    CutterCompensationDirection,
    GGroups,
    ModalCode,
    MotionPlane,
    PositionMode,
    ToolLengthCompensation,
    Units,
    WorkOffset,
)


def _six_axes_to_codes(
    x: maybe_float | None = None,
    y: maybe_float | None = None,
    z: maybe_float | None = None,
    a: maybe_float | None = None,
    b: maybe_float | None = None,
    c: maybe_float | None = None,
) -> t.List[Code]:
    codes = []
    if x is not None:
        codes.append(Code(code_type="X", code_number=float(x)))
    if y is not None:
        codes.append(Code(code_type="Y", code_number=float(y)))
    if z is not None:
        codes.append(Code(code_type="Z", code_number=float(z)))
    if a is not None:
        codes.append(Code(code_type="A", code_number=float(a)))
    if b is not None:
        codes.append(Code(code_type="B", code_number=float(b)))
    if c is not None:
        codes.append(Code(code_type="C", code_number=float(c)))
    return codes


def combine_motion_codes(codes: t.List[Code]) -> Code | None:
    match len(codes):
        case 0:
            return None
        case 1:
            return codes[0]
        case _:
            base = codes.pop(0)
            base.sub_codes.extend(codes)
            return base


class GCode(Code):
    code_type: CodeType = "G"


class RapidMove(ModalCode):
    enter_code: GCode = GCode(code_number=0)
    group: GGroups = GGroups.MOTION

    def move(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
    ) -> None:
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class LinearMove(ModalCode):
    enter_code: GCode = GCode(code_number=1)
    group: GGroups = GGroups.MOTION

    def __init__(self, feedrate: maybe_float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.append(Code(code_type="F", code_number=float(feedrate)))

    def move(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
    ) -> None:
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class CannedCycle(ModalCode):
    group: GGroups = GGroups.CANNED_CYCLE
    cancel: t.ClassVar[GCode] = GCode(code_number=80, comment="cancel canned cycle")
    exit_code: GCode = cancel

    def move(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
    ) -> None:
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class DrillCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = GCode(code_number=81, comment="begin drilling cycle")

    def __init__(self, f: maybe_float, z: maybe_float, r: maybe_float | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.append(Code(code_type="F", code_number=float(f)))
        self.enter_code.sub_codes.append(Code(code_type="Z", code_number=float(z)))
        if r is not None:
            self.enter_code.sub_codes.append(Code(code_type="R", code_number=float(r)))


class SpotDrillCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = GCode(code_number=82, comment="begin spot drilling cycle")

    def __init__(
        self,
        f: maybe_float,
        z: maybe_float,
        r: maybe_float | None = None,
        p: maybe_float | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.append(Code(code_type="F", code_number=float(f)))
        self.enter_code.sub_codes.append(Code(code_type="Z", code_number=float(z)))
        if r is not None:
            self.enter_code.sub_codes.append(Code(code_type="R", code_number=float(r)))
        if p is not None:
            self.enter_code.sub_codes.append(Code(code_type="P", code_number=float(p)))


class SetCutterCompensation(ModalCode):
    group: GGroups = GGroups.CUTTER_COMPENSATION
    cancel: t.ClassVar[GCode] = GCode(code_number=40, comment="cancel cutter compensation")
    exit_code: GCode = cancel

    def __init__(self, direction: CutterCompensationDirection, d: maybe_float, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=direction.value, sub_codes=[Code(code_type="D", code_number=float(d))]),
            *args,
            **kwargs,
        )


class SetToolLengthCompensation(ModalCode):
    group: GGroups = GGroups.TOOL_LENGTH_OFFSET
    cancel: t.ClassVar[GCode] = GCode(code_number=49, comment="cancel tool length compensation")
    exit_code: GCode = cancel

    def __init__(self, direction: ToolLengthCompensation, h: int, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=direction.value, sub_codes=[Code(code_type="H", code_number=float(h))]),
            *args,
            **kwargs,
        )


class SetUnits(ModalCode):
    group: GGroups = GGroups.UNITS

    def __init__(self, units: Units, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=units.value, comment=f"use {units.name.lower()}"), *args, **kwargs
        )


class SetMotionPlane(ModalCode):
    group: GGroups = GGroups.PLANE_SELECTION

    def __init__(self, motion_plane: MotionPlane, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=motion_plane.value, comment=f"{motion_plane.name} plane"), *args, **kwargs
        )


class SetPositionMode(ModalCode):
    group: GGroups = GGroups.DISTANCE_MODE

    def __init__(self, position_mode: PositionMode, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=position_mode.value, comment=f"{position_mode.name.lower()} positioning"),
            *args,
            **kwargs,
        )


class SetWorkOffset(ModalCode):
    group: GGroups = GGroups.COORDINATE_SYSTEM

    def __init__(self, work_offset: WorkOffset, *args, **kwargs):
        super().__init__(
            enter_code=GCode(code_number=work_offset.value, comment=f"use work offset {work_offset.name.lower()}"),
            *args,
            **kwargs,
        )
