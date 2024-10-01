from mach30.mill.builder import ProgramBuilder


def test_rapid():
    builder = ProgramBuilder(number=1)
    builder.rapid(z=1.0)
    builder.rapid(x=1.0, y=2.0)
    builder.rapid(x=0, y=4, z=3)
    assert builder._render_codes() == "G00 Z1.0\nX1.0 Y2.0\nX0.0 Y4.0 Z3.0"


def test_linear():
    builder = ProgramBuilder(number=1)
    builder.linear_feed(z=1.0, feedrate=1250)
    builder.linear_feed(x=1.0, y=2.0)
    builder.linear_feed(x=0, y=4, z=3)
    assert builder._render_codes() == "G01 F1250.0 Z1.0\nX1.0 Y2.0\nX0.0 Y4.0 Z3.0"
