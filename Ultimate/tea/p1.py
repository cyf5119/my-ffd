import threading
import math

from .utils import *

special_actions[18470] = 0
# 倾泻 全屏AOE
special_actions[18477] = 0
# 苦痛之手 全屏AOE
special_actions[18869] = 0
# 万变水波 可视扇形 来自活水之怒（水圈）
special_actions[18468] = 0
special_actions[18466] = 0
# 万变水波 可视扇形 来自有生命活水，后面这个是它自己放的
special_actions[18865] = 0
# 冲洗 可视黄圈


# TODO 进本时候会有timeout的报错
class Fluid:
    def __init__(self):
        self.state = 0
        self.hand_omen: raid_utils.BaseOmen = None
        self.liquid_omen: raid_utils.BaseOmen = None
        tea.on_reset(self.reset)
        tea.on_effect(18808)(self.start)  # P1 水基佬 平A 比开怪时间略晚？
        tea.on_effect(18871)(lambda _: self.hand_omen.timeout())  # 流体强袭 18871 手 10
        tea.on_effect(18864)(lambda _: self.liquid_omen.timeout())  # 流体摆动 18864 人 8

    def reset(self, _=None):
        self.state = 0
        self.hand_omen.timeout()
        self.liquid_omen.timeout()

    def start(self, _=None):
        if not self.state:
            self.state = 1
            self.draw()

    def draw(self):
        state = self.state
        match state:
            case 1:
                raid_utils.sleep(5.2)
            case 2:
                raid_utils.sleep(26.3)
            case 3:
                raid_utils.sleep(19.1)
            case _:
                return
        if state != self.state:
            return
        if state != 1:
            self.draw_hand()
        self.draw_liquid()

    def draw_hand(self):
        if hand := next(raid_utils.find_actor_by_base_id(0x2C48)):
            self.hand_omen = raid_utils.draw_fan(degree=90, radius=10, pos=hand, duration=5.2,
                                                 surface_color=Colors.red.surface, line_color=Colors.red.line)

    def draw_liquid(self):
        if liquid := next(raid_utils.find_actor_by_base_id(0x2C47)):
            self.liquid_omen = raid_utils.draw_fan(degree=90, radius=8, pos=liquid, duration=5,
                                                   surface_color=Colors.red.surface, line_color=Colors.red.line)
            self.state += 1
            self.draw()


fluid = Fluid()


