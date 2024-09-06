from .models import Code, ModalCode, CodeType

import typing as t
from typing import SupportsFloat as maybe_float


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
    enter_code: Code = Code(code_type="G", code_number=0)

    def move(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
    ):
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class LinearMove(ModalCode):
    enter_code: Code = Code(code_type="G", code_number=1)

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
    ):
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class CannedCycle(ModalCode):
    exit_code: Code = Code(code_type="G", code_number=80)

    def move(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
    ):
        codes = _six_axes_to_codes(x, y, z, a, b, c)
        if maybe_code := combine_motion_codes(codes):
            self.builder.add(maybe_code)


class DrillCycle(CannedCycle):
    enter_code: Code = Code(code_type="G", code_number=81)

    def __init__(self, f: maybe_float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enter_code.sub_codes.append(Code(code_type="F", code_number=float(f)))
