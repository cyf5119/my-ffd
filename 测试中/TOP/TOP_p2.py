import itertools
from .utils import *

special_actions[31552] = 0 # 防御程序
special_actions[31553] = 0 # 防御程序
special_actions[31524] = 0 # 宇宙记忆
special_actions[31557] = 0 # 激光骤雨，狂暴
# 下面这些需要提前绘制，所以关了
special_actions[31521] = 0 # 光学射线F 大眼直线？
special_actions[31525] = 0 # 盾连击G 男人月环
special_actions[31526] = 0 # 剑击 男人钢铁
special_actions[31531] = 0 # 剑连击B 女人辣翅
special_actions[31532] = 0 # 剑连击B
special_actions[31533] = 0 # 欧米茄冰封 女人十字


# 这东西应该是要在P2P5都用上的，P5直接从这里拿就好了
class Sony:
    list = [[], [], [], []]
    priority = 0

@top.on_cast(31551, 32788) # P2一运与P5二运读条
def suoni_youxianji(msg: NetworkMessage[zone_server.ActorCast]):
    Sony.list = [[], [], [], []] # 清空列表并选择优先级
    if msg.message.action_id == 31551:
        Sony.priority = The_Omega_Protocol.p2_Party_Synergy_priority.value
    elif msg.message.action_id == 32788:
        Sony.priority = The_Omega_Protocol.p5_Sigma_priority.value

@top.on_lockon(416, 417, 418, 419)
# 圈 三角 方块 叉 z3o3_firechain_01c 02c 03c 04c
def suoni(msg: ActorControlMessage[actor_control.SetLockOn]):
    a_id = msg.source_id
    # logger.debug(f'索尼target_id = {msg.target_id}\n索尼source_id = {a_id}') # source_id 没问题 但有重复触发情况
    match msg.param.lockon_id:
        # 在这里就直接用圈叉三角方块顺序来了
        case 416: sony_icon = 0 
        case 419: sony_icon = 1
        case 417: sony_icon = 2
        case 418: sony_icon = 3
    if a_id in Sony.list[sony_icon]: return
    Sony.list[sony_icon].append(a_id)
    if len(Sony.list[sony_icon]) == 2:
        if raid_utils.role_key(Sony.priority, Sony.list[sony_icon][0]) > raid_utils.role_key(Sony.priority, Sony.list[sony_icon][1]):
            Sony.list[sony_icon][0], Sony.list[sony_icon][1] = Sony.list[sony_icon][1], Sony.list[sony_icon][0]

# 男女组合技 P2 一运 / P5 三运

def omegaMF(actor: raid_utils.NActor, dura):
    if actor.base_id == 15714: # 男人
        if actor.model_attr & 1: # 31525 盾连击G 月环 范围40 内圈10
            raid_utils.draw_circle(radius=45, inner_radius=10, pos=actor, duration=dura)
        else: # 31526 剑击 钢铁 范围10
            raid_utils.draw_circle(radius=10, pos=actor, duration=dura)
    elif actor.base_id == 15715: # 女人
        if actor.model_attr & 1: 
            # 31531 31532 剑连击B 辣翅 范围80 宽度 36 以面向 左右4安全
            # 31530 剑连击B 这个才是15715放的技能 上面那个是9020放的 应该是分成两个矩形来放辣翅了
            for r in (actor.facing + math.pi/2, actor.facing - math.pi/2):
                # 下面的位置也可填这个，但感觉下面的运算量更小一点？ pos=actor.pos + glm.rotateY(glm.vec3(0,0,4), r)
                raid_utils.draw_rect(width=90, length=41, pos= actor.pos + glm.vec3(math.sin(math.pi - r)*4, 0, -math.cos(math.pi - r)*4), facing=r, duration=dura)
        else: # 31533 欧米茄冰封 十字 范围100 宽度10
            raid_utils.draw_rect(width=10, length=45, pos=actor, facing=actor.facing, duration=dura, arg=2)
            # 这里用arg=2使ffd画十字矩形

# 大眼直线激光 P2 一运 / P5 一运

OPTICAL_UNITS = [(-(a := math.pi/4 * i), glm.vec3(math.sin(a)*45 + 100, 0, -math.cos(a)*45 + 100)) for i in range(8)]

def optical_laser(index):
    # 31521 光学射线 矩形 范围100 宽度16 判定4s
    facing, pos = OPTICAL_UNITS[index - 1]
    raid_utils.draw_rect(width=16, length=100, pos=pos, facing=facing, duration=4)

P2_SONY_MID = [glm.vec3(-11.5,0,-15), # 左圈
               glm.vec3(11.5,0,-15), # 右圈
               glm.vec3(-11.5,0,-5), # 左叉
               glm.vec3(11.5,0,-5), # 右叉
               glm.vec3(-11.5,0,5), # 左三角
               glm.vec3(11.5,0,5), # 右三角
               glm.vec3(-11.5,0,15), # 左方块
               glm.vec3(11.5,0,15)] # 右方块
