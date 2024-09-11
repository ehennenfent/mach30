from mach30 import ProgramBuilder
from mach30.gcode import LinearMove, RapidMove


def test_rapid():
    builder = ProgramBuilder(number=1)
    with RapidMove(builder=builder) as rapid:
        rapid.move(z=1.0)
        rapid.move(x=1.0, y=2.0)
        rapid.move(x=0, y=4, z=3)
    assert builder._render_codes() == "G00\nZ1.0\nX1.0 Y2.0\nX0.0 Y4.0 Z3.0"


def test_linear():
    builder = ProgramBuilder(number=1)
    with LinearMove(builder=builder, feedrate=1250) as linear:
        linear.move(z=1.0)
        linear.move(x=1.0, y=2.0)
        linear.move(x=0, y=4, z=3)
    assert builder._render_codes() == "G01 F1250.0\nZ1.0\nX1.0 Y2.0\nX0.0 Y4.0 Z3.0"