@tea.on_npc_spawn(11338)
def jagd_doll(msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
    # 狩猎人偶 生成到第一次aoe有6.1秒
    raid_utils.sleep(.1)  # 等待以解决报错以及缺少一个绘制的问题
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_circle(radius=8.8, pos=actor, duration=6,
                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)


@tea.on_npc_spawn(11339)
def embolus(msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
    # 栓塞 水球
    raid_utils.sleep(.1)
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_circle(radius=1, pos=actor, duration=30,
                           surface_color=Colors.red.surface, line_color=Colors.red.line)


@tea.on_set_channel(3)
def drainage(msg: ActorControlMessage[actor_control.SetChanneling]):
    # 7.2s后 18471 排水 连线死刑 
    actor = raid_utils.NActor.by_id(msg.param.target_id)
    raid_utils.timeout_when_channeling_change(
        raid_utils.draw_circle(radius=6, pos=actor, duration=7.2,
                               surface_color=Colors.purple.surface, line_color=Colors.purple.line),
        msg)


def protean_wave(aid, times):
    actor = raid_utils.NActor.by_id(aid)

    def draw(_i):
        raid_utils.draw_fan(degree=30, radius=40, pos=actor, duration=2.1,
                            facing=lambda _: actor.target_radian(raid_utils.get_actor_by_dis(actor, _i)),
                            surface_color=Colors.red.surface, line_color=Colors.red.line)
    for x in range(times):
        draw(x)


@tea.on_cast(18466)
def protean_wave_boss(msg: NetworkMessage[zone_server.ActorCast]):
    # 万变水波 有生命活水 5.1+3.1=8.2
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.sleep(3)
    protean_wave(msg.header.source_id, 4)
    raid_utils.draw_fan(degree=30, radius=40, pos=actor, duration=2.1,
                        surface_color=Colors.red.surface, line_color=Colors.red.line)
    raid_utils.sleep(3.1)
    protean_wave(msg.header.source_id, 4)
    raid_utils.draw_fan(degree=30, radius=40, pos=actor, duration=2.1,
                        surface_color=Colors.red.surface, line_color=Colors.red.line)
        

@tea.on_cast(18869)
def protean_wave_range(msg: NetworkMessage[zone_server.ActorCast]):
    # 万变水波 活水之怒
    raid_utils.sleep(3)
    protean_wave(msg.header.source_id, 1)


class LimitCut:
    def __init__(self):
        self.enable = False
        self.state = 0
        self.p_list = [0] * 8
        tea.on_reset(self.reset)
        tea.on_lockon(79, 80, 81, 82, 83, 84, 85, 86)(self.lock_on)
        tea.on_actor_play_action_timeline(7747)(self.play)

    def reset(self, _=None):
        self.enable = False
        self.state = 0
        self.p_list = [0] * 8

    def lock_on(self, msg: ActorControlMessage[actor_control.SetLockOn]):
        idx = msg.param.lockon_id - 79
        self.p_list[idx] = msg.source_id

    def play(self, msg: PlayActionTimelineMessage):
        if not self.enable:
            return
        actor = raid_utils.NActor.by_id(msg.id)
        p1 = raid_utils.NActor.by_id(self.p_list[self.state * 2])
        p2 = raid_utils.NActor.by_id(self.p_list[self.state * 2 + 1])
        raid_utils.draw_fan(degree=90, radius=35, pos=actor, duration=1.1, facing=lambda _: actor.target_radian(p1),
                            surface_color=Colors.red.surface, line_color=Colors.red.line)
        raid_utils.draw_rect(width=10, length=50, pos=actor, duration=2.6, facing=lambda _: actor.target_radian(p2),
                             surface_color=Colors.red.surface, line_color=Colors.red.line)
        self.state += 1
        if self.state > 3:
            self.reset()


limit_cut = LimitCut()


def play(state, pos):
    r = 10
    next_pos = glm.rotateY(pos - center, -math.pi / 4) + center

    def dynamic(omen: BaseOmen):
        return max(omen.progress * r, 0.1)

    if state in [7, 8]:
        raid_utils.draw_circle(radius=r, pos=next_pos, duration=4.4,
                               surface_color=Colors.red.surface, line_color=Colors.red.line)
        raid_utils.draw_circle(radius=dynamic, pos=next_pos, duration=4.4,
                               color=Colors.red.color)
    if state in [8, 17]:
        raid_utils.draw_circle(radius=r, pos=center, duration=2.2,
                               surface_color=Colors.red.surface, line_color=Colors.red.line)
        raid_utils.draw_circle(radius=dynamic, pos=center, duration=2.2,
                               color=Colors.red.color)
    if state not in [7, 8, 9, 16, 17, 18]:
        raid_utils.draw_circle(radius=r, pos=next_pos, duration=2.2,
                               surface_color=Colors.red.surface, line_color=Colors.red.line)
        raid_utils.draw_circle(radius=dynamic, pos=next_pos, duration=2.2,
                               color=Colors.red.color)


class HawkBlaster:
    def __init__(self):
        self.state = 0
        self.state_lock = threading.Lock()
        tea.on_effect(18480)(self.start)
        tea.on_reset(self.reset)

    def reset(self, _=None):
        self.state = 0

    def start(self, msg: NetworkMessage[zone_server.ActionEffect]):
        limit_cut.enable = True
        # 鹰式破坏炮 18480 间隔2.2s 10m圆形
        with self.state_lock:
            self.state += 1
            play(self.state, msg.message.pos)
        if self.state > 17:
            self.reset()


hawk_blaster = HawkBlaster()

