from mach30.enums import CircularMotionDirection, WorkOffset
from mach30.mill.builder import ProgramBuilder
from mach30.mill.gcode import PeckDrillCycle, SpotDrillCycle
from mach30.mill.models import SpindleDirection, SpindleSettings, Tool

T1_FEED = 35.0  # IPM
T2_FEED = 10.0  # IPM
T3_FEED = round(100 * 3.82 / 0.281 * 0.003 * 2, 2)  # 8.16 IPM
T4_FEED = round(100 * 3.82 / 0.25 * 0.003 * 2, 2)  # 9.17 IPM
T5_FEED = round(500 * 3.82 / 0.5 * 0.002 * 3, 2)  # 22.92 IPM
T6_FEED = round(400 * 3.82 / 0.25 * 0.003 * 2, 2)  # 36.67 IPM


def test_build_millprogr1():

    tool_1 = Tool(
        number=1, description="3 inch FACEMILL", spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=3000)
    )
    tool_2 = Tool(
        number=2,
        description="1/2 inch 90DEG SPOT DRILL",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=2500),
    )
    tool_3 = Tool(
        number=3,
        description="LETTER K 0.281 inch DRILL- 2 FLUTE",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=round(100 * 3.82 / 0.281)),  # 1359 RPM
    )
    tool_4 = Tool(
        number=4,
        description="1/4 DRILL- 2 FLUTE",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=round(100 * 3.82 / 0.25)),  # 1528 RPM
    )
    tool_5 = Tool(
        number=5,
        description="1/2 FLAT ENDMILL- 3 FLUTE",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=round(500 * 3.82 / 0.5)),  # 3820 RPM
    )
    tool_6 = Tool(
        number=6,
        description="1/4 CHAMFER MILL- 2 FLUTE",
        spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=round(400 * 3.82 / 0.25)),  # 6112 RPM
    )

    builder = ProgramBuilder(number=40, preamble_comments=["ehennenfent mill part: facing and drilling"])

    with builder.program():
        builder.default_config()
        builder.set_work_offset(WorkOffset.ONE)

        # adjust y to center on stock, not part
        builder.rapid(x=3.625 + (1.5 * 1.25), y=1.5 - 0.25, comment="position above starting point")

        builder.use_tool(tool_1)  # 3 inch face mill
        with builder.compensate(tool=tool_1, start_pos={"z": 1}, end_pos={}, direction=None):
            builder.linear_feed(z=0, feedrate=T1_FEED, comment="slow plunge to facing height")
            builder.linear_feed(x=1.5 * -1.25, comment="face past the end")
            builder.rapid(z=0.1, comment="raise spindle before canceling length comp")

        builder.use_tool(tool_2)  # spot drill
        with builder.compensate(tool=tool_2, start_pos={"z": 1}, end_pos={}, direction=None):
            builder.rapid(x=0.650, y=1.850, z=0.1, comment="position above hole a")
            with SpotDrillCycle(
                builder=builder,
                f=T1_FEED,
                z=-1 * (0.25 * 0.5) - 0.007,  # spot drill to end up with .007 chamfer
                r=0.1,
            ) as cycle:  # spot drill
                # First hole is drilled by default
                cycle.move(x=2.5, y=1.5) # hole c

            builder.rapid(x=1.0, y=1.0, z=0.1, comment="position above hole b")
            with SpotDrillCycle(
                builder=builder,
                f=T1_FEED,
                z=-1 * (0.281 * 0.5) - 0.007, # spot drill to end up with .007 chamfer
                r=0.1,
            ) as cycle:  # spot drill
                # First hole is drilled by default
                cycle.move(x=2.938, y=0.562) # hole d
            builder.rapid(z=1, comment="raise spindle before canceling length comp")

        builder.use_tool(tool_4)  # 1/4 drill
        with builder.compensate(tool=tool_4, start_pos={"z": 1}, end_pos={}, direction=None):
            builder.rapid(x=0.650, y=1.850, z=0.1, comment="position above hole a")
            with PeckDrillCycle(
                builder=builder,
                f=T4_FEED,
                z=-0.725 - (0.207 * 0.25), # thickness of part plus tip depth
                r=0.1,
                q=0.125,
            ) as cycle:  # peck drill
                # First hole is drilled by default
                cycle.move(x=2.5, y=1.5) # drill hole c
            builder.rapid(z=1, comment="raise spindle before canceling length comp")

        builder.use_tool(tool_3)  # k drill
        with builder.compensate(tool=tool_3, start_pos={"z": 1}, end_pos={}, direction=None):
            builder.rapid(x=1.0, y=1.0, z=0.1, comment="position above hole b")
            with PeckDrillCycle(
                builder=builder,
                f=T4_FEED,
                z=-0.45 - (0.207 * 0.281),  # 0.45 nominal hole depth plus tip depth
                r=0.1,
                q=0.125,
            ) as cycle:  # peck drill
                # First hole is drilled by default
                cycle.move(x=2.938, y=0.562) # drill hole d
            builder.rapid(z=1, comment="raise spindle before canceling length comp")

        with builder.use_global():
            builder.rapid(z=0)
            builder.rapid(x=0, y=0)
        # exiting context manager should turn the spindle off and end the program

    builder.save("generated_programs/eric_hennenfent_millpart_noline.nc", with_line_numbers=False)
    builder.save("generated_programs/eric_hennenfent_millpart.nc", with_line_numbers=True)
