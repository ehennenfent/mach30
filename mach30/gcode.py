import typing as t
from typing import SupportsFloat as maybe_float
from typing import get_args

from .models import (
    CircularMotionDirection,
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


def _kwargs_to_codes(**kwargs: maybe_float | None) -> t.List[Code]:
    assert all(key.upper() in get_args(CodeType) for key in kwargs.keys()), f"Invalid code type in {kwargs.keys()}"
    # mypy isn't quite smart enough to understand that the assert above guarantees that the keys are valid
    return [Code(code_type=key.upper(), code_number=float(value)) for key, value in kwargs.items() if value is not None]  # type: ignore


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

    @property
    def docs(self) -> str:
        return (
            f"https://www.haascnc.com/service/codes-settings.type=gcode.machine=mill.value=G{self.code_number:02}.html"
        )


class Dwell(Code):
    code_number: int = 4

    def __init__(self, p: maybe_float, is_millis: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if is_millis:
            self.sub_codes.append(
                Code(code_type="P", code_number=int(float(p)))
            )  # double cast needed to make mypy happy
        else:
            self.sub_codes.append(Code(code_type="P", code_number=float(p)))


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
        codes = _kwargs_to_codes(x=x, y=y, z=z, a=a, b=b, c=c)
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
        codes = _kwargs_to_codes(x=x, y=y, z=z, a=a, b=b, c=c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class CircularMove(ModalCode):

    group: GGroups = GGroups.MOTION

    def __init__(
        self,
        direction: CircularMotionDirection,
        feedrate: maybe_float,
        i: maybe_float | None = None,
        j: maybe_float | None = None,
        k: maybe_float | None = None,
        r: maybe_float | None = None,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            enter_code=GCode(code_number=direction.value, sub_codes=[Code(code_type="F", code_number=float(feedrate))]),
            *args,
            **kwargs,
        )
        self.enter_code.sub_codes.extend(_kwargs_to_codes(i=i, j=j, k=k, r=r, x=x, y=y, z=z, a=a))


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
        codes = _kwargs_to_codes(x=x, y=y, z=z, a=a, b=b, c=c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)

    def goto_initial_z(self) -> None:
        self.builder.add(GCode(code_number=98, comment="return to initial point"))

    def goto_r_plane(self) -> None:
        self.builder.add(GCode(code_number=99, comment="return to R plane"))


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


class PeckDrillCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = GCode(code_number=83, comment="begin peck drilling cycle")

    def __init__(
        self,
        f: maybe_float,
        z: maybe_float,
        r: maybe_float | None = None,
        p: maybe_float | None = None,
        i: maybe_float | None = None,
        j: maybe_float | None = None,
        k: maybe_float | None = None,
        q: maybe_float | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.extend(
            _kwargs_to_codes(
                f=f,
                z=z,
                r=r,
                p=p,
                i=i,
                j=j,
                k=k,
                q=q,
            )
        )


class TapCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = GCode(code_number=84, comment="begin tapping cycle")

    def __init__(
        self,
        f: maybe_float,
        z: maybe_float,
        r: maybe_float | None = None,
        j: maybe_float | None = None,
        q: maybe_float | None = None,
        s: maybe_float | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.extend(
            _kwargs_to_codes(
                f=f,
                z=z,
                r=r,
                j=j,
                q=q,
                s=s,
            )
        )


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
            enter_code=GCode(code_number=direction.value, sub_codes=[Code(code_type="H", code_number=h)]),
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
