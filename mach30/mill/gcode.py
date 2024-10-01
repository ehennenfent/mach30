import typing as t
from typing import SupportsFloat as maybe_float

from mach30.enums import CutterCompensationDirection, ToolLengthCompensation

from .gcode_basic import CancelCannedCycle as _CancelCannedCycle
from .gcode_basic import CancelCutterComp as _CancelCutterComp
from .gcode_basic import CancelToolLengthComp as _CancelToolLengthComp
from .gcode_basic import CannedCycleInitialPointReturn, CannedCycleRPointReturn
from .gcode_basic import DrillCycle as _DrillCycle
from .gcode_basic import PeckDrillCycle as _PeckDrillCycle
from .gcode_basic import SpotDrillCycle as _SpotDrillCycle
from .gcode_basic import TapCycle as _TapCycle
from .helpers import combine_codes, kwargs_to_codes
from .modal_code import ModalCode
from .models import Code, GCode, GGroups


class CannedCycle(ModalCode):
    group: GGroups = GGroups.CANNED_CYCLE
    cancel: t.ClassVar[GCode] = _CancelCannedCycle(comment="cancel canned cycle")
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
        codes = kwargs_to_codes(x=x, y=y, z=z, a=a, b=b, c=c)
        if maybe_code := combine_codes(codes):
            self.builder.add(maybe_code)

    def goto_initial_z(self) -> None:
        self.builder.add(CannedCycleInitialPointReturn(comment="return to initial point"))

    def goto_r_plane(self) -> None:
        self.builder.add(CannedCycleRPointReturn(comment="return to R plane"))


class DrillCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = _DrillCycle(comment="begin drilling cycle")

    def __init__(self, f: maybe_float, z: maybe_float, r: maybe_float | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.append(Code(code_type="F", code_number=float(f)))
        self.enter_code.sub_codes.append(Code(code_type="Z", code_number=float(z)))
        if r is not None:
            self.enter_code.sub_codes.append(Code(code_type="R", code_number=float(r)))


class SpotDrillCycle(CannedCycle):
    group: GGroups = GGroups.CANNED_CYCLE
    enter_code: GCode = _SpotDrillCycle(comment="begin spot drilling cycle")

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
    enter_code: GCode = _PeckDrillCycle(comment="begin peck drilling cycle")

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
            kwargs_to_codes(
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
    enter_code: GCode = _TapCycle(comment="begin tapping cycle")

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
            kwargs_to_codes(
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
    cancel: t.ClassVar[GCode] = _CancelCutterComp(comment="cancel cutter compensation")
    exit_code: GCode = cancel

    def __init__(self, direction: CutterCompensationDirection, d: maybe_float, *args, **kwargs):
        super().__init__(
            enter_code=GCode(
                code_number=direction.value,
                group=GGroups.CUTTER_COMPENSATION,
                sub_codes=[Code(code_type="D", code_number=float(d))],
            ),
            *args,
            **kwargs,
        )


class SetToolLengthCompensation(ModalCode):
    group: GGroups = GGroups.TOOL_LENGTH_OFFSET
    cancel: t.ClassVar[GCode] = _CancelToolLengthComp(comment="cancel tool length compensation")
    exit_code: GCode = cancel

    def __init__(self, direction: ToolLengthCompensation, h: int, *args, **kwargs):
        super().__init__(
            enter_code=GCode(
                code_number=direction.value,
                group=GGroups.TOOL_LENGTH_OFFSET,
                sub_codes=[Code(code_type="H", code_number=h)],
            ),
            *args,
            **kwargs,
        )
