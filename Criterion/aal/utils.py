import logging
import glm
import enum
import typing
import math

from raid_helper import utils as raid_utils
from raid_helper.utils.typing import *
from raid_helper.data import special_actions, omen_color, delay_until

main = raid_utils.FFDraw.instance

naal = raid_utils.MapTrigger.get(1179)  # 异闻
saal = raid_utils.MapTrigger.get(1180)  # 零式
center1 = glm.vec3(0, 0, 0)
center2 = glm.vec3(200, -300, 0)
center3 = glm.vec3(-200, -200, 0)

logger = logging.getLogger('raid_helper/aal')
nis_enable = naal.add_value(raid_utils.BoolCheckBox('default/enable', True))
sis_enable = saal.add_value(raid_utils.BoolCheckBox('default/enable', True))
naal.decorators.append(lambda f: (lambda *args, **kwargs: f(*args, **kwargs) if nis_enable.value else None))
saal.decorators.append(lambda f: (lambda *args, **kwargs: f(*args, **kwargs) if sis_enable.value else None))

pi = math.pi
pi2 = math.pi * 2
pi_2 = math.pi / 2
pi_4 = math.pi / 4
pi_8 = math.pi / 8


class Colors(enum.Enum):
    white = glm.vec3(1, 1, 1)
    black = glm.vec3(0, 0, 0)

    red = glm.vec3(1, .2, .2)
    green = glm.vec3(.2, 1, .2)
    blue = glm.vec3(.2, .2, 1)

    cyan = glm.vec3(.2, 1, 1)
    violet = glm.vec3(1, .2, 1)
    yellow = glm.vec3(1, 1, .2)

    orange = glm.vec3(1, .6, .2)
    pink = glm.vec3(1, .2, .6)
    grass = glm.vec3(.6, 1, .2)
    spring = glm.vec3(.2, 1, .6)
    purple = glm.vec3(.6, .2, 1)
    lake = glm.vec3(.2, .6, 1)

    @property
    def surface(self):
        return glm.vec4(self.value.x/2 + 0.5, self.value.y/2 + 0.5, self.value.z/2 + 0.5, 0.2)

    @property
    def line(self):
        return glm.vec4(self.value.x, self.value.y, self.value.z, 0.8)

    @property
    def color(self):
        return glm.vec4(self.value.x, self.value.y, self.value.z, 0.5)

    @property
    def re_surface(self):
        return glm.vec4(self.value.x, self.value.y, self.value.z, 0.2)

    @property
    def re_line(self):
        return glm.vec4(self.value.x / 2 + 0.5, self.value.y / 2 + 0.5, self.value.z / 2 + 0.5, 0.8)


arrow_points = [
    glm.vec3(0, 0, 2),
    glm.vec3(0, 0, 0),
    glm.vec3(0.5, 0, 1),
    glm.vec3(-0.5, 0, 1)
]


def draw_facing_arrow(
        actor: Actor,
        facing: typing.Callable[[BaseOmen], float] | float = None,
        duration: float = 0,
        color: typing.Callable[[BaseOmen], glm.vec4 | str] | glm.vec4 | str = Colors.green.line,
        width: int = 5
):
    omens = []
    if facing is None:
        facing = raid_utils.facing_tracker(actor)
    # elif isinstance(facing, Actor):
    #     def facing(o: BaseOmen):
    #         return o.get_maybe_callable(actor.target_radian(facing))

    def play(idx):
        def get_0(o: BaseOmen):
            return actor.pos + glm.rotateY(arrow_points[0], o.get_maybe_callable(facing))

        def get_i(o: BaseOmen):
            return actor.pos + glm.rotateY(arrow_points[idx], o.get_maybe_callable(facing))

        return raid_utils.draw_line(
            source=get_0,
            target=get_i,
            color=color,
            duration=duration,
            width=width
        )
    for i in range(1, 4):
        omens.append(play(i))
    return raid_utils.OmenGroup(*omens)