P2_SONY_REMOTE = [glm.vec3(-10.8,0,-15.4), # 左圈
                  glm.vec3(10.8,0,15.4), # 右圈
                  glm.vec3(-17.8,0,-5.6), # 左叉
                  glm.vec3(17.8,0,5.6), # 右叉
                  glm.vec3(-17.8,0,5.6), # 左三角
                  glm.vec3(10.5,0,-15.4), # 右三角
                  glm.vec3(-10.5,0,15.4), # 左方块
                  glm.vec3(10.8,0,-15.4)] # 右方块
P2_STACK_MID = [glm.vec3(2,0,-13),
                glm.vec3(0,0,-15)] # 左下，中线
P2_STACK_REMOTE = [glm.vec3(5.6,0,-13),
                   glm.vec3(-5.6,0,-13)] # 左右，远线 

# 协作程序PT

class Party_Synergy:
    def __init__(self):
        self.state = 0 # 阶段控制
        self.state_lock = threading.Lock() # 线程锁
        self.is_mid = 0 # 中线还是远线
        self.stack_list = [] # 分摊点名的人
        self.sony_list = 0 # 索尼列表
        self.last_run_time = 0
        top.on_reset(lambda _: setattr(self, 'state', 0)) # 团灭重置
        top.on_cast(31551)(self.start) # 一运读条
        top.on_actor_play_action_timeline(7747)(self.on_action_timeline_7747) # 传送出现
        top.on_map_effect(self.on_map_effect_omen) # 视觉组闪光特效
        top.on_add_status_by_action(1675)(self.on_add_status_1675) # 附加buff 欧米茄F
        top.on_add_status(3427, 3428)(self.on_add_glitch) # 附加中线远线
        top.on_lockon(100)(self.stack) # 分摊点名特效

    def start(self, _):
        self.state = 4
        self.is_mid = 0
        self.stack_list = []
        self.sony_list = 0
        self.last_run_time = 0

    def on_action_timeline_7747(self, msg: PlayActionTimelineMessage):
        if not self.state: return
        actor = raid_utils.NActor.by_id(msg.id)
        if actor.base_id == 15714 or actor.base_id == 15715:
            with self.state_lock:
                if self.state > 2:
                    self.state -= 1
                    omegaMF(actor, 5.3) # 3.8s后读条 5.3s后判定

        now = time.time() # 限制触发一次
        if now - self.last_run_time < 15: return
        self.last_run_time = now
        self.sony_list = Sony.list
        myself = raid_utils.get_me()
        optical_unit = next(raid_utils.find_actor_by_base_id(15716))
        r = glm.polar(center - optical_unit.pos).y
        for i in range(4): # 判断自己位置
            if myself.id in self.sony_list[i]:
                idx = 2*i + self.sony_list[i].index(myself.id)
        if self.is_mid: # 根据中远拿位置坐标并旋转
            mypos = glm.rotateY(P2_SONY_MID[idx], r) + center
        else:
            mypos = glm.rotateY(P2_SONY_REMOTE[idx], r) + center
        # 在组合技就画出方便准备去自己位置
        raid_utils.draw_circle(radius=1, pos=mypos, duration=5.3, surface_color=0, line_color=col.orange_line)
        raid_utils.draw_line(myself, mypos, width=5, duration=5.3, color=col.orange_line)
        raid_utils.sleep(5.3) # 触发到组合技5.3s 组合技到分散6.8s
        raid_utils.draw_circle(radius=1, pos=mypos, duration=6.8, surface_color=0, line_color=col.green_line)
        raid_utils.draw_line(myself, mypos, width=5, duration=6.8, color=col.green_line)
        
    def on_map_effect_omen(self, msg: NetworkMessage[zone_server.MapEffect]):
        if msg.message.state == 64 and msg.message.play_state == 128:
            if self.state != 2: return
            self.state = 1
            optical_laser(msg.message.index) # p5会用到所以弄出去了

            # 31535 欧米茄烈炎 圆形 范围7 对每人 距map effect 4s
            for actor in raid_utils.iter_main_party(False):
                raid_utils.draw_circle(radius=7, pos=actor, duration=4)
              
    def on_add_status_1675(self, _): # 1675 欧米茄F buff
        if self.state != 1: return
        self.state = 0
        # 31534 能量放出 圆形 范围100 击退7.2m 时间4.5s 从 15712 omega_f
        # omega_f = next(raid_utils.find_actor_by_base_id(15712))
        # raid_utils.draw_knock_predict_circle(radius= 100, pos= omega_f, knock_distance=7, duration=4.5)
        # 击退距离不确定，并且击退距离居然只能是int

        # 31526 剑击 钢铁 范围10 时间10s 从 15713 15714 omega_m
        for actor in itertools.chain(raid_utils.find_actor_by_base_id(15714)):
            raid_utils.draw_circle(radius=10, pos=actor, duration=10)
        omega_m = next(raid_utils.find_actor_by_base_id(15713)) # 单独把这个换个颜色方便找北
        raid_utils.draw_circle(radius=10, pos=omega_m, duration=10, surface_color=col.lightblue_surface, line_color=col.lightblue_line)
        myself = raid_utils.get_me()
        for i in self.sony_list:
            if myself.id in i:
                myidx = i.index(myself.id) # 判断分摊去左还是右下
        if self.is_mid: # 拿坐标并且旋转
            mypos = glm.rotateY(P2_STACK_MID[myidx], glm.polar(omega_m.pos-center).y) + omega_m.pos
        else:
            mypos = glm.rotateY(P2_STACK_REMOTE[myidx], glm.polar(omega_m.pos-center).y) + omega_m.pos
        raid_utils.draw_circle(radius=1, pos=mypos, duration=6.3, surface_color=col.green_surface, line_color=col.green_line)
        raid_utils.draw_line(myself, mypos, duration=6.3,width=5, color=col.green_line)

    def on_add_glitch(self, msg: ActorControlMessage[actor_control.AddStatus]):
        if  not self.state: return
        if msg.param.status_id == 3427: # 中线
            self.is_mid = 1
        elif msg.param.status_id == 3428: # 远线
            self.is_mid = 0

    def stack(self, msg: ActorControlMessage[actor_control.SetLockOn]):
        if not self.state: return
        a_id = msg.source_id
        # logger.debug(f'分摊target_id = {msg.target_id}\n分摊source_id = {a_id}') # 测一下
        if a_id in self.stack_list: return
        self.stack_list.append(a_id)
        if len(self.stack_list) == 2: # 分摊换位判定
            stack_idx = [0,0] # 左0右1
            for i in self.sony_list:
                for j in range(2):
                    if self.stack_list[j] in i:
                        stack_idx[j] = i.index(self.stack_list[j])
            if stack_idx[0] == stack_idx[1]:
                if stack_idx[0]:
                    for i in range(4):
                        if self.stack_list[0] in self.sony_list[i]:
                            self.sony_list[i][0], self.sony_list[i][1] = self.sony_list[i][1], self.sony_list[i][0]
                else:
                    for i in range(4):
                        if self.stack_list[1] in self.sony_list[i]:
                            self.sony_list[i][0], self.sony_list[i][1] = self.sony_list[i][1], self.sony_list[i][0]
            logger.debug(f'分摊列表 = {self.sony_list}')

