from pydantic import BaseModel

from .builder import ProgramBuilder
from .enums import GGroups
from .models import Code


class ModalCode(BaseModel):
    enter_code: Code
    exit_code: Code | None = None
    builder: ProgramBuilder
    group: GGroups

    def __enter__(self):
        self.builder.add(self.enter_code)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.exit_code is not None:
            self.builder.add(self.exit_code)
