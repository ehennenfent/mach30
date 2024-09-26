import typing as t

from pydantic import BaseModel

from .enums import GGroups, SpindleDirection

CodeType = t.Literal["G", "M", "T", "R", "F", "S", "H", "D", "X", "Y", "Z", "A", "B", "C", "P", "I", "J", "K", "Q"]


class SpindleSettings(BaseModel):
    direction: SpindleDirection
    speed: float | int


class Tool(BaseModel):
    number: int
    description: str
    spindle: SpindleSettings

    def __str__(self) -> str:
        return f"T{self.number:02} {self.description}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tool):
            return False
        return self.number == other.number and self.spindle == other.spindle


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

    def __instancecheck__(self, instance: object) -> bool:
        # TODO - make everything classvars so this will actually work.
        """Make isinstance work even if you manually construct a Code object"""
        return (
            isinstance(instance, Code)
            and self.code_type == instance.code_type
            and self.code_number == instance.code_number
        )


class GCode(Code):
    code_type: CodeType = "G"
    group: GGroups
    args: t.List[CodeType] = []
    description: str | None = None

    @property
    def docs(self) -> str:
        return (
            f"https://www.haascnc.com/service/codes-settings.type=gcode.machine=mill.value=G{self.code_number:02}.html"
        )
