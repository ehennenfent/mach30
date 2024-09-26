# from mach30 import ProgramBuilder
# from mach30.gcode import (
#     CircularMove,
#     GCode,
#     LinearMove,
#     RapidMove,
#     SetToolLengthCompensation,
#     SetWorkOffset,
# )
# from mach30.helpers import standard_preamble
# from mach30.mcode import EndProgram, SpindleOn, ToolChange
# from mach30.models import (
#     CircularMotionDirection,
#     Code,
#     SpindleDirection,
#     ToolLengthCompensation,
#     WorkOffset,
# )

# FEED = 18.34


# def test_build_homework():
#     builder = ProgramBuilder(number=11, preamble_comments=["ehennenfent prog5 circular countour", "T4: 0.5in end mill"])
#     standard_preamble(builder)

#     with SetWorkOffset(builder=builder, work_offset=WorkOffset.ONE):
#         builder.add(ToolChange(tool_number=4))
#         with RapidMove(builder=builder) as rapid:
#             rapid.move(x=0.250, y=0.250)
#         with SetToolLengthCompensation(builder=builder, direction=ToolLengthCompensation.ADD, h=4):
#             with SpindleOn(builder=builder, direction=SpindleDirection.FORWARD, speed=3050):
#                 with LinearMove(builder=builder, feedrate=FEED) as linear:
#                     linear.move(z=-0.15)
#                     linear.move(x=-2.5)
#                 with CircularMove(
#                     builder=builder, direction=CircularMotionDirection.COUNTERCLOCKWISE, feedrate=FEED
#                 ) as circular:
#                     circular.move(x=-3.25, y=-0.5, i=0, j=-0.5 - 0.25)
#                 with LinearMove(builder=builder, feedrate=FEED) as linear:
#                     linear.move(y=-2.75)
#                 with CircularMove(
#                     builder=builder, direction=CircularMotionDirection.COUNTERCLOCKWISE, feedrate=FEED
#                 ) as circular:
#                     circular.move(x=-2.75, y=-3.25, i=-2.75 - -3.25, j=0)
#                 with LinearMove(builder=builder, feedrate=FEED) as linear:
#                     linear.move(x=-1)
#                 with CircularMove(
#                     builder=builder, direction=CircularMotionDirection.COUNTERCLOCKWISE, feedrate=FEED
#                 ) as circular:
#                     circular.move(x=0.25, y=-2, i=0, j=-2 - -3.25)
#                 with LinearMove(builder=builder, feedrate=FEED) as linear:
#                     linear.move(y=0.25)

#                 builder.add(
#                     GCode(
#                         code_number=0,
#                         sub_codes=[
#                             GCode(code_number=28),
#                             Code(code_type="Z", code_number=0.0),
#                         ],
#                     )
#                 )
#                 builder.add(
#                     GCode(
#                         code_number=28,
#                         sub_codes=[Code(code_type="X", code_number=0.0), Code(code_type="Y", code_number=0.0)],
#                     )
#                 )
#     builder.add(EndProgram(comment="end program"))

#     builder.save("generated_programs/eric_hennenfent_program5.nc", with_line_numbers=True)
