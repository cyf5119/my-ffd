from .utils import *

special_actions[18583] = 0
# 时间牢狱 狂暴
special_actions[18575] = 0
# 神圣大审判 地火 每个地火一个圈 不是boss的演示技能
special_actions[18580] = raid_utils.donut_shape(5.8, 6)
omen_color[18580] = Colors.cyan.color, Colors.cyan.line
# 株连 地火时候的分摊


@tea.on_add_status(2153)
def contact_regulation(msg: ActorControlMessage[actor_control.AddStatus]):
    # 判决确定：接触保护命令
    player = raid_utils.NActor.by_id(msg.source_id)
    raid_utils.draw_circle(radius=22, inner_radius=21.5, pos=player, duration=10,
                           surface_color=Colors.yellow.color, line_color=Colors.yellow.line)
    raid_utils.draw_circle(radius=1, pos=player, duration=10,
                           surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)


@tea.on_add_status(2155)
def escape_detection(msg: ActorControlMessage[actor_control.AddStatus]):
    # 判决确定：逃亡监察命令
    player = raid_utils.NActor.by_id(msg.source_id)
    raid_utils.draw_circle(radius=5, inner_radius=4.8, pos=player, duration=10,
                           surface_color=Colors.purple.color, line_color=Colors.purple.line)
    raid_utils.draw_circle(radius=1, pos=player, duration=10,
                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)


@tea.on_add_status(2152)
def escape_detection(msg: ActorControlMessage[actor_control.AddStatus]):
    # 判决确定：接触禁止命令
    player = raid_utils.NActor.by_id(msg.source_id)
    raid_utils.sleep(.1)
    raid_utils.draw_circle(radius=.5, pos=player, duration=10,
                           surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)
    if raid_utils.is_me_id(player.id):
        for a in raid_utils.iter_main_party():
            if a.status.has_status(2153):
                actor = a
        raid_utils.draw_rect(width=.3, length=20, pos=player, duration=10, facing=lambda _: player.target_radian(actor),
                             surface_color=Colors.green.color, line_color=Colors.green.line)


@tea.on_add_status(2154)
def escape_detection(msg: ActorControlMessage[actor_control.AddStatus]):
    # 判决确定：逃亡禁止命令
    player = raid_utils.NActor.by_id(msg.source_id)
    raid_utils.sleep(.1)
    raid_utils.draw_circle(radius=.5, pos=player, duration=10,
                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)
    if raid_utils.is_me_id(player.id):
        for a in raid_utils.iter_main_party():
            if a.status.has_status(2155):
                actor = a
        raid_utils.draw_rect(width=.3, length=20, pos=player, duration=10, facing=lambda _: actor.target_radian(player),
                             surface_color=Colors.green.color, line_color=Colors.green.line)


@tea.on_effect(18591)
def sacrament(msg: NetworkMessage[zone_server.ActionEffect]):
    # 18591 幻影 十字圣礼
    # 18569 十字圣礼 与上面间隔18.1
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.draw_rect(width=16, length=50, pos=actor, duration=18.1,
                         surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)


