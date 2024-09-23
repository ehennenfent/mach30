# from mach30 import Builder2 as ProgramBuilder
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
#     builder = ProgramBuilder(number=12, preamble_comments=["ehennenfent prog6 two countour and drill"])

#     with builder.program():  # should do standard cancellations

#         # motion
#         # plane
#         # units
#         # cutter comp
#         # tool offset
#         # coordinate system
#         # distance mode

#         builder.setplane(xy)
#         builder.setunits(inches)
#         builder.setpositionmode(absolute)
#         builder.setworkoffset(one)

#         builder.usetool(t4)  # 0.5 inch end mill
#         builder.rapid(start)
#         builder.linearfeed()  # mill squircle
#         builder.circularfeed()  # mill circle
#         builder.usetool(t1)  # .125 end mill
#         builder.circularfeed()
#         with builder.canned_cycle(drilling) as cycle:  # canned drill
#             cycle.drill(position)

#         with builder.use_global():
#             builder.rapid(etc)
#         # exiting context manager should turn the spindle off,
#         # move to a safe location, and end the program

#     builder.save("eric_hennenfent_program6.nc", with_line_numbers=True)
