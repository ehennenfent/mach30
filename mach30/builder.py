import typing as t
from pathlib import Path
from typing import SupportsFloat as maybe_float

from pydantic import BaseModel

from .enums import (
    CircularMotionDirection,
    CutterCompensationDirection,
    GGroups,
    MotionPlane,
    PositionMode,
    SpindleDirection,
    ToolLengthCompensation,
    Units,
    WorkOffset,
)
from .gcode_basic import (
    CancelCannedCycle,
    CancelCutterComp,
    CancelToolLengthComp,
    CCWFeed,
    CWFeed,
    LinearFeed,
    Rapid,
    UseMachineCoord,
)
from .helpers import combine_codes, kwargs_to_codes
from .mcode import MCode, ToolChange
from .models import Code, GCode, SpindleSettings, Tool


class BuilderCtx:
    def __init__(self, builder: "ProgramBuilder", enter_cb, exit_cb):
        self.builder = builder
        self.enter_cb = enter_cb
        self.exit_cb = exit_cb

    def __enter__(self):
        return self.enter_cb(self)

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit_cb(self)


class ProgramBuilder(BaseModel):
    number: int
    preamble_comments: t.List[str] = []
    codes: t.List[Code] = []
    tools: t.List[Tool] = []

    modal_stacks: t.Dict[GGroups, t.List[Code]] = {}
    mode_stack: t.List[GGroups] = []

    _coolant_on: bool = False
    _use_global: bool = False
    _motion_feedrate: int | float | None = None
    _spindle_settings: SpindleSettings = SpindleSettings(direction=SpindleDirection.OFF, speed=0)  # should be stack

    # should do standard cancellations

    # motion
    # plane
    # units
    # cutter comp
    # tool offset
    # coordinate system
    # distance mode
    # spindle direction & speed
    # coolant

    @property
    def current_mode(self) -> GGroups | None:
        if not self.mode_stack:
            return None
        return self.mode_stack[-1]

    @property
    def current_tool(self) -> Tool | None:
        if not self.tools:
            return None
        return self.tools[-1]

    @property
    def current_mode_op(self) -> Code | None:
        if not self.current_mode:
            return None
        stack = self.modal_stacks.get(self.current_mode, [])
        if not stack:
            return None
        return stack[-1]

    def _add_one(self, code: Code) -> None:
        if hasattr(code, "group"):
            self.modal_stacks.setdefault(code.group, []).append(code)
            if code.group != GGroups.NONMODAL:
                self.mode_stack.append(code.group)

        if self._use_global:
            self.codes.append(UseMachineCoord(sub_codes=[code], comment=code.comment))
        else:
            self.codes.append(code)

    def add(self, *codes: Code) -> None:
        for code in codes:
            self._add_one(code)

    def __str__(self) -> str:
        return self.render(with_line_numbers=True)

    def render(self, with_line_numbers: bool = False) -> str:
        return f"%\nO{self.number:05}\n{self._render_comments()}\n\n{self._render_codes(with_line_numbers=with_line_numbers)}\n%"

    def _render_comments(self) -> str:
        all_comments = self.preamble_comments + [str(tool) for tool in self.tools]
        return "\n".join(f"({comment})" for comment in all_comments)

    def _render_codes(self, with_line_numbers: bool = False) -> str:
        if with_line_numbers:
            return "\n".join(f"N{i:03} {code.render()}" for i, code in enumerate(self.codes, start=1))
        return "\n".join(code.render() for code in self.codes)

    def save(self, fname: Path, with_line_numbers: bool = False) -> None:
        with open(fname, "w") as f:
            print(self.render(with_line_numbers=with_line_numbers), file=f)

    def use_tool(
        self,
        tool: Tool,
        length_comp: ToolLengthCompensation | None = ToolLengthCompensation.ADD,
        dia_comp: CutterCompensationDirection | None = None,
        final_z: maybe_float | None = None,
    ) -> None:
        if tool not in self.tools:
            self.tools.append(tool)

        with self.use_global():
            self.rapid(z=0, comment="explicitly move to tool-change z")
        self.add(ToolChange(tool_number=tool.number))

        if self._should_update_spindle(tool.spindle):
            self.add(
                MCode(
                    code_number=tool.spindle.direction.value,
                    sub_codes=[Code(code_type="S", code_number=tool.spindle.speed)],
                    comment="set spindle direction and speed",
                )
            )
            self._spindle_settings = tool.spindle

        if length_comp is not None:
            assert final_z is not None, "must include a final z position for tool length compensation"
            self.add(
                GCode(
                    code_number=length_comp.value,
                    group=GGroups.TOOL_LENGTH_OFFSET,
                    comment=f"set tool length compensation to {length_comp.name}",
                    sub_codes=[
                        Code(code_type="H", code_number=int(tool.number)),
                        Code(code_type="Z", code_number=float(final_z)),
                    ],
                )
            )

        assert dia_comp is None, "unimplemented"

    def override_spindle(self, new_settings: SpindleSettings) -> "BuilderCtx":
        old_settings = self._spindle_settings

        def enter_spindle(ctx: "BuilderCtx") -> None:
            ctx.builder.add(
                MCode(
                    code_number=new_settings.direction.value,
                    sub_codes=[Code(code_type="S", code_number=new_settings.speed)],
                    comment="set spindle direction and speed",
                )
            )
            ctx.builder._spindle_settings = new_settings

        def exit_spindle(ctx: "BuilderCtx") -> None:
            ctx.builder.add(
                MCode(
                    code_number=old_settings.direction.value,
                    sub_codes=[Code(code_type="S", code_number=old_settings.speed)],
                    comment="reset spindle direction and speed",
                )
            )
            ctx.builder._spindle_settings = old_settings

        return BuilderCtx(self, enter_spindle, exit_spindle)

    def override_coolant(self):
        pass

    def set_plane(self, plane: MotionPlane) -> None:
        self.add(GCode(code_number=plane.value, group=GGroups.PLANE_SELECTION, comment=f"use {plane.name} plane"))

    def set_units(self, units: Units) -> None:
        self.add(GCode(code_number=units.value, group=GGroups.UNITS, comment=f"use {units.name}"))

    def set_position_mode(self, mode: PositionMode) -> None:
        self.add(GCode(code_number=mode.value, group=GGroups.DISTANCE_MODE, comment=f"use {mode.name} distances"))

    def default_config(self) -> None:
        self.set_plane(MotionPlane.XY)
        self.set_units(Units.INCHES)
        self.set_position_mode(PositionMode.ABSOLUTE)

    def set_work_offset(self, offset: WorkOffset) -> None:
        self.add(
            GCode(code_number=offset.value, group=GGroups.COORDINATE_SYSTEM, comment=f"use work offset {offset.name}")
        )

    def program(self) -> "BuilderCtx":
        def start_program(ctx: "BuilderCtx") -> None:
            ctx.builder.add(CancelCannedCycle(comment="cancel canned cycle"))
            ctx.builder.add(CancelCutterComp(comment="cancel cutter compensation"))
            ctx.builder.add(CancelToolLengthComp(comment="cancel tool length compensation"))

        def exit_program(ctx: "BuilderCtx") -> None:
            ctx.builder.add(MCode(code_number=5, comment="turn off spindle"))
            ctx.builder.add(MCode(code_number=30, comment="end program"))

        return BuilderCtx(self, start_program, exit_program)

    def _override_mode(self, group: GGroups, code: Code) -> None:
        pass

    def rapid(
        self,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
        comment: str | None = None,
    ) -> None:

        self._move(Rapid(), comment=comment, x=x, y=y, z=z, a=a, b=b, c=c)

    def _resolve_feedrate(self, feedrate: maybe_float | None) -> float:
        if feedrate is not None:
            return float(feedrate)
        assert self._motion_feedrate is not None, "You need to provide an initial feedrate"
        return float(self._motion_feedrate)

    def linear_feed(
        self,
        feedrate: maybe_float | None = None,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        b: maybe_float | None = None,
        c: maybe_float | None = None,
        comment: str | None = None,
    ) -> None:
        motion_code = LinearFeed.with_feedrate(feedrate=self._resolve_feedrate(feedrate))

        self._move(motion_code, comment=comment, x=x, y=y, z=z, a=a, b=b, c=c)

    def circular_feed(
        self,
        direction: CircularMotionDirection,
        feedrate: maybe_float | None = None,
        x: maybe_float | None = None,
        y: maybe_float | None = None,
        z: maybe_float | None = None,
        a: maybe_float | None = None,
        i: maybe_float | None = None,
        j: maybe_float | None = None,
        k: maybe_float | None = None,
        r: maybe_float | None = None,
        comment: str | None = None,
    ) -> None:
        use_feedrate = self._resolve_feedrate(feedrate)

        motion_code: CWFeed | CCWFeed = (
            CWFeed.with_feedrate(feedrate=use_feedrate)
            if direction == CircularMotionDirection.CLOCKWISE
            else CCWFeed.with_feedrate(feedrate=use_feedrate)
        )

        self._move(motion_code, comment=comment, x=x, y=y, z=z, a=a, i=i, j=j, k=k, r=r)

    def _move(
        self,
        motion_code: Rapid | LinearFeed | CWFeed | CCWFeed,
        comment: str | None = None,
        **kwargs: maybe_float | None,
    ) -> None:
        codes: t.List[Code] = []
        if self._should_update_motion(motion_code):
            codes.append(motion_code)
            if motion_code.code_number in (1, 2, 3):
                assert hasattr(motion_code, "feedrate")  # you're welcome mypy
                self._motion_feedrate = motion_code.feedrate

        codes.extend(kwargs_to_codes(**kwargs))
        if maybe_code := combine_codes(codes):
            if comment:
                maybe_code.comment = comment
            self.add(maybe_code)

    def use_global(self) -> "BuilderCtx":
        def enter_global(ctx: "BuilderCtx") -> None:
            ctx.builder._use_global = True

        def exit_global(ctx: "BuilderCtx") -> None:
            ctx.builder._use_global = False

        return BuilderCtx(self, enter_global, exit_global)

    def _should_update_motion(self, new_code: Rapid | LinearFeed | CWFeed | CCWFeed) -> bool:
        if self.current_mode is None:
            return True
        if self.current_mode != GGroups.MOTION:
            return True
        if self.current_mode_op is None:
            return True
        if self.current_mode_op.code_number != new_code.code_number:
            return True
        if new_code.code_number in (1, 2, 3):
            assert hasattr(new_code, "feedrate")  # you're welcome mypy
            feedrate = new_code.feedrate
            if self._motion_feedrate is None or self._motion_feedrate != feedrate:
                return True
        return False

    def _should_update_spindle(self, new_spindle: SpindleSettings) -> bool:
        if self._spindle_settings is None:
            return True
        if self._spindle_settings != new_spindle:
            return True
        return False
