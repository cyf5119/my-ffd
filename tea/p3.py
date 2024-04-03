import glm
import math

from .utils import *
from .p1 import limit_cut

special_actions[18526] = 0
# 时空潜行 读条结束后传送出现的十字
special_actions[19075] = 0
# 百万神圣 全屏AOE
special_actions[18549] = 0
# 黑暗命运 飞机狂暴
special_actions[19034] = 0
# None P3最后亚历山大读的不明东西
omen_color[18519] = Colors.cyan.surface, Colors.cyan.line
# 十字圣礼 二运
omen_color[19072] = Colors.cyan.surface, Colors.cyan.line
# 神罚射线 易伤死刑
omen_color[19025] = Colors.cyan.surface, Colors.cyan.line
# 净化射线 分摊

# unknown_4a4f 只在炸出金色真心出现


def alpha_sword(dura):
    # 18539 阿尔法之剑 扇形90 半径暂定35 间隔1.07约成1.1
    actor = next(raid_utils.find_actor_by_base_id(11342))

    def _draw(_i):
        raid_utils.draw_fan(degree=90, radius=35, pos=actor, duration=dura + _i * 1.1,
                            facing=lambda _: actor.target_radian(raid_utils.get_actor_by_dis(actor, _i)),
                            surface_color=Colors.red.surface, line_color=Colors.red.line)
    for i in range(3):
        _draw(i)


def flare_thrower(times, dura):
    # 18540 大火炎放射 扇形90 半径暂定35 间隔[2.141, 2.314]暂取2.3
    actor = next(raid_utils.find_actor_by_base_id(11340))

    def _draw(_i):
        raid_utils.draw_fan(degree=90, radius=35, pos=actor, duration=dura + _i * 2.3,
                            facing=lambda _: actor.target_radian(raid_utils.get_actor_by_dis(actor, _i)),
                            surface_color=Colors.orange.surface, line_color=Colors.orange.line)
    for i in range(times):
        _draw(i)


# 过场时停小动画
@tea.on_cast(18522)
def temporal_stasis(_):
    # 时间停止 从开始咏唱到上buff有9.1s
    raid_utils.sleep(6.1)
    alpha_sword(6.9)
    # 咏唱到第一刀是13s
    flare_thrower(times=2, dura=7.2)
    # 咏唱到第一喷是13.3s
    # 这里时间停止了，也不需要特别准


@tea.on_cast(19072)
def divine_spear(msg: NetworkMessage[zone_server.ActorCast]):
    # 19072 神罚射线 圆形死刑 半径5 自动画
    # 19074 圣炎 90°扇形 半径25
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.sleep(5)
    raid_utils.draw_fan(degree=90, radius=25, pos=actor, duration=9.4,
                        facing=lambda _: actor.target_radian(raid_utils.NActor.by_id(actor.target_id)),
                        surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)


@tea.on_effect(18545)
def unknown_4871(_):
    # 飞机创造以太炸弹？
    actor = next(raid_utils.find_actor_by_base_id(11347))
    pos1 = glm.rotateY((actor.pos - center), math.pi) + center
    pos2 = glm.rotateY((actor.pos - center), math.pi) / 3 + center
    raid_utils.draw_line(source=pos1, target=pos2, color=Colors.cyan.line, width=10, duration=13.7)


@tea.on_effect(19024)
def unknown_4a50(_):
    # 上英格玛秘典 buff 真心触碰到隐身的亚历山大
    actor = next(raid_utils.find_actor_by_base_id(11347))
    raid_utils.draw_rect(width=16, length=50, pos=actor, duration=4.3, arg=2,
                         surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)
    for a in raid_utils.iter_main_party():
        if a.status.has_status(1122):
            raid_utils.draw_share(radius=4, pos=a, duration=4,
                                  surface_color=Colors.red.surface, line_color=Colors.red.line)


@tea.on_effect(18527)
def play_alpha_sword(_):
    # 18527 十字圣礼
    raid_utils.sleep(1)
    alpha_sword(5)


@tea.on_cast(18523)
def play_flare_thrower(_):
    # 18523 读条审判结晶
    raid_utils.sleep(15.5)
    flare_thrower(times=3, dura=4.6)


@tea.on_cast(19215)
def limit_cut_p3(_):
    # 19215 限制器减档
    limit_cut.enable = True

