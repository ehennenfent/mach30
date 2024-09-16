from mach30 import ProgramBuilder
from mach30.gcode import DrillCycle, RapidMove, SetWorkOffset, SpotDrillCycle
from mach30.helpers import standard_preamble, use_tool
from mach30.mcode import EndProgram, SpindleOn
from mach30.models import SpindleDirection, WorkOffset


def test_build_homework():
    builder = ProgramBuilder(number=3, preamble_comments=["ehennenfent 9 holes"])
    standard_preamble(builder)

    with SetWorkOffset(builder=builder, work_offset=WorkOffset.ONE):
        with (
            use_tool(builder=builder, tool_number=6),
            SpindleOn(builder=builder, direction=SpindleDirection.FORWARD, speed=2750),
        ):
            with RapidMove(builder=builder) as rapid:
                rapid.move(x=0, y=0, z=0.1)
            with SpotDrillCycle(builder=builder, f=11, z=-0.150, r=0.1) as drill:
                drill.move(x=0, y=1)
                drill.move(x=-1.0, y=1)
                drill.move(x=-1.0, y=0)
                drill.move(x=-1.0, y=-1)
                drill.move(x=0, y=-1)
                drill.move(x=1.0, y=-1)
                drill.move(x=1.0, y=0)
                drill.move(x=1.0, y=1)

        with (
            use_tool(builder=builder, tool_number=7),
            SpindleOn(builder=builder, direction=SpindleDirection.FORWARD, speed=4500),
        ):
            with RapidMove(builder=builder) as rapid:
                rapid.move(x=0, y=0, z=0.1)
            with DrillCycle(builder=builder, f=15, z=-0.350, r=0.1) as drill:
                drill.move(x=0, y=1)
                drill.move(x=-1.0, y=1)
                drill.move(x=-1.0, y=0)
                drill.move(x=-1.0, y=-1)
                drill.move(x=0, y=-1)
                drill.move(x=1.0, y=-1)
                drill.move(x=1.0, y=0)
                drill.move(x=1.0, y=1)
    builder.add(EndProgram(comment="all done"))

    rendered = builder.render()
    assert rendered.startswith("%\nO00003\n(ehennenfent 9 holes)\n")
    assert rendered.endswith("M30 (all done)\n%")
