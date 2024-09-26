from mach30.builder import ProgramBuilder
from mach30.enums import CircularMotionDirection, WorkOffset
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
            start_pos={"x": -1.0, "y": -1.0, "z": 0.1},
            end_pos={"x": -2, "y": -1, "z": 0.1},
        ):

            builder.linear_feed(z=-0.1, feedrate=T4_FEED, comment="plunge to mill outer countour")
            builder.linear_feed(x=0.1, comment="move below start of cut")
            builder.linear_feed(y=1.0, comment="move all the way to C")
            builder.linear_feed(x=0.5, comment="C --> D")
            builder.circular_feed(
                direction=CircularMotionDirection.COUNTERCLOCKWISE, x=1.0, y=1.5, r=0.5, comment="D --> E"
            )
            builder.linear_feed(y=1.75, comment="E --> F")
            builder.circular_feed(
                direction=CircularMotionDirection.COUNTERCLOCKWISE, x=0.5, y=2.25, r=0.5, comment="F --> G"
            )
            builder.linear_feed(x=0.1, comment="G --> H")
            builder.linear_feed(y=2.5, comment="H --> I")
            builder.linear_feed(x=1.0, y=2.75, comment="I --> J")
            builder.linear_feed(x=2.38, comment="J --> K")
            builder.linear_feed(x=2.88, y=2.5, comment="K --> L")  # K->L
            builder.linear_feed(y=0.5, comment="L --> M")
            builder.circular_feed(
                direction=CircularMotionDirection.CLOCKWISE, x=2.63, y=0.25, r=0.25, comment="M --> N"
            )
            builder.linear_feed(x=-1, comment=" N --> B --> move past end of cut")

        with builder.use_global():
            builder.rapid(z=0)
            builder.rapid(x=0, y=0)

    builder.save("generated_programs/prog8_readable.nc", with_line_numbers=False)
    builder.save("generated_programs/eric_hennenfent_program8.nc", with_line_numbers=True)
