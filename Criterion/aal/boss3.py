import glm

from .utils import *
import math

special_actions[35145] = 0
special_actions[35174] = 0
# 飙风 全屏aoe
special_actions[35207] = 0
special_actions[35208] = 0
# 开心扳机 扇形 安全区
special_actions[35148] = raid_utils.fan_shape(60)
omen_color[35148] = Colors.red.color, Colors.white.line
special_actions[35177] = raid_utils.fan_shape(60)
omen_color[35177] = Colors.red.color, Colors.white.line
# 开心扳机 扇形 危险区
special_actions[35165] = 0
special_actions[35194] = 0
# 爆炸 圆形 半径12 炸弹
special_actions[35171] = 0
special_actions[35200] = 0
# 幻惑之光 上强制移动buff
special_actions[35150] = 0
special_actions[35179] = 0
# 碎裂 半径60 击退13
special_actions[35151] = 0
special_actions[35180] = 0
# 惊喜飞针 打爆气球的
special_actions[35158] = 0
special_actions[35187] = 0
# 仙女环 月环
omen_color[35154] = Colors.purple.color, Colors.white.line
omen_color[35183] = Colors.purple.color, Colors.white.line
# 喷火 矩形 第一次


# @aal.on_npc_spawn(16481)
# def print_bomb(msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
#     raid_utils.sleep(.1)
#     actor = raid_utils.NActor.by_id(msg.header.source_id)
#     a = f'actor.id: {actor.id} \nactor.name: {actor.name} \n'
#     if actor.get_channeling(0).target_id:
#         a += f'actor.get_channeling.target_id: {actor.get_channeling(0).target_id} \n'
#     if actor.model_attr:
#         a += f'actor.model_attr: {actor.model_attr} \n'
#     if actor.timeline_model_skin:
#         a += f'actor.timeline_model_skin: {actor.timeline_model_skin} \n'
#     if actor.timeline_model_flag:
#         a += f'actor.timeline_model_flag: {list(actor.timeline_model_flag)} \n'
#     # if actor.timeline_model_flag.handle:
#     #     a += f"actor.timeline_model_flag.handle: {actor.timeline_model_flag.handle} \n"
#     # if actor.timeline_model_flag.address:
#     #     a += f"actor.timeline_model_flag.address: {actor.timeline_model_flag.address} \n"
#     logger.debug(a)


class TrickReload:
    def __init__(self):
        self.bullets: list = []
        naal.on_reset(self.reset)  # 这种本真的有reset么
        saal.on_reset(self.reset)
        naal.on_cast(35146)(self.reset)  # 花式装填
        saal.on_cast(35175)(self.reset)
        naal.on_effect(35109)(self.successful_load)
        saal.on_effect(35109)(self.successful_load)
        naal.on_effect(35110)(self.failed_load)
        saal.on_effect(35110)(self.failed_load)
        naal.on_cast(36122, 35161)(self.on_shoot)  # 陷阱射击 1/2
        saal.on_cast(36124, 35190)(self.on_shoot)

    def reset(self, _=None):
        self.bullets.clear()

    def successful_load(self, _):
        self.bullets.append(1)

    def failed_load(self, _):
        self.bullets.append(0)

    def on_shoot(self, _=None):
        logger.debug(f'bullets: {self.bullets}')
        if len(self.bullets) != 8:
            logger.debug("Bullet count error!")
            return
        match self.bullets[0]:
            case 0:  # 分摊
                self.bullets[0] = -1
                actor = next(raid_utils.iter_main_party())
                raid_utils.draw_share(radius=6, pos=actor, duration=8.1,
                                      surface_color=Colors.orange.surface, line_color=Colors.orange.line)
            case 1:  # 分散
                self.bullets[0] = -1
                for actor in raid_utils.iter_main_party():
                    raid_utils.draw_circle(radius=6, pos=actor, duration=8.1,
                                           surface_color=Colors.red.surface, line_color=Colors.red.line)
            case -1:  # 第二次射击
                self.bullets[0] = self.bullets[-1]
                self.on_shoot()


trick_reload = TrickReload()


