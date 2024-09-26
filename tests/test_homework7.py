from mach30.builder import ProgramBuilder
from mach30.enums import WorkOffset
from mach30.models import SpindleDirection, SpindleSettings, Tool

T4_FEED = 18.0


def test_build_homework():

    tool_4 = Tool(
        number=4,
        description="0.5 inch end mill",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=3056),
    )

    builder = ProgramBuilder(number=13, preamble_comments=["ehennenfent program 7: contour with cutter compensation"])

    with builder.program():
        builder.default_config()
        builder.set_work_offset(WorkOffset.ONE)

        builder.rapid(x=0, y=0, comment="position above stock origin")

        builder.use_tool(tool_4)  # 0.5 inch end mill

        with builder.compensate(
            tool=tool_4,
            start_pos={"x": -1.0, "y": -1.0},
            end_pos={"x": -2, "y": -1},
        ):

            builder.linear_feed(z=-0.1, feedrate=T4_FEED, comment="plunge to mill outer countour")
            builder.linear_feed(x=0.3, comment="move below start of cut")
            builder.linear_feed(y=1.1)
            builder.linear_feed(x=1.6, y=2.7)
            builder.linear_feed(x=2.7)
            builder.linear_feed(y=0.3)
            builder.linear_feed(x=-1, comment="move past end of cut")

        with builder.use_global():
            builder.rapid(z=0)
            builder.rapid(x=0, y=0)

    builder.save("generated_programs/prog7_readable.nc", with_line_numbers=False)
    builder.save("generated_programs/eric_hennenfent_program7.nc", with_line_numbers=True)
