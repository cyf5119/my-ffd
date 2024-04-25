from .utils import *
import itertools
import math

special_actions[34990] = 0
special_actions[35845] = 0
# 散火法 全屏aoe
special_actions[34959] = raid_utils.fan_shape(270)
omen_color[34959] = Colors.purple.color, Colors.white.line
special_actions[35814] = raid_utils.fan_shape(270)
omen_color[35814] = Colors.purple.color, Colors.white.line
# 魔纹炮 扇形 角度270 旋转后的范围
special_actions[34961] = 0
special_actions[35816] = 0
# 闪光 第一块发光地板读条
special_actions[34970] = 0
special_actions[35825] = 0
# 地雷魔纹 地雷预兆
omen_color[34980] = Colors.red.color, Colors.white.line
omen_color[35835] = Colors.red.color, Colors.white.line
# 烈风 小怪矩形 阿罗阿罗树木巨像
special_actions[34984] = 0
special_actions[35839] = 0
# 魔爆法
special_actions[34985] = 0
special_actions[35840] = 0
# 地隆法


class Analysis:
    def __init__(self):
        self.phase = 0
        self.globes = [0] * 2
        self.omens: list[BaseOmen] = []
        self.last_rotation = 0

        naal.on_reset(self.reset)
        saal.on_reset(self.reset)
        naal.on_effect(34990)(self.reset)
        saal.on_effect(35845)(self.reset)
        naal.on_cast(34965)(self.start)
        saal.on_cast(35820)(self.start)
        naal.on_object_spawn(2013505)(self.on_bright_arrow_spawn)
        saal.on_object_spawn(2013505)(self.on_bright_arrow_spawn)
        naal.on_effect(34964)(self.facing_helper)
        saal.on_effect(35819)(self.facing_helper)
        naal.on_lockon(493, 494)(self.lock_on)
        saal.on_lockon(493, 494)(self.lock_on)
        naal.on_effect(36063)(self.reset)
        saal.on_effect(36065)(self.reset)

    def reset(self, _=None):
        self.phase = 0
        self.globes = [0] * 2
        self.clear_omens()
        self.last_rotation = 0

    def start(self, _=None):
        self.phase = 3
        self.globes = [0] * 2
        self.clear_omens()
        self.last_rotation = 0

    def clear_omens(self):
        for o in self.omens:
            o.timeout()
        self.omens.clear()

    def on_bright_arrow_spawn(self, msg: NetworkMessage[zone_server.ObjectSpawn]):
        if not self.phase:
            return
        raid_utils.sleep(.1)
        arrow = raid_utils.NActor.by_id(msg.header.source_id)
        _next = False
        for globe in itertools.chain(raid_utils.find_actor_by_base_id(16448, 16606)):
            if abs(arrow.facing % pi2 - arrow.target_radian(globe) % pi2) < (pi/10):
                self.globes[0] = globe.id
                _next = True
            else:
                self.globes[1] = globe.id
        if (self.globes[0] != 0) and (self.globes[1] != 0) and _next:
            self.facing_helper()

    def facing_helper(self, _=None):
        self.clear_omens()
        if not self.phase:
            return
        me = raid_utils.get_me()
        idx = 0
        unseens = [3726, 3729, 3727, 3728]
        for i in range(4):
            if me.status.has_status(unseens[i]):
                idx = i
        match self.phase:
            case 3:
                actor = raid_utils.NActor.by_id(self.globes[0])
                dura = 10  # 6.1
            case 2:
                actor = raid_utils.NActor.by_id(self.globes[1])
                dura = 15  # 9.6
            case 1:
                if self.last_rotation == 0:
                    logger.debug('analysis.last_rotation error!')
                    return
                actor = next(raid_utils.find_actor_by_base_id(16446, 16604))
                dura = 10  # todo
                idx += self.last_rotation
            case _:
                logger.debug('analysis.phase error!')
                return
        self.phase -= 1
        raid_utils.sleep(.1)  # 防止顺序错乱
        self.draw(actor=actor, dura=dura, idx=idx)

    def draw(self, actor: Actor, dura: float, idx: int):
        me = raid_utils.get_me()

        # def get_pos(o: BaseOmen):
        #     return o.get_maybe_callable(
        #           me.pos + glm.rotateY(glm.vec3(0, 0, 3), me.target_radian(actor) - math.pi/2 * idx))

        def get_facing(o: BaseOmen):
            return o.get_maybe_callable(me.target_radian(actor) - math.pi/2 * idx)

        # omen = draw_guide_line(actor=me, pos=get_pos, duration=dura, radius=.1)
        omen = draw_facing_arrow(actor=me, facing=get_facing, duration=dura)
        line = raid_utils.draw_line(source=me, target=actor, color=Colors.cyan.line, duration=dura)
        self.omens.append(omen)
        self.omens.append(line)

    def lock_on(self, msg: ActorControlMessage[actor_control.SetLockOn]):
        if not raid_utils.is_me_id(msg.source_id):
            return
        me = raid_utils.get_me()
        # idx = 0
        if me.status.has_status(3721):  # 三
            idx = -1
        elif me.status.has_status(3790):  # 五
            idx = 1
        else:
            logger.debug('analysis.lockon error!')
            return
        if msg.param.lockon_id == 493:  # 顺
            idx *= -1
        # else: idx *= 1  # 494 逆
        self.last_rotation = idx


analysis = Analysis()


@naal.on_lockon(493, 494)
@saal.on_lockon(493, 494)
def forward_march(msg: ActorControlMessage[actor_control.SetLockOn]):
    actor = raid_utils.NActor.by_id(msg.source_id)
    if not actor.status.has_status(3715):
        return
    if not raid_utils.is_me_id(msg.source_id):
        return 
    idx = 0
    if actor.status.has_status(3721):  # 三
        idx = -1
    elif actor.status.has_status(3790):  # 五
        idx = 1
    if msg.param.lockon_id == 493:  # 顺
        idx *= -1

    dura = actor.status.find_status_remain(3715)
    #  TODO  距离 猜测24

    def get_pos(o: BaseOmen):
        return o.get_maybe_callable(actor.pos + glm.rotateY(glm.vec3(0, 0, 24), actor.facing + math.pi/2 * idx))
    # raid_utils.draw_knock_predict_circle(radius=5, pos=get_pos, duration=dura, knock_distance=24,
    #                                      surface_color=Colors.purple.surface, line_color=Colors.purple.line)
    draw_guide_line(actor=actor, pos=get_pos, duration=dura, radius=.1,
                    surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)

    for a in raid_utils.iter_main_party():
        if a.status.has_status(3723):
            raid_utils.draw_share(radius=6, pos=a, duration=dura,
                                  surface_color=Colors.orange.surface, line_color=Colors.orange.line)



