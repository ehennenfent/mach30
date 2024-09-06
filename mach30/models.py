import typing as t
from pydantic import BaseModel

CodeType = t.Literal["G", "M", "T", "R", "F", "S", "X", "Y", "Z", "A", "B", "C"]


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
    codes: t.List[Code] = []

    # This isn't complicated enough, we need to have separate ones for feedrate, spindle speed, etc.
    modal_stack: t.List[Code] = []

    def add(self, *codes: Code):
        for code in codes:
            self.codes.append(code)

    def render(self) -> str:
        return "\n".join(code.render() for code in self.codes)

    def enter(self, code: Code):
        """Add the current entry code to the modal stack"""
        self.modal_stack.append(code)

    def exit(self) -> Code:
        """exit this mode and return the code that was popped"""
        return self.modal_stack.pop()

    def resume(self):
        """replay the last modal entry code on the stack, if present"""
        if self.modal_stack:
            self.add(self.modal_stack[-1])


class ModalCode(BaseModel):
    enter_code: Code
    exit_code: Code | None = None
    builder: ProgramBuilder

    def __enter__(self):
        self.builder.enter(self.enter_code)
        self.builder.add(self.enter_code)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.builder.exit()
        if self.exit_code is not None:
            self.builder.add(self.exit_code)
        else:
            self.builder.resume()
