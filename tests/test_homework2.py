from mach30.enums import WorkOffset
from mach30.mill.builder import ProgramBuilder
from mach30.mill.gcode import DrillCycle, SpotDrillCycle
from mach30.mill.models import SpindleDirection, SpindleSettings, Tool


def test_build_homework():
    t6 = Tool(
        number=6, description="spot drill", spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=2750)
    )

    t7 = Tool(
        number=7, description="regular drill", spindle=SpindleSettings(direction=SpindleDirection.FORWARD, speed=4500)
    )

    builder = ProgramBuilder(number=3, preamble_comments=["ehennenfent 9 holes"])
    with builder.program():
        builder.default_config()
        builder.set_work_offset(WorkOffset.ONE)

        builder.rapid(x=0, y=0)
        builder.use_tool(t6)

        with builder.compensate(
            tool=t6,
            start_pos={},
            end_pos={},
            direction=None,
        ):

            with SpotDrillCycle(builder=builder, f=11, z=-0.150, r=0.1) as drill:
                drill.move(x=0, y=1)
                drill.move(x=-1.0, y=1)
                drill.move(x=-1.0, y=0)
                drill.move(x=-1.0, y=-1)
                drill.move(x=0, y=-1)
                drill.move(x=1.0, y=-1)
                drill.move(x=1.0, y=0)
                drill.move(x=1.0, y=1)

            builder.zhome()

        builder.use_tool(t7)

        with builder.compensate(
            tool=t7,
            start_pos={},
            end_pos={},
            direction=None,
        ):

            with DrillCycle(builder=builder, f=15, z=-0.350, r=0.1) as drill:
                drill.move(x=0, y=1)
                drill.move(x=-1.0, y=1)
                drill.move(x=-1.0, y=0)
                drill.move(x=-1.0, y=-1)
                drill.move(x=0, y=-1)
                drill.move(x=1.0, y=-1)
                drill.move(x=1.0, y=0)
                drill.move(x=1.0, y=1)

            builder.zhome()

    rendered = builder.render()
    assert rendered.startswith("%\nO00003\n(ehennenfent 9 holes)\n")
    assert rendered.endswith("M30 (end program)\n%")