# 未来确定α 18556
class FateProjectionAlpha:
    def __init__(self):
        self.enable = False
        self.ordain_list = [0, 0]
        self.shadow = []
        self.sorted_list = []
        tea.on_cast(18555)(self.start)
        tea.on_reset(self.reset)
        tea.on_cast(19219)(self.reset)
        tea.on_effect(19214, 18586, 19213, 18585)(self.ordain)
        tea.on_set_channel(98)(self.channel)

    def reset(self, _=None):
        # 未来观测β 19219
        self.enable = False
        self.ordain_list = [0, 0]
        self.shadow = []
        self.sorted_list = []

    def start(self, _):
        # 未来观测α 18555
        self.enable = True
        self.ordain_list = [0, 0]
        self.shadow = []
        self.sorted_list = []

    def ordain(self, msg: NetworkMessage[zone_server.ActionEffect]):
        # 亚历山大幻影读 18584 0.7s 实际是1s后effect 第一次动静判断
        # 亚历山大幻影读 18858 0.7s 实际是1s后effect 第二次动静判断
        match msg.message.action_id:
            case 19214:
                self.ordain_list[0] = 1
                # logger.debug("1静")
            case 18586:
                self.ordain_list[1] = 1
                # logger.debug("2静")
            case 19213:
                self.ordain_list[0] = 2
                # logger.debug("1动")
            case 18585:
                self.ordain_list[1] = 2
                # logger.debug("2动")
            case _:
                logger.debug("一测动静获取错误")

    def channel(self, msg: ActorControlMessage[actor_control.SetChanneling]):
        if not self.enable:
            return
        self.shadow.append([msg.source_id, msg.param.target_id])
        if len(self.shadow) >= 8:
            self.sorted_list = sorted(self.shadow, key=lambda x: x[1], reverse=True)

            # 0为分摊 1为大圈 234为电 567无
            for idx in range(8):
                player = raid_utils.NActor.by_id(self.sorted_list[idx][0])
                # logger.debug(f"idx = {idx}, name = {player.name}, shadow = {self.sorted_list[idx][1]}")
                if idx == 0:
                    raid_utils.draw_share(radius=4, pos=player, duration=35.9,
                                          surface_color=Colors.red.surface, line_color=Colors.red.line)
                elif idx == 1:
                    raid_utils.draw_decay(radius=5, pos=player, duration=35.4,
                                          surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)
                    raid_utils.draw_circle(radius=30, inner_radius=29.5, pos=player, duration=35.4,
                                           surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)
                elif idx < 5:
                    raid_utils.draw_circle(radius=0.5, pos=player, duration=36.4,
                                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)
                else:
                    pass
                    # 还没想好闲人写什么


fate_projection_alpha = FateProjectionAlpha()


@tea.on_effect(18589)
def punch(msg: NetworkMessage[zone_server.ActionEffect]):
    # 18589 幻影 正义之跃
    # 18565 正义之跃 间隔33.054
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.sleep(28)
    raid_utils.draw_circle(radius=10, duration=5,
                           pos=lambda _: raid_utils.get_actor_by_dis(actor, -1).pos,
                           surface_color=Colors.orange.surface, line_color=Colors.orange.line)


@tea.on_effect(18592)
def spread(_):
    # 18592 幻影 制导 动画技能 分散
    # 18861 制导 动画技能
    raid_utils.sleep(27.5)
    for player in raid_utils.iter_main_party():
        raid_utils.draw_circle(radius=6, pos=player, duration=6.1,
                               surface_color=Colors.purple.surface, line_color=Colors.purple.line)


@tea.on_effect(18590)
def donut(msg: NetworkMessage[zone_server.ActionEffect]):
    # 18590 幻影 拜火圣礼
    # 18566 拜火圣礼 月环
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    raid_utils.sleep(28)
    raid_utils.draw_circle(radius=50, inner_radius=8, pos=actor, duration=5,
                           surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)


# 未来确定β 19220
class FateProjectionBeta:
    def __init__(self):
        self.state = 0
        self.shadow = []
        self.sorted_list = []
        tea.on_cast(19219)(self.start)  # 未来观测β 19219
        tea.on_reset(self.reset)
        tea.on_cast(18574)(self.reset)  # 18574 神圣大审判
        tea.on_set_channel(98)(self.channel)
        tea.on_effect(18590)(self.donut)
        tea.on_effect(18592)(self.spread)
        tea.on_effect(18593)(self.stack)

    def reset(self, _=None):
        self.state = 0
        self.shadow = []
        self.sorted_list = []

    def start(self, _):
        self.state = 1
        self.shadow = []
        self.sorted_list = []

    def channel(self, msg: ActorControlMessage[actor_control.SetChanneling]):
        if not self.state:
            return
        self.shadow.append([msg.source_id, msg.param.target_id])
        if len(self.shadow) >= 8:
            self.sorted_list = sorted(self.shadow, key=lambda x: x[1], reverse=True)

            # 0为大暗 1为大光 357为小光 6远线小暗 4近线小暗 2小暗
            for idx in range(8):
                player = raid_utils.NActor.by_id(self.sorted_list[idx][0])
                # logger.debug(f"idx = {idx}, name = {player.name}, shadow = {self.sorted_list[idx][1]}")
                if idx == 0:
                    raid_utils.draw_circle(radius=5, inner_radius=4.8, pos=player, duration=43.3,
                                           surface_color=Colors.purple.color, line_color=Colors.purple.line)
                    raid_utils.draw_circle(radius=1, pos=player, duration=43.3,
                                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)
                elif idx == 1:
                    raid_utils.draw_circle(radius=22, inner_radius=21.5, pos=player, duration=43.3,
                                           surface_color=Colors.yellow.color, line_color=Colors.yellow.line)
                    raid_utils.draw_circle(radius=1, pos=player, duration=43.3,
                                           surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)
                elif idx in [2, 4, 6]:
                    raid_utils.draw_circle(radius=.5, pos=player, duration=43.3,
                                           surface_color=Colors.purple.surface, line_color=Colors.purple.line)
                    if raid_utils.is_me_id(player.id):
                        me = raid_utils.get_me()
                        raid_utils.draw_rect(
                            width=.3, length=20, pos=player, duration=43.3,
                            facing=lambda _: raid_utils.NActor.by_id(self.sorted_list[0][0]).target_radian(me),
                            surface_color=Colors.green.color, line_color=Colors.green.line)
                elif idx in [3, 5, 7]:
                    raid_utils.draw_circle(radius=.5, pos=player, duration=43.3,
                                           surface_color=Colors.yellow.surface, line_color=Colors.yellow.line)
                    if raid_utils.is_me_id(player.id):
                        me = raid_utils.get_me()
                        raid_utils.draw_rect(
                            width=.3, length=20, pos=me, duration=43.3,
                            facing=lambda _: me.target_radian(raid_utils.NActor.by_id(self.sorted_list[1][0])),
                            surface_color=Colors.green.color, line_color=Colors.green.line
                        )

    def donut(self, msg: NetworkMessage[zone_server.ActionEffect]):
        # 月环 r8 写外头了
        pass

    def spread(self, msg: NetworkMessage[zone_server.ActionEffect]):
        # 制导分散 写外头了
        pass

    def stack(self, msg: NetworkMessage[zone_server.ActionEffect]):
        player1 = raid_utils.NActor.by_id(self.sorted_list[0][0])
        player2 = raid_utils.NActor.by_id(self.sorted_list[1][0])
        raid_utils.sleep(27.5)
        raid_utils.draw_share(radius=6, pos=player1, duration=6.1,
                              surface_color=Colors.red.surface, line_color=Colors.red.line)
        raid_utils.draw_share(radius=6, pos=player2, duration=6.1,
                              surface_color=Colors.red.surface, line_color=Colors.red.line)


fate_projection_beta = FateProjectionBeta()


@tea.on_cast(18575)
def almighty_judgment(msg: NetworkMessage[zone_server.ActorCast]):
    # 从演示咏唱到实际判定约8s 两次地火间隔是2s
    # 实际判定为 18576
    pos = msg.message.pos
    raid_utils.sleep(6)
    raid_utils.draw_circle(radius=6, pos=pos, duration=2,
                           surface_color=Colors.red.surface, line_color=Colors.red.line)
# pos:vec3(      107.988,    -0.015259,      99.9924 ) 右下
# pos:vec3(      99.9924,    -0.015259,      107.988 ) 中下
# pos:vec3(      91.9966,    -0.015259,      107.988 ) 左下
# pos:vec3(      107.988,    -0.015259,      99.9924 ) 右中

