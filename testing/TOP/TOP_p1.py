from .utils import *

special_actions[31480] = 0 # 原子射线 狂暴
special_actions[31501] = 0 # raid_utils.fan_shape(60) # 前两次火炎放射 60°扇形
special_actions[32368] = 0 # raid_utils.fan_shape(60) # 后面的火炎放射 60°扇形
omen_color[31500] = 0, col.red_line # 只留下红线描边，不然放一起中间的很白很亮
# omen_color[31501] = 0, col.red_line # 只留下红线描边
# omen_color[32368] = 0, col.red_line # 只留下红线描边

# 循环程序

class Program_Loop:
    def __init__(self):
        self.state = 0 # 阶段控制
        self.mj = [[], [], [], []] # 装麻将玩家id
        self.tower = [[], [], [], []] # 装塔id
        self.tower_pos = [[], [], [], []] # 装塔优先级 北东南西0123
        self.tether_pos = [[], [], [], []] # 装线优先级 同上
        self.o = [] # 装大圈用
        top.on_reset(lambda _: setattr(self, 'state', 0)) # 团灭重置
        top.on_cast(31491)(self.start) # 循环程序读条
        top.on_add_status(3004,3005,3006,3451)(self.mahjong) # 上麻将buff
        top.on_object_spawn(2013244)(self.tower_spawn) # 生成塔
        top.on_set_channel(89)(self.set_tether) # 接线
        top.on_cancel_channel(89)(self.remove_channel) # 线被接走
        top.on_add_status_by_action(3401)(self.end_omen) # 被附加体力衰减
        top.on_cast(31499)(lambda _: setattr(self, 'state', 0)) # 读条全能之主

    def start(self, msg: NetworkMessage[zone_server.ActorCast]):
        # 初始化
        self.state = 5
        self.mj = [[], [], [], []]
        self.tower = [[], [], [], []]
        self.tower_pos = [[], [], [], []]
        self.tether_pos = [[], [], [], []]
        self.o = []

    def mahjong(self, msg: ActorControlMessage[actor_control.AddStatus]):
        # 进行麻将判断，并按照优先级装进去
        if not self.state: return
        mj_buff = [3004, 3005, 3006, 3451] # 麻将1234buff
        actor = raid_utils.NActor.by_id(msg.source_id)
        for i in range(4):
            if actor.status.has_status(mj_buff[i]):
                if actor.id in self.mj[i]: return
                self.mj[i].append(actor.id)
                if len(self.mj[i]) == 2: # 同麻将按优先级排序
                    priority = The_Omega_Protocol.p1_Program_Loop_priority.value
                    if raid_utils.role_key(priority, self.mj[i][0]) > raid_utils.role_key(priority, self.mj[i][1]):
                        self.mj[i][0], self.mj[i][1] = self.mj[i][1], self.mj[i][0]
    
    def tower_spawn(self, msg: NetworkMessage[zone_server.ObjectSpawn]):
        if not self.state: return
        tower = raid_utils.NActor.by_id(msg.header.source_id)
        times = 5 - self.state
        if tower.id in self.tower[times]: return # 根据塔坐标判断北东南西
        if tower.pos.z < 90 :  tower_pos = 0
        elif tower.pos.x > 110 : tower_pos = 1
        elif tower.pos.z > 110 : tower_pos = 2
        elif tower.pos.x < 90 : tower_pos = 3
        self.tower[times].append(tower.id)
        self.tower_pos[times].append(tower_pos)
        # 把塔和塔优先级装入，并排序
        if len(self.tower[times]) == 2:
            if self.tower_pos[times][0] > self.tower_pos[times][1]: # 保证按照北东南西
                self.tower[times][0], self.tower[times][1] = self.tower[times][1], self.tower[times][0]
                self.tower_pos[times][0], self.tower_pos[times][1] = self.tower_pos[times][1], self.tower_pos[times][0]
            for i in range(4): # 装入线优先级
                if not i in self.tower_pos[times]:
                    self.tether_pos[times].append(i)
            myself = raid_utils.get_me()
            if myself.id in self.mj[times]: # 这里限制只画自己的 改一改可以测全队
                _priority = self.mj[times].index(myself.id)
                _tower = raid_utils.NActor.by_id(self.tower[times][_priority])
                raid_utils.draw_circle(radius=3, pos=_tower, duration=10,line_color=col.green_line, surface_color=col.green_surface)
                raid_utils.draw_line(myself, _tower, duration=10, width=5, color=col.green_line)
            if self.state: self.state -= 1 # 阶段控制
            
    def set_tether(self, msg: ActorControlMessage[actor_control.SetChanneling]):
        if not self.state: return
        beetle = raid_utils.NActor.by_id(msg.param.target_id)
        player = raid_utils.NActor.by_id(msg.source_id)
        times = 4 - self.state # 线在塔后生成所以得比上面的少1

        if player.id in self.mj[(times + 2) % 4]:
            o = raid_utils.timeout_when_channeling_change(raid_utils.draw_circle(radius=15, pos=player, duration=15, surface_color=0, line_color=col.red_line), msg)
            # o.line_width = 5 # 没效果，应该不是这样写，不会写，开摆以后再说
            i = [o, msg] # 有个不懂的bug在多了这一步后就没了
            self.o.append(i) 
            # logger.debug(f'加入{i}')
            myself = raid_utils.get_me()
            if myself.id == player.id: # 同样是限制只画自己的
                _idx = self.mj[(times + 2) % 4].index(player.id)
                _p = glm.rotateY(glm.vec3(0, 0, -19), -self.tether_pos[times][_idx]/2 * math.pi) + center
                raid_utils.timeout_when_channeling_change(raid_utils.draw_line(player, _p, width=5, color=col.green_line, duration=10), msg)
                raid_utils.timeout_when_channeling_change(raid_utils.draw_circle(radius=1, pos=_p, duration=10, surface_color=0, line_color=col.green_line), msg)
        else:
            raid_utils.timeout_when_channeling_change(raid_utils.draw_line(player, beetle, width=5, color=col.red_line, duration=15), msg)

    def remove_channel(self, msg: ActorControlMessage[actor_control.RemoveChanneling]):
        if not self.state: return
        for i in self.o:
            if msg.source_id == i[1].source_id:
                self.o.remove(i)
                # logger.debug(f'失去连线移除{i}')

    def end_omen(self, msg:AddStatusByActionMessage):
        if not self.state: return
        o_msg = 0
        for i in self.o:
            if msg.target_id == i[1].source_id:
                o_msg = i[1]
                self.o.remove(i)
                i[0].timeout()
                # logger.debug(f'炸圈移除{i}')
        times = 4 - self.state
        actor = raid_utils.NActor.by_id(msg.target_id) # 吃大圈的人
        beetle = next(raid_utils.find_actor_by_base_id(15708))
        raid_utils.timeout_when_channeling_change(raid_utils.draw_line(actor, beetle, color=col.red_line, width=5, duration=10), o_msg)
        _idx = 0
        if msg.target_id in self.mj[(times + 1) % 4]:
            _idx = self.mj[(times + 1) % 4].index(msg.target_id)
        actor2 = raid_utils.NActor.by_id(self.mj[(times + 2) % 4][_idx]) # 这个是接下来要接线的人
        myself = raid_utils.get_me()
        if actor2.id != myself.id: return # 限制只画自己
        p1 = lambda _: (actor.pos + beetle.pos)/2 # 二者中点，接线位置
        p2 = glm.rotateY(glm.vec3(0, 0, -19), -self.tether_pos[times][_idx]/2 * math.pi) + center # 拉线位置
        raid_utils.timeout_when_channeling_change(raid_utils.draw_circle(radius=1, pos=p1, duration=10, surface_color=0, line_color=col.green_line), o_msg)
        raid_utils.timeout_when_channeling_change(raid_utils.draw_line(p1, actor2, color=col.green_line, width=5, duration=10), o_msg)
        raid_utils.timeout_when_channeling_change(raid_utils.draw_circle(radius=1, pos=p2, duration=10, surface_color=0, line_color=col.orange_line), o_msg)
        raid_utils.timeout_when_channeling_change(raid_utils.draw_line(p1, p2, color=col.orange_line, width=5, duration=10), o_msg)

