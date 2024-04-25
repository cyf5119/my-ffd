from .utils import *

special_actions[35916] = 0
special_actions[35794] = 0
# 古代暴风 全屏aoe
omen_color[35917] = Colors.red.surface, Colors.red.line
omen_color[35795] = Colors.red.surface, Colors.red.line
# 龙卷 单点 圆形 半径4
omen_color[35777] = Colors.red.surface, Colors.red.line
omen_color[35796] = Colors.red.surface, Colors.red.line
# 拍手 矩形 宽4 长12
special_actions[35918] = 0
special_actions[35897] = 0
# 古代爆震 全屏aoe
omen_color[35781] = Colors.orange.surface, Colors.orange.line
omen_color[35898] = Colors.orange.surface, Colors.orange.line
# 重力领域 分摊 圆形 半径6
omen_color[35951] = Colors.red.surface, Colors.red.line
omen_color[35900] = Colors.red.surface, Colors.red.line
# 沉岛 圆形 半径6
special_actions[35887] = 0
special_actions[35914] = 0
# 古代爆震 狂暴


@naal.on_cast(35777)
@saal.on_cast(35796)
def ovation(msg: NetworkMessage[zone_server.ActorCast]):
    # 拍手
    def get_width(o: BaseOmen):
        r = 4
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_rect(width=get_width, length=12, pos=msg.message.pos,
                             facing=msg.message.facing, duration=msg.message.cast_time,
                             surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )


@naal.on_cast(35951)
@saal.on_cast(35900)
def isle_drop(msg: NetworkMessage[zone_server.ActorCast]):
    # 沉岛
    def get_radius(o: BaseOmen):
        r = 6
        return max(o.get_maybe_callable(o.progress * r), .1)
    raid_utils.timeout_when_cancel(
        raid_utils.draw_circle(radius=get_radius, pos=msg.message.pos, duration=msg.message.cast_time,
                               surface_color=Colors.red.color, line_color=Colors.white.line),
        raid_utils.NActor.by_id(msg.header.source_id)
    )
