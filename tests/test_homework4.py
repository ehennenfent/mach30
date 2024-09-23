from mach30 import ProgramBuilder
from mach30.gcode import (
    GCode,
    LinearMove,
    RapidMove,
    SetToolLengthCompensation,
    SetWorkOffset,
)
from mach30.helpers import standard_preamble
from mach30.mcode import EndProgram, SpindleOn, ToolChange
from mach30.models import Code, SpindleDirection, ToolLengthCompensation, WorkOffset


def test_build_homework():
    builder = ProgramBuilder(number=10, preamble_comments=["ehennenfent prog4 countour", "T4: 0.5in end mill"])
    standard_preamble(builder)

    with SetWorkOffset(builder=builder, work_offset=WorkOffset.ONE):
        builder.add(ToolChange(tool_number=4))
        with RapidMove(builder=builder) as rapid:
            rapid.move(x=0, y=-0.375)
        with SetToolLengthCompensation(builder=builder, direction=ToolLengthCompensation.ADD, h=4):
            with SpindleOn(builder=builder, direction=SpindleDirection.FORWARD, speed=3050):
                with LinearMove(builder=builder, feedrate=20) as linear:
                    linear.move(z=-0.125)
                    linear.move(x=0, y=2.9)
                    linear.move(x=0.5, y=2.9)
                    linear.move(x=0.5, y=3.15)
                    linear.move(x=3.0, y=3.15)
                    linear.move(x=3.0, y=1.275)
                    linear.move(x=1.5, y=1.275)
                    linear.move(x=1.5, y=1.15)
                    linear.move(x=3.0, y=1.15)
                    linear.move(x=3.0, y=0.15)
                    linear.move(x=-0.375, y=0.15)
                    linear.move(z=0.1)

                builder.add(
                    GCode(
                        code_number=0,
                        sub_codes=[
                            GCode(code_number=28),
                            Code(code_type="Z", code_number=0.0),
                        ],
                    )
                )
                builder.add(
                    GCode(
                        code_number=28,
                        sub_codes=[Code(code_type="X", code_number=0.0), Code(code_type="Y", code_number=0.0)],
                    )
                )
    builder.add(EndProgram(comment="end program"))

    builder.save("generated_programs/eric_hennenfent_program4.nc", with_line_numbers=True)
