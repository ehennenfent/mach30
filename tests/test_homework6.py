from mach30.builder import ProgramBuilder
from mach30.enums import CircularMotionDirection, WorkOffset
from mach30.gcode import DrillCycle
from mach30.models import SpindleDirection, SpindleSettings, Tool

T4_FEED = 18.0
T1_FEED = 7.0


def test_build_homework():

    tool_4 = Tool(
        number=4,
        description="0.5 inch end mill",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=3056),
    )

    tool_1 = Tool(
        number=1,
        description="0.125 inch end mill",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=5000),
    )

    builder = ProgramBuilder(number=12, preamble_comments=["ehennenfent prog6 two countour and drill"])

    with builder.program():
        builder.default_config()
        builder.set_work_offset(WorkOffset.ONE)

        builder.rapid(x=0.875, y=0, comment="position above starting point")

        builder.use_tool(tool_4, final_z=1)  # 0.5 inch end mill

        builder.linear_feed(z=-0.0625, feedrate=T4_FEED, comment="plunge to mill squircle")  # mill squircle
        builder.linear_feed(y=0.5)
        builder.circular_feed(direction=CircularMotionDirection.COUNTERCLOCKWISE, x=0.5, y=0.875, r=0.375)
        builder.linear_feed(x=-0.5)
        builder.circular_feed(direction=CircularMotionDirection.COUNTERCLOCKWISE, x=-0.875, y=0.5, r=0.375)
        builder.linear_feed(y=-0.5)
        builder.circular_feed(direction=CircularMotionDirection.COUNTERCLOCKWISE, x=-0.5, y=-0.875, r=0.375)
        builder.linear_feed(x=0.5)
        builder.circular_feed(direction=CircularMotionDirection.COUNTERCLOCKWISE, x=0.875, y=-0.5, r=0.375)
        builder.linear_feed(y=0)

        builder.linear_feed(z=-0.125, comment="plunge to mill circle")
        builder.circular_feed(direction=CircularMotionDirection.COUNTERCLOCKWISE, i=-0.875, j=0)

        builder.use_tool(tool_1, final_z=1)  # .125 end mill
        builder.rapid(x=0.875, y=0, z=0.1, comment="return to starting point, just in case")
        with DrillCycle(
            builder=builder,
            f=T1_FEED,
            z=-0.260,
            r=0.1,
        ) as cycle:  # canned drill
            # First hole is drilled by default
            cycle.move(x=0, y=-0.875)
            cycle.move(x=-0.875, y=0)
            cycle.move(x=0, y=0.875)

        with builder.use_global():
            builder.rapid(z=0)
            builder.rapid(x=0, y=0)
        # exiting context manager should turn the spindle off and end the program

    builder.save("generated_programs/prog6_readable.nc", with_line_numbers=False)
    builder.save("generated_programs/eric_hennenfent_program6.nc", with_line_numbers=True)