'''
17:16,209 31550 cast
17:19,103 31550 effect
17:24,362 7747 15715
17:24,366 7747 15714
17:29,480 31530 辣翅
17:29,481 31526 钢铁
17:32,300 mapeffect 64 128
17:35,967 31535 分散
17:36,280 31521 光学射线F
17:36,814 lockon
17:36,816 lockon
17:43,162 31534 能量放出
17:47,491 31526 钢铁
'''

Party_Synergy()



# 协作程序LB Limitless_Synergy

@top.on_set_channel(84)
def optimized_bladedance(msg: ActorControlMessage[actor_control.SetChanneling]):
    # vfx/channeling/eff/chn_teke01h.avfx 龙诗同款
    # 接线扇形死刑 欧米茄刀光剑舞
    player = raid_utils.NActor.by_id(msg.param.target_id)
    omegaMF = raid_utils.NActor.by_id(msg.source_id)
    raid_utils.timeout_when_channeling_change(raid_utils.draw_fan(
            degree=90, radius=50, pos=omegaMF, duration=16,
            facing=lambda _: glm.polar(player.update().pos - omegaMF.update().pos).y,),msg)

# 盾连击 P2 二运 / P5 一运
@top.on_cast(32369)
def beyond_defense_line(msg: NetworkMessage[zone_server.ActorCast]):
    # 32369 合成盾 可选中的和不可选中的都会使用
    if not The_Omega_Protocol.p2_Beyond_Defense_setting.value: return
    shield_m = raid_utils.NActor.by_id(msg.header.source_id)
    if shield_m.can_select: return # 所以这里限制
    myself = raid_utils.get_me() # 连线自己和盾男
    raid_utils.draw_line(myself, shield_m, color=col.yellow_line, width=5, duration=20)

@top.on_cast(31527)
def beyond_defense(msg: NetworkMessage[zone_server.ActorCast]):
    # 31527 自身读条的盾连击S
    shield_m = raid_utils.NActor.by_id(msg.header.source_id) # 盾连击给最近两人画个圈
    raid_utils.draw_circle(radius=5, duration=5, pos=lambda _: raid_utils.get_actor_by_dis(shield_m, 0).pos)
    raid_utils.draw_circle(radius=5, duration=5, pos=lambda _: raid_utils.get_actor_by_dis(shield_m, 1).pos)
    # 这个会炸，pos里用这个寻找最近玩家后一定得加.pos不然整个FFD炸掉

@top.on_effect(31528)
def pile_pitch(msg: NetworkMessage[zone_server.ActionEffect]):
    # 31528 实际造成伤害的盾连击S
    shield_m = raid_utils.NActor.by_id(msg.header.source_id) # 盾连击后的能量投射 分摊画个圈
    raid_utils.draw_circle(radius=5, duration=5, line_color=col.yellow_line, surface_color=col.yellow_surface,
                           pos= lambda _: raid_utils.get_actor_by_dis(shield_m, 0).pos)
    