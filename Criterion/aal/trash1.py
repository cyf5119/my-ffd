import glm

from .utils import *

special_actions[35776] = 0
special_actions[35791] = 0
# unknown_8bc0 钢铁 半径6 龙卷aoe 每隔0.5秒读条一次 读条0.2秒
omen_color[35768] = Colors.red.surface, Colors.red.line
omen_color[35785] = Colors.red.surface, Colors.red.line
# 螺旋尾 钢铁 半径4
omen_color[35940] = Colors.orange.surface, Colors.orange.line
omen_color[35788] = Colors.orange.surface, Colors.orange.line
# 狂水 分摊 半径8
omen_color[35769] = Colors.red.surface, Colors.red.line
omen_color[35786] = Colors.red.surface, Colors.red.line
# 泡泡吐息 扇形 半径9 角度90
special_actions[35770] = 0  # raid_utils.fan_shape(120)
special_actions[35787] = 0  # raid_utils.fan_shape(120)
# 蟹甲流 扇形 半径6 角度120
omen_color[35773] = Colors.red.surface, Colors.red.line
omen_color[35915] = Colors.red.surface, Colors.red.line
# 水化炮 矩形 宽6 长15
special_actions[35774] = raid_utils.donut_shape(8, 60)
omen_color[35774] = Colors.red.surface, Colors.red.line
special_actions[35789] = raid_utils.donut_shape(8, 60)
omen_color[35789] = Colors.red.surface, Colors.red.line
# 电漩涡 月环 半径60 内径8
omen_color[35775] = Colors.red.surface, Colors.red.line
omen_color[35790] = Colors.red.surface, Colors.red.line
# 驱逐 钢铁 半径8


@naal.on_npc_spawn(16590)
@saal.on_npc_spawn(16590)
def twister(msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
    # 16590 龙卷
    # 35776 unknown_8bc0
    raid_utils.sleep(.2)  # 为.1的时候仍偶然出现不画圈只画箭头的情况
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_circle(radius=6, pos=actor,
                               surface_color=Colors.cyan.surface, line_color=Colors.cyan.line),
        actor
    )
    raid_utils.timeout_when_cancel(
        draw_facing_arrow(actor=actor), actor
    )


@naal.on_cast(35768)
@saal.on_cast(35785)
def tail_screw(msg: NetworkMessage[zone_server.ActorCast]):
    # 螺旋尾
    def get_radius(o: BaseOmen):
        r = 4
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_circle(radius=get_radius, pos=msg.message.pos, duration=msg.message.cast_time,
                               surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )


@naal.on_cast(35769)
@saal.on_cast(35786)
def bubble_shower(msg: NetworkMessage[zone_server.ActorCast]):
    # 泡泡吐息
    def get_radius(o: BaseOmen):
        r = 9
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_fan(degree=90, radius=get_radius, pos=msg.message.pos, facing=msg.message.facing,
                            duration=msg.message.cast_time,
                            surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )


@naal.on_effect(35769)
@saal.on_effect(35786)
def crab_dribble(msg: NetworkMessage[zone_server.ActionEffect]):
    # 35769 泡泡吐息
    # 35770 蟹甲流
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_fan(degree=120, radius=6, pos=actor, facing=actor.facing + pi, duration=3.6,
                            surface_color=Colors.red.surface, line_color=Colors.red.line),
        actor
    )

    def get_radius(o: BaseOmen):
        r = 6
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_fan(degree=120, radius=get_radius, pos=actor, facing=actor.facing + pi, duration=3.6,
                            surface_color=Colors.red.color, line_color=Colors.white.line),
        actor
    )


@naal.on_cast(35941)
@saal.on_cast(35793)
def hydroshot(msg: NetworkMessage[zone_server.ActorCast]):
    # 35941 水球喷射 单点 dot+击退
    source = raid_utils.NActor.by_id(msg.header.source_id)
    target = raid_utils.NActor.by_id(msg.message.target_id)
    raid_utils.draw_knock_predict_circle(radius=60, pos=source, duration=5, knock_distance=10, actor=target,
                                         surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)


@naal.on_cast(35773)
@saal.on_cast(35915)
def hydrocannon(msg: NetworkMessage[zone_server.ActorCast]):
    # 水化泡
    def get_width(o: BaseOmen):
        r = 6
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_rect(width=get_width, length=15, pos=msg.message.pos, facing=msg.message.facing,
                             duration=msg.message.cast_time,
                             surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )


@naal.on_cast(35774)
@saal.on_cast(35789)
def electric_whorl(msg: NetworkMessage[zone_server.ActorCast]):
    # 电漩涡
    def get_inner(o: BaseOmen):
        r = 8
        return min(o.get_maybe_callable(60 - o.progress * (60 - r)), 59.9)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_circle(radius=60, inner_radius=get_inner, pos=msg.message.pos, duration=msg.message.cast_time,
                               color=Colors.red.color),
        raid_utils.NActor.by_id(msg.header.source_id)
    )
# TODO 在被击杀后omen不会立刻消除


@naal.on_cast(35775)
@saal.on_cast(35790)
def expulsion(msg: NetworkMessage[zone_server.ActorCast]):
    # 驱逐
    def get_radius(o: BaseOmen):
        r = 8
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_circle(radius=get_radius, pos=msg.message.pos, duration=msg.message.cast_time,
                               surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )

