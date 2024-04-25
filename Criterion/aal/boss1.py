import glm

from .utils import *
import math

special_actions[35506] = 0
# 鲸尾突风 横向 矩形 宽20 长20 9.7s 吹风预兆
special_actions[35507] = 0
# 鲸尾突风 纵向 矩形 宽20 长20 7.7s 吹风预兆
special_actions[35500] = 0
special_actions[35548] = 0
# 喷水 水晶直线 矩形 宽10 长76 0.7s
special_actions[35537] = 0
special_actions[35563] = 0
# 水化爆弹 圆形 半径5 2.7s 脚底黄圈
special_actions[35532] = 0
special_actions[35559] = 0
# 圆浪连潮 先钢铁 半径14 再月环 半径60 内径8
special_actions[35535] = 0
special_actions[35562] = 0
# 环浪 上面跟的月环
special_actions[35534] = 0
special_actions[35561] = 0
# 环浪连潮 先月环 半径60 内径8 再钢铁 半径14
special_actions[35533] = 0
special_actions[35562] = 0
# 圆浪 上面跟的钢铁
special_actions[35526] = 0
special_actions[35556] = 0
# 捕食气泡网 一次 第二次水晶
special_actions[35502] = 0
special_actions[35549] = 0
# 捕食气泡网 三次 第一三四次水晶
special_actions[35528] = 0
# 上升气流
special_actions[35529] = 0  # raid_utils.fan_shape(180)
special_actions[35557] = 0
# 胡乱打 猜测是上天人引导的
special_actions[35531] = 0  # raid_utils.fan_shape(180)
special_actions[35558] = 0
# 胡乱打 猜测是止步人引导的
special_actions[35521] = 0
special_actions[35553] = 0
# 愤怒之海 击退aoe
special_actions[35504] = 0
# 鲸尾台风 矩形 宽40 长40 击退气泡20
special_actions[35499] = 0
special_actions[35547] = 0
# 喷水 水晶钢铁 半径8


@naal.on_add_status(3747)
@saal.on_add_status(3747)
def hydrofall_target(msg: ActorControlMessage[actor_control.AddStatus]):
    # 选定目标：水瀑 分摊点名 圆形 半径6
    actor = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(actor, msg.param.status_id, 5):
        raid_utils.draw_share(radius=6, pos=actor, duration=5.1,
                              surface_color=Colors.orange.surface, line_color=Colors.orange.line)


@naal.on_add_status(3748)
@saal.on_add_status(3748)
def hydrobullet_target(msg: ActorControlMessage[actor_control.AddStatus]):
    # 选定目标：水化弹 分散点名 圆形 半径13 ?
    actor = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(actor, msg.param.status_id, 5):
        raid_utils.draw_circle(radius=13, inner_radius=12.9, pos=actor, duration=5.1,
                               surface_color=Colors.red.color, line_color=Colors.red.line)


def pos_check(pos: glm.vec3, limit: float = 20) -> bool:
    if abs(pos.x - center1.x) < limit and abs(pos.z - center1.z) < limit:
        return True
    else:
        return False


class SpringCrystalRect:
    def __init__(self):
        self.center_crystal_id = 0
        self.crystal_ids = []
        self.omens: list[BaseOmen] = []

        naal.on_reset(self.reset)  # 持疑
        saal.on_reset(self.reset)
        naal.on_cast(35540)(self.reset)  # 开场aoe
        saal.on_cast(35540)(self.reset)
        naal.on_npc_spawn(16542)(self.spawn)  # 生成方水晶
        saal.on_npc_spawn(16549)(self.spawn)
        naal.on_effect(35500)(self.reset)  # 水晶读条直线判定
        saal.on_effect(35548)(self.reset)

    def reset(self, _=None):
        self.center_crystal_id = 0
        self.crystal_ids.clear()
        for omen in self.omens:
            omen.timeout()
        self.omens.clear()

    def spawn(self, msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
        raid_utils.sleep(.1)
        self.crystal_ids.append(msg.header.source_id)
        if len(self.crystal_ids) > 3:
            self.center_check()

    def center_check(self):
        # 中心水晶检查，以此判断第一还是第二次
        for aid in self.crystal_ids:
            actor = raid_utils.NActor.by_id(aid)
            if pos_check(pos=actor.pos, limit=10):
                self.center_crystal_id = actor.id
        self.calculate_pos()

    def calculate_pos(self):
        # 第一次需要对坐标重新计算
        for crystal_id in self.crystal_ids:
            crystal = raid_utils.NActor.by_id(crystal_id)
            if self.center_crystal_id != 0:
                pos = crystal.pos + glm.rotateY(glm.vec3(0, 0, -20), crystal.facing + math.pi / 2)
                if not pos_check(pos=pos):
                    pos = crystal.pos + glm.rotateY(glm.vec3(0, 0, -20), crystal.facing - math.pi / 2)
            else:
                pos = crystal.pos
            self.draw_crystal(pos=pos, facing=crystal.facing)

    def draw_crystal(self, pos: glm.vec3, facing):
        # 处理坐标，画起来更好看 TODO fix bug
        if ((facing + math.pi / 4) % math.pi) > (math.pi / 2):
            # x轴 横向水晶
            omen_pos = glm.vec3(-20, pos.y, pos.z)
            omen_facing = math.pi / 2
        else:
            # z轴 纵向水晶
            omen_pos = glm.vec3(pos.x, pos.y, -20)
            omen_facing = 0

        #  第一次水晶和第二次水晶持续时长不同
        if self.center_crystal_id:
            dura = 45  # 40.1 判定时消除图形，可以更宽松的时间
        else:
            dura = 30  # 24.9 判定时消除图形，可以更宽松的时间
        omen = raid_utils.draw_rect(width=10, length=40, pos=omen_pos, duration=dura, facing=omen_facing,
                                    surface_color=Colors.red.color, line_color=Colors.white.line)
        self.omens.append(omen)


spring_crystal_rect = SpringCrystalRect()


def twintides_circle(aid, dura):
    def get_radius(o: BaseOmen):
        r = 14
        return max(o.get_maybe_callable(o.progress * r), .1)
    actor = raid_utils.NActor.by_id(aid)
    raid_utils.draw_circle(radius=14, pos=actor, duration=dura,
                           surface_color=Colors.red.surface, line_color=Colors.red.line)
    raid_utils.draw_circle(radius=get_radius, pos=actor, duration=5,
                           surface_color=Colors.red.color, line_color=Colors.white.line)


def twintides_donut(aid, dura):
    def get_inner(o: BaseOmen):
        r = 8
        return min(o.get_maybe_callable(60 - o.progress * (60 - r)), 59.9)
    actor = raid_utils.NActor.by_id(aid)
    raid_utils.draw_circle(radius=60, inner_radius=8, pos=actor, duration=dura,
                           surface_color=Colors.red.surface, line_color=Colors.red.line)
    raid_utils.draw_circle(radius=60, inner_radius=get_inner, pos=actor, duration=dura,
                           surface_color=Colors.red.color, line_color=Colors.white.line)


@naal.on_cast(35532)
@saal.on_cast(35559)
def receding_twintides(msg: NetworkMessage[zone_server.ActorCast]):
    # 圆浪连潮 先钢铁 半径14 再月环 半径60 内径8
    twintides_circle(aid=msg.header.source_id, dura=5)
    raid_utils.sleep(5)
    twintides_donut(aid=msg.header.source_id, dura=3.1)


@naal.on_cast(35534)
@saal.on_cast(35561)
def encroaching_twintides(msg: NetworkMessage[zone_server.ActorCast]):
    # 环浪连潮 先月环 半径60 内径8 再钢铁 半径14
    twintides_donut(aid=msg.header.source_id, dura=5)
    raid_utils.sleep(5)
    twintides_circle(aid=msg.header.source_id, dura=3.1)


class BubbleStrewer:
    def __init__(self):
        self.obj_1st = []
        self.obj_2rd = []

        naal.on_reset(self.reset)
        saal.on_reset(self.reset)
        naal.on_cast(35515)(self.reset)  # 散布气泡
        saal.on_cast(35515)(self.reset)
        naal.on_object_spawn(2013494)(self.spawn)
        saal.on_object_spawn(2013494)(self.spawn)

    def reset(self, _=None):
        self.obj_1st.clear()
        self.obj_2rd.clear()

    def spawn(self, msg: NetworkMessage[zone_server.ObjectSpawn]):
        raid_utils.sleep(.1)
        if len(self.obj_1st) < 4:
            self.obj_1st.append(msg.header.source_id)
            if len(self.obj_1st) == 4:
                self.draw_1st()
        else:
            self.obj_2rd.append(msg.header.source_id)

    def draw_1st(self):
        def get_width_1st(o: BaseOmen):
            r = 10
            return max(o.get_maybe_callable(o.progress * r), .1)
        for aid in self.obj_1st:
            actor = raid_utils.NActor.by_id(aid)
            raid_utils.draw_rect(width=10, length=20, pos=actor, duration=10.8,  # 10.753
                                 surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)
            raid_utils.draw_rect(width=get_width_1st, length=20, pos=actor, duration=10.8,
                                 surface_color=Colors.cyan.color, line_color=Colors.white.line)
        raid_utils.sleep(10.8)
        self.draw_2nd()

    def draw_2nd(self):
        def get_width_2rd(o: BaseOmen):
            r = 10
            return max(o.get_maybe_callable(o.progress * r), .1)
        for aid in self.obj_2rd:
            actor = raid_utils.NActor.by_id(aid)
            raid_utils.draw_rect(width=10, length=20, pos=actor, duration=3,  # 3.034
                                 surface_color=Colors.cyan.surface, line_color=Colors.cyan.line)
            raid_utils.draw_rect(width=get_width_2rd, length=20, pos=actor, duration=3,
                                 surface_color=Colors.cyan.color, line_color=Colors.white.line)


bubble_strewer = BubbleStrewer()


def rotation_check(aid_1, aid_2):
    # 给小怪检查的，1的优先级是否高于2
    act_1 = raid_utils.NActor.by_id(aid_1)
    act_2 = raid_utils.NActor.by_id(aid_2)
    rota_1 = (glm.polar(act_1.pos) + 5 / 4 * pi) % pi2
    rota_2 = (glm.polar(act_2.pos) + 5 / 4 * pi) % pi2
    return True if rota_1 > rota_2 else False


# class Roar:
#     def __init__(self):
#         self.zaratans = []
#         self.bubble_zaratans = []
#         self.normal_zaratans = []
#
#         naal.on_reset(self.reset)
#         saal.on_reset(self.reset)
#         naal.on_cast(35524)(self.reset)
#         saal.on_cast(35524)(self.reset)
#         naal.on_npc_spawn(16545)(self.spawn)
#         saal.on_npc_spawn(16552)(self.spawn)
#         naal.on_add_status(3745)(self.zaratans_add_bubbles)
#         saal.on_add_status(3745)(self.zaratans_add_bubbles)
#
#     def reset(self, _=None):
#         self.zaratans.clear()
#         self.bubble_zaratans.clear()
#         self.normal_zaratans.clear()
#
#     def spawn(self, msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
#         self.zaratans.append(msg.header.source_id)
#
#     def zaratans_add_bubbles(self, msg: ActorControlMessage[actor_control.AddStatus]):
#         actor = raid_utils.NActor.by_id(msg.source_id)
#         if actor.base_id not in [16545, 16552]:
#             return
#         self.bubble_zaratans.append(msg.source_id)
#         if len(self.bubble_zaratans) == 2:
#             for aid in self.zaratans:
#                 if aid not in self.bubble_zaratans:
#                     self.normal_zaratans.append(aid)
#             if len(self.normal_zaratans) == 2:
#                 if not rotation_check(self.bubble_zaratans[0], self.bubble_zaratans[1]):
#                     self.bubble_zaratans[0], self.bubble_zaratans[1] = self.bubble_zaratans[1], self.bubble_zaratans[0]
#                 if not rotation_check(self.normal_zaratans[0], self.normal_zaratans[1]):
#                     self.normal_zaratans[0], self.normal_zaratans[1] = self.normal_zaratans[1], self.normal_zaratans[0]
#                 self.guide()
#
#     def guide(self):
#         me = raid_utils.get_me()
#         if me.status.has_status(3743):
#             zaratans = self.bubble_zaratans
#             sid = 3743
#         elif me.status.has_status(3788):
#             zaratans = self.normal_zaratans
#             sid = 3788
#         else:
#             logger.debug('roar.guide error!')
#             return
#         idx = 0
#         for player in raid_utils.iter_main_party(exclude_id=me.id):
#             if player.status.has_status(sid):
#                 if raid_utils.role_key('thd', me.id) > raid_utils.role_key('thd', player.id):
#                     idx = 1
#         actor = zaratans[idx]
#         dura1 = 11.6
#         dura2 = 2.4
#         pos1 = actor.pos + glm.rotateY(glm.vec3(10, 0, 0), actor.facing)
#         pos2 = actor.pos + glm.rotateY(glm.vec3(0, 0, -2), actor.facing)
#         raid_utils.draw_circle(radius=3, pos=pos1, duration=dura1,
#                                surface_color=Colors.green.surface, line_color=Colors.green.line)
#         draw_guide_line(actor=me, pos=pos1, duration=dura1, radius=3)
#         raid_utils.sleep(dura1)
#         raid_utils.draw_circle(radius=1, pos=pos2, duration=dura2,
#                                surface_color=Colors.green.surface, line_color=Colors.green.line)
#         draw_guide_line(actor=me, pos=pos2, duration=dura2, radius=1)
#
#
# roar = Roar()


# 水晶3 圆水晶
@naal.on_npc_spawn(16541)
@saal.on_npc_spawn(16548)
def spring_crystal_sphere(msg: NetworkMessage[zone_server.NpcSpawn | zone_server.NpcSpawn2]):
    # 从生成到aoe判定共23.924
    raid_utils.sleep(.2)  # 尝试让它在分散分摊后再出来
    actor = raid_utils.NActor.by_id(msg.header.source_id)
    pos = actor.pos + glm.vec3(20, 0, 0)
    if not pos_check(pos):
        pos = actor.pos + glm.vec3(-20, 0, 0)

    def get_pos(_):
        if actor.status.has_status(3745):
            return pos
        else:
            return actor.pos

    def get_radius(o: BaseOmen):
        return max(o.get_maybe_callable(o.progress * 8), .1)

    raid_utils.draw_circle(radius=8, pos=get_pos, duration=23.7,
                           surface_color=Colors.red.surface, line_color=Colors.red.line)
    raid_utils.draw_circle(radius=get_radius, pos=get_pos, duration=23.7,
                           surface_color=Colors.red.color, line_color=Colors.white.line)