Program_Loop()

# 全能之主 Pantokrator

@top.on_add_status(3507, 3508, 3509, 3510)
def condensed_wave_cannon_kyrios(msg: ActorControlMessage[actor_control.AddStatus]):
    # 31503 大功率波动炮P 直线分摊 持续时间12/18/24/30
    omega = next(raid_utils.find_actor_by_base_id(15708))
    player = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(player, msg.param.status_id, 5):
        raid_utils.draw_rect(pos=omega, width=6, length=30, duration=5, line_color=col.yellow_line, surface_color=col.yellow_surface,
                             facing=lambda _: glm.polar(player.update().pos - omega.update().pos).y)
        
@top.on_add_status(3424, 3495, 3496, 3497)
def guided_missile_kyrios(msg: ActorControlMessage[actor_control.AddStatus]):
    # 31502 跟踪导弹P 圆形单点 持续时间12/18/24/30
    actor = raid_utils.NActor.by_id(msg.source_id)
    if raid_utils.assert_status(actor, msg.param.status_id, 5):
        raid_utils.draw_circle(radius=5, pos=actor, duration=5, surface_color=col.purple_surface, line_color=col.purple_line)

'''
后续可能加起跑点去哪里
怎么跑全能之主感觉是我写不出的东西
'''

# 扩散波动炮P Diffuse_Wave_Cannon_Kyrios

