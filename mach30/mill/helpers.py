import typing as t
from typing import SupportsFloat as maybe_float
from typing import get_args

from .models import Code, CodeType


def kwargs_to_codes(**kwargs: maybe_float | None) -> t.List[Code]:
    assert all(key.upper() in get_args(CodeType) for key in kwargs.keys()), f"Invalid code type in {kwargs.keys()}"
    # mypy isn't quite smart enough to understand that the assert above guarantees that the keys are valid
    return [Code(code_type=key.upper(), code_number=float(value)) for key, value in kwargs.items() if value is not None]  # type: ignore


def combine_codes(codes: t.List[Code]) -> Code | None:
    match len(codes):
        case 0:
            return None
        case 1:
            return codes[0]
        case _:
            base = codes.pop(0)
            base.sub_codes.extend(codes)
            return base