class Bombs:
    def __init__(self):
        naal.on_npc_spawn(16481)(self.bomb_spawn)  # 炸弹
        saal.on_npc_spawn(16489)(self.bomb_spawn)
        naal.on_actor_control(ActorControlId.SetTimelineModelSkin)(self.on_set_timeline_model_skin)
        saal.on_actor_control(ActorControlId.SetTimelineModelSkin)(self.on_set_timeline_model_skin)

    def bomb_spawn(self, msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
        raid_utils.sleep(.1)
        actor = raid_utils.NActor.by_id(msg.header.source_id)
        if actor.timeline_model_flag[0]:
            logger.debug(f'{hex(actor.id)} TimelineModelFlag {actor.timeline_model_flag[0]}')
            self.draw_bomb(bomb_id=actor.id, origin_bomb_id=actor.id, dura=17.2)

    def on_set_timeline_model_skin(self, msg: ActorControlMessage[actor_control.SetTimelineModelSkin]):
        actor = raid_utils.NActor.by_id(msg.source_id)
        # logger.debug(f'{hex(actor.id)} SetTimelineModelSkin')
        if actor.base_id not in [16481, 16489]:
            # logger.debug("on_set_timeline_model_skin error!")
            return
        if msg.param.val == 0x1:
            self.draw_bomb(bomb_id=actor.id, origin_bomb_id=actor.id, dura=17.7)

    def draw_bomb(self, bomb_id, origin_bomb_id, dura):
        actor = raid_utils.NActor.by_id(bomb_id)
        raid_utils.draw_circle(radius=12, pos=actor, duration=dura,
                               surface_color=Colors.purple.color, line_color=Colors.white.line)
        next_id = actor.get_channeling(0).target_id
        if next_id != origin_bomb_id:
            self.draw_bomb(bomb_id=next_id, origin_bomb_id=origin_bomb_id, dura=dura)


bombs = Bombs()


#     ForwardMarch = 3538,  # none->player, extra=0x0
#     AboutFace = 3539,  # none->player, extra=0x0
#     LeftFace = 3540,  # none->player, extra=0x0
#     RightFace = 3541,  # none->player, extra=0x0
@naal.on_add_status(3538, 3540, 3539, 3541)
@saal.on_add_status(3538, 3540, 3539, 3541)
def forced_march(msg: ActorControlMessage[actor_control.AddStatus]):
    status_list = [3538, 3540, 3539, 3541]
    actor = raid_utils.NActor.by_id(msg.source_id)

    def get_pos(o: BaseOmen):
        idx = 0
        if actor.status.has_status(msg.param.status_id):
            idx = status_list.index(msg.param.status_id)
        target_pos = actor.pos + glm.rotateY(glm.vec3(0, 0, 12), actor.facing + idx * math.pi / 2)
        return o.get_maybe_callable(target_pos)

    if raid_utils.assert_status(actor=actor, status_id=msg.param.status_id, until_remain=5):
        # raid_utils.draw_circle(radius=.2, pos=get_pos, duration=5,
        #                        surface_color=Colors.green.surface, line_color=Colors.green.line)
        # raid_utils.draw_line(source=actor, target=get_pos, width=5, duration=5,
        #                      color=Colors.green.line)
        # raid_utils.draw_knock_predict_circle(radius=50, pos=get_pos, knock_distance=8, duration=5,
        #                                      surface_color=Colors.purple.surface, line_color=Colors.purple.line)
        draw_guide_line(actor=actor, pos=get_pos, duration=5, radius=.1,
                        surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)

        # TODO change the tool of drawing


@naal.on_cast(35150)
@saal.on_cast(35179)
def balloon_pop(msg: NetworkMessage[zone_server.ActorCast]):
    raid_utils.draw_knock_predict_circle(radius=50, pos=msg.message.pos,
                                         knock_distance=13, duration=msg.message.cast_time,
                                         surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)


class FireSpread:
    def __init__(self):
        self.is_ccw = -1
        naal.on_lockon(156, 157)(self.lockon)
        saal.on_lockon(156, 157)(self.lockon)
        naal.on_cast(35154)(self.cast)
        saal.on_cast(35183)(self.cast)

    def lockon(self, msg: ActorControlMessage[actor_control.SetLockOn]):
        if msg.param.lockon_id == 157:
            self.is_ccw = 1
        elif msg.param.lockon_id == 156:
            self.is_ccw = -1
        # 156 cw  157 ccw

    def cast(self, msg: NetworkMessage[zone_server.ActorCast]):
        facing = msg.message.facing
        pos = msg.message.pos
        raid_utils.sleep(8)
        for i in range(1, 12):
            pos = glm.rotateY(pos - center3, pi / 18 * self.is_ccw) + center3
            facing += pi / 18 * self.is_ccw
            raid_utils.draw_rect(width=5, length=12, pos=pos, facing=facing, duration=2.2,
                                 surface_color=Colors.purple.color, line_color=Colors.white.line)
            raid_utils.sleep(1.1)


fire_spread = FireSpread()


# @naal.on_set_channel(17)
# @saal.on_set_channel(17)
# def on_set_channel_17(msg: ActorControlMessage[actor_control.SetChanneling]):
#     if not raid_utils.is_me_id(msg.target_id):
#         return
#     source = raid_utils.NActor.by_id(msg.source_id)
#     target = raid_utils.NActor.by_id(msg.target_id)
#     raid_utils.timeout_when_channeling_change(
#         raid_utils.draw_circle(radius=.5, pos=source, surface_color=Colors.red.color, line_color=Colors.red.line),
#         msg
#     )
#     raid_utils.timeout_when_channeling_change(
#         raid_utils.draw_line(source=source, target=target, width=5, color=Colors.red.line),
#         msg
#     )