# def draw_facing_arrow_test():
#     if me := raid_utils.get_me():
#         draw_facing_arrow(actor=me, duration=10)
#
#
# # def draw_facing_arrow_test2():
# #     if me := raid_utils.get_me():
# #         draw_facing_arrow(actor=me, facing=raid_utils.NActor.by_id(me.target_id), duration=10)
#
#
# def draw_facing_arrow_test3():
#     if me := raid_utils.get_me():
#         def fac(o: BaseOmen):
#             return o.get_maybe_callable(me.facing + math.pi / 2)
#         draw_facing_arrow(actor=me, facing=fac, duration=10)
#
#
# aal.add_value(raid_utils.ClickButton('aal/draw_facing_arrow_test', draw_facing_arrow_test))
# # aal.add_value(raid_utils.ClickButton('aal/draw_facing_arrow_test2', draw_facing_arrow_test2))
# aal.add_value(raid_utils.ClickButton('aal/draw_facing_arrow_test3', draw_facing_arrow_test3))


def draw_guide_line(
        actor: typing.Callable[[], glm.vec3] | glm.vec3 | Actor,
        pos: typing.Callable[[], glm.vec3] | glm.vec3 | Actor,
        surface_color: typing.Callable[[BaseOmen], glm.vec4 | str] | glm.vec4 | str = Colors.green.surface,
        line_color: typing.Callable[[BaseOmen], glm.vec4 | str] | glm.vec4 | str = Colors.green.line,
        duration: float = 0,
        alpha: typing.Callable[[BaseOmen], float] | float = None,
        radius: float = None,
        step_distance: float = .5,
):
    if isinstance(actor, Actor):
        actor = raid_utils.pos_tracker(actor)
    if isinstance(pos, Actor):
        pos = raid_utils.pos_tracker(pos)
    scale = glm.scale(glm.vec3(step_distance * .5, 1, step_distance * .5))

    def draw_arrow_line(start: glm.vec3, end: glm.vec3, _surface_color: glm.vec4, _line_color: glm.vec4, offset=0.):
        norm_d = glm.normalize(end - start)
        dis = glm.distance(start, end)
        rot = glm.polar(norm_d).y
        drawn = offset * step_distance
        while drawn < dis:
            main.gui.add_3d_shape(
                shape=0x1010000,
                transform=glm.translate(start + (norm_d * drawn)) * glm.rotate(rot, glm.vec3(0, 1, 0)) * scale,
                surface_color=_surface_color,
                line_color=_line_color,
            )
            drawn += step_distance

    def draw_dot_line(start: glm.vec3, end: glm.vec3, _line_color: glm.vec4):
        norm_d = glm.normalize(end - start)
        dis = glm.distance(start, end)
        drawn = 0
        while drawn < dis:
            main.gui.add_3d_shape(
                shape=0x90000,
                transform=glm.translate(start + (norm_d * drawn)),
                point_color=_line_color
            )
            drawn += step_distance

    def get_shape(o: BaseOmen):
        _actor = o.get_maybe_callable(actor)
        _pos = o.get_maybe_callable(pos)
        if _actor is None or _pos is None:
            return 0
        xz_dis = glm.distance(_actor.xz, _pos.xz)

        offset = (o.play_time % .5) / .5

        if radius is not None and xz_dis > radius:
            draw_arrow_line(_actor, _pos, surface_color, line_color, offset)
        else:
            draw_dot_line(_pos, _actor, line_color)
        return 0

    return raid_utils.create_game_omen(
        shape=get_shape, pos=glm.vec3(), scale=glm.vec3(), duration=duration, alpha=alpha
    )


# def draw_guide_line_test():
#     if me := raid_utils.get_me():
#         draw_guide_line(actor=me, pos=me.pos + glm.vec3(0, 0, 10), duration=10, radius=3,
#                         surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)
#
#
# aal.add_value(raid_utils.ClickButton('aal/draw_guide_line_test', draw_guide_line_test))

