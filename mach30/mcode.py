from .models import Code, CodeType, GGroups, ModalCode, SpindleDirection


class MCode(Code):
    code_type: CodeType = "M"


class StopProgram(MCode):
    code_number: int = 0


class OptionalStop(MCode):
    code_number: int = 1


class EndProgram(MCode):
    code_number: int = 30


class ToolChange(MCode):
    code_number: int = 6

    def __init__(self, tool_number: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_codes.append(Code(code_type="T", code_number=tool_number))


class SpindleOn(ModalCode):
    group: GGroups = GGroups.MCODE
    exit_code: MCode = MCode(code_number=5, comment="Spindle off")
    direction: SpindleDirection

    def __init__(self, direction: SpindleDirection, speed: int, *args, **kwargs):
        kwargs["direction"] = direction
        super().__init__(
            enter_code=MCode(code_number=direction.value, sub_codes=[Code(code_type="S", code_number=speed)]),
            *args,
            **kwargs,
        )

    def override_spindle(self, speed: int):
        self.builder.add(MCode(code_number=self.direction.value, sub_codes=[Code(code_type="S", code_number=speed)]))


class CoolantOn(ModalCode):
    group: GGroups = GGroups.MCODE
    enter_code: MCode = MCode(code_number=8, comment="Coolant on")
    exit_code: MCode = MCode(code_number=9, comment="Coolant off")
