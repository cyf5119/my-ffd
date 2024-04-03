import glm

from .utils import *

special_actions[18882] = 0
# 龙卷风 全屏AOE
special_actions[18482] = 0
# 螺旋桨强风 全屏AOE
omen_color[18517] = Colors.red.surface, Colors.red.line
# 激光战轮
omen_color[18481] = Colors.red.surface, Colors.red.line
# 鹰式破坏炮
omen_color[19058] = Colors.red.surface, Colors.red.line
# 回旋碎踢
omen_color[18503] = Colors.red.surface, Colors.red.line
# 双重火箭飞拳


@tea.on_cast(18517)
def eye_of_the_chakram(msg: NetworkMessage[zone_server.ActorCast]):
    w = 6

    def dynamic(omen: BaseOmen):
        return max(omen.progress * w, 0.1)
    raid_utils.draw_rect(width=dynamic, length=73, duration=msg.message.cast_time,
                         pos=msg.message.pos, facing=msg.message.facing,
                         color=Colors.red.color)


@tea.on_cast(19058)
def spin_crusher(msg: NetworkMessage[zone_server.ActorCast]):
    r = 10

    def dynamic(omen: BaseOmen):
        return max(omen.progress * r, 0.1)
    raid_utils.draw_fan(degree=90, radius=dynamic, duration=msg.message.cast_time,
                        pos=msg.message.pos, facing=msg.message.facing,
                        color=Colors.red.color)


@tea.on_add_status(2142)
def compressed_water(msg: ActorControlMessage[actor_control.AddStatus]):
    # 2142 水属性压缩 29s
    actor = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(actor, msg.param.status_id, 5):
        raid_utils.draw_circle(radius=8, inner_radius=7.8, pos=actor, duration=5,
                               surface_color=Colors.lake.color, line_color=Colors.lake.line)


@tea.on_add_status(2143)
def compressed_lightning(msg: ActorControlMessage[actor_control.AddStatus]):
    # 2143 雷属性压缩 29s
    actor = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(actor, msg.param.status_id, 5):
        raid_utils.draw_circle(radius=8, inner_radius=7.8, pos=actor, duration=5,
                               surface_color=Colors.purple.color, line_color=Colors.purple.line)


@tea.on_cast(18501)
def flare_thrower(msg: NetworkMessage[zone_server.ActorCast]):
    # 18501 读条大火炎放射
    # 18502 实际伤害大火炎放射
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_fan(degree=90, radius=35, pos=actor, duration=4.2,
                        facing=actor.target_radian(raid_utils.get_actor_by_dis(actor, 0)),
                        surface_color=Colors.orange.surface, line_color=Colors.orange.line)


class Mines:
    def __init__(self):
        self.state = 0
        self.omens: list[BaseOmen] = []
        tea.on_reset(self.clear)
        tea.on_cast(18513)(self.hidden_minefield)  # 放雷
        tea.on_effect(18514)(self.hidden_mine)  # 踩雷
        tea.on_cast(18491)(self.clear)  # 终审开庭

    def clear(self, _=None):
        for o in self.omens:
            o.timeout()
        self.omens.clear()
        self.state = 0

    def hidden_minefield(self, msg: NetworkMessage[zone_server.ActorCast]):
        pos = msg.message.pos
        o = raid_utils.draw_circle(radius=8, inner_radius=7.8, pos=pos, duration=30,
                                   surface_color=Colors.red.color, line_color=Colors.red.line)
        self.omens.append(o)

    def hidden_mine(self, _):
        self.state += 1
        if self.state > 1:
            self.clear()


mines = Mines()


class FinalSentence:
    def __init__(self):
        self.rot_omen: list[raid_utils.BaseOmen] = []
        self.rot_list = [2222, 2223, 2137, 2138]  # 蓝橙紫绿
        self.buff_list = [2224, 2225, 2139, 2140]
        self.color_list = [Colors.blue.color, Colors.orange.color, Colors.purple.color, Colors.green.color]
        tea.on_add_status(2222, 2223, 2137, 2138)(self.add_rot)
        tea.on_reset(self.clear)
        tea.on_effect(18492)(self.clear)

    def add_rot(self, msg: ActorControlMessage[actor_control.AddStatus]):
        actor = raid_utils.NActor.by_id(msg.source_id)
        rot_idx = self.rot_list.index(msg.param.status_id)
        o = raid_utils.draw_circle(radius=1, pos=actor, duration=36,
                                   color=self.color_list[rot_idx])
        self.rot_omen.append(o)

    def clear(self, _=None):
        for o in self.rot_omen:
            o.timeout()
        self.rot_omen = []


final_sentence = FinalSentence()


@tea.on_cast(18505)
def super_jump(msg: NetworkMessage[zone_server.ActorCast]):
    # 18505 boss对自身 读条的超级跳
    # 18506 boss跳过去的aoe
    r = 10

    def dynamic(omen: BaseOmen):
        return max(omen.progress * r, 0.1)
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_circle(radius=r, duration=4.3,
                           pos=lambda _: raid_utils.get_actor_by_dis(actor, -1).pos,
                           surface_color=Colors.orange.surface, line_color=Colors.orange.line)
    raid_utils.draw_circle(radius=dynamic, duration=4.3,
                           pos=lambda _: raid_utils.get_actor_by_dis(actor, -1).pos,
                           color=Colors.orange.color)


@tea.on_effect(18507)
def apocalyptic_ray(msg: NetworkMessage[zone_server.ActionEffect]):
    # 18507 末世宣言 对自身读条
    # 18508 末世宣言 回头扇形多次 角度90 半径25？
    r = 25

    def dynamic(omen: BaseOmen):
        return max(omen.progress * r, 0.1)
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_fan(degree=90, radius=r, pos=actor, duration=5,
                        facing=actor.target_radian(raid_utils.get_actor_by_dis(actor, -1)),
                        surface_color=Colors.orange.surface, line_color=Colors.orange.line)
    raid_utils.draw_fan(degree=90, radius=dynamic, pos=actor, duration=5,
                        facing=actor.target_radian(raid_utils.get_actor_by_dis(actor, -1)),
                        color=Colors.orange.color)

