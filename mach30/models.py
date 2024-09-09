import typing as t
from enum import Enum

from pydantic import BaseModel

CodeType = t.Literal["G", "M", "T", "R", "F", "S", "X", "Y", "Z", "A", "B", "C"]


class MotionPlane(Enum):
    XY = 17
    XZ = 18
    YZ = 19


class SpindleDirection(Enum):
    FORWARD = 3
    REVERSE = 4


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
    MCODE = -1
    NONMODAL = 0
    MOTION = 1
    PLANE = 2
    DISTANCE = 3
    FEEDRATE = 5
    UNITS = 6
    CUTTER_COMPENSATION = 7
    TOOL_LENGTH_OFFSET = 8
    CANNED_CYCLE = 9
    CANNED_CYCLE_RETURN_MODE = 10
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

    def render(self) -> str:
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
            self.builder.resume(self.group)
