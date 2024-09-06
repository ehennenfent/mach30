from .models import Code, CodeType


class MCode(Code):
    code_type: CodeType = "M"
