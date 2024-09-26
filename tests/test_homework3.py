# from mach30 import ProgramBuilder
# from mach30.gcode import GCode, LinearMove, RapidMove, SetWorkOffset
# from mach30.helpers import standard_preamble, use_tool
# from mach30.mcode import EndProgram, SpindleOn
# from mach30.models import Code, SpindleDirection, WorkOffset


# def test_build_homework():
#     builder = ProgramBuilder(number=9, preamble_comments=["ehennenfent prog3 countour", "T4: 0.5in end mill"])
#     standard_preamble(builder)

#     with SetWorkOffset(builder=builder, work_offset=WorkOffset.ONE):
#         with (
#             use_tool(builder=builder, tool_number=4),
#             SpindleOn(builder=builder, direction=SpindleDirection.FORWARD, speed=3050),
#         ):
#             with RapidMove(builder=builder) as rapid:
#                 rapid.move(x=-0.5, y=3)
#                 rapid.move(z=-0.125)
#             with LinearMove(builder=builder, feedrate=20) as linear:
#                 linear.move(x=1.25, y=3)
#                 linear.move(x=1.25, y=2)
#                 linear.move(x=1.375, y=2)
#                 linear.move(x=1.375, y=3)
#                 linear.move(x=2.875, y=3)
#                 linear.move(x=2.875, y=1.25)
#                 linear.move(x=3.125, y=1.25)
#                 linear.move(x=3.125, y=0)
#                 linear.move(x=0, y=0)
#                 linear.move(x=0, y=3.375)
#                 linear.move(z=0.1)

#             builder.add(
#                 GCode(
#                     code_number=0,
#                     sub_codes=[
#                         GCode(code_number=28),
#                         Code(code_type="Z", code_number=0.0),
#                     ],
#                 )
#             )
#             builder.add(
#                 GCode(
#                     code_number=28,
#                     sub_codes=[Code(code_type="X", code_number=0.0), Code(code_type="Y", code_number=0.0)],
#                 )
#             )
#     builder.add(EndProgram(comment="end program"))

#     builder.save("generated_programs/eric_hennenfent_program3.nc", with_line_numbers=True)
