import typing as t
from enum import Enum
from pathlib import Path

from pydantic import BaseModel

CodeType = t.Literal["G", "M", "T", "R", "F", "S", "H", "D", "X", "Y", "Z", "A", "B", "C", "P", "I", "J", "K", "Q"]


class MotionPlane(Enum):
    XY = 17
    XZ = 18
    YZ = 19


class SpindleDirection(Enum):
    FORWARD = 3
    REVERSE = 4


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


class CutterCompensationDirection(Enum):
    LEFT = 41
    RIGHT = 42


class ToolLengthCompensation(Enum):
    ADD = 43
    SUB = 44


class GGroups(Enum):
    MCODE = -1
    NONMODAL = 0
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


class Code(BaseModel):
    code_type: CodeType
    code_number: int | float
    sub_codes: t.List["Code"] = []
    comment: str | None = None

    def render(self) -> str:
        return self.render_without_comment() + (f" ({self.comment})" if self.comment else "")

    def render_without_comment(self) -> str:
        base = self.render_without_subcodes()
        if self.sub_codes:
            return f"{base} {' '.join(sub.render_without_comment() for sub in self.sub_codes)}"
        return base

    def render_without_subcodes(self) -> str:
        if isinstance(self.code_number, int):
            return f"{self.code_type}{self.code_number:02}"
        return f"{self.code_type}{self.code_number}"


class ProgramBuilder(BaseModel):
    number: int
    preamble_comments: t.List[str] = []
    codes: t.List[Code] = []

    modal_stacks: t.Dict[GGroups, t.List["ModalCode"]] = {}

    def add(self, *codes: Code) -> None:
        for code in codes:
            self.codes.append(code)

    def render(self, with_line_numbers: bool = False) -> str:
        return f"%\nO{self.number:05}\n{self._render_comments()}\n{self._render_codes(with_line_numbers=with_line_numbers)}\n%"

    def _render_comments(self) -> str:
        return "\n".join(f"({comment})" for comment in self.preamble_comments)

    def _render_codes(self, with_line_numbers: bool = False) -> str:
        if with_line_numbers:
            return "\n".join(f"N{i:03} {code.render()}" for i, code in enumerate(self.codes, start=1))
        return "\n".join(code.render() for code in self.codes)

    def enter(self, code: "ModalCode") -> None:
        """Add the current entry code to the modal stack"""
        self.modal_stacks.setdefault(code.group, []).append(code)

    def exit(self, group: GGroups) -> "ModalCode":
        """exit this mode and return the code that was popped"""
        if not (stack := self.modal_stacks.get(group, [])):
            raise RuntimeError(f"No modal ops for group {group} left on stack!")
        return stack.pop()

    def resume(self, group: GGroups) -> None:
        """replay the last modal entry code on the stack, if present"""
        if stack := self.modal_stacks.get(group, []):
            self.add(stack[-1].enter_code)

    def save(self, fname: Path, with_line_numbers: bool = False) -> None:
        with open(fname, "w") as f:
            f.write(self.render(with_line_numbers=with_line_numbers))


class ModalCode(BaseModel):
    enter_code: Code
    exit_code: Code | None = None
    builder: ProgramBuilder
    group: GGroups

    def __enter__(self):
        self.builder.enter(self)
        self.builder.add(self.enter_code)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.builder.exit(self.group)
        if self.exit_code is not None:
            self.builder.add(self.exit_code)
        else:
            # Maybe we need a stack that tracks the last group, so we can resume
            # whatever the previous group was? Idk if that makes sense.
            self.builder.resume(self.group)