class Diffuse_Wave_Cannon_Kyrios:
    def __init__(self):
        self.last_run_time = 0
        top.on_lockon(23)(self.wave_cannon_kyrios)

    def wave_cannon_kyrios(self, msg: ActorControlMessage[actor_control.SetLockOn]):
        # 31505 波动炮P 一次三个的直线单点 点名5.1触发
        omega = next(raid_utils.find_actor_by_base_id(15708))
        player = raid_utils.NActor.by_id(msg.source_id)
        raid_utils.draw_rect(pos=omega, width=6, length=30, duration=6,
                             facing= lambda _: glm.polar(player.update().pos - omega.update().pos).y)
        self.diffuse_wave_cannon_kyrios()
        
    def diffuse_wave_cannon_kyrios(self):
        # 31504 扩散波动炮P 点名两个最远的5次120扇形
        now = time.time()
        if now - self.last_run_time < 15: return
        self.last_run_time = now
        omega = next(raid_utils.find_actor_by_base_id(15708))
        raid_utils.draw_fan(pos=omega, degree=120, radius=30, duration=15,
                            facing= lambda _: glm.polar(raid_utils.get_actor_by_dis(omega, -1).pos - omega.update().pos).y)
        raid_utils.draw_fan(pos=omega, degree=120, radius=30, duration=15,
                            facing= lambda _: glm.polar(raid_utils.get_actor_by_dis(omega, -2).pos - omega.update().pos).y)
        POINT = [glm.vec3(0,0,-14), # THD顺序的点位，有需求自己修改
                 glm.vec3(0,0,-14),
                 glm.vec3(-9.3,0,4.3),
                 glm.vec3(9.3,0,4.3),
                 glm.vec3(-4,0,9.5),
                 glm.vec3(4,0,9.5),
                 glm.vec3(-10,0,-2.5),
                 glm.vec3(10,0,-2.5)]
        myself = raid_utils.get_me()
        mypriority = raid_utils.role_key('thd', myself.id)
        mypos = POINT[mypriority] + omega.pos
        raid_utils.draw_circle(radius=1, pos=mypos, duration=15, surface_color=0, line_color=col.green_line)
        raid_utils.draw_line(mypos, myself, width=5, color=col.green_line, duration=15)

Diffuse_Wave_Cannon_Kyrios()
