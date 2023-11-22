from .utils import *

special_actions[31573] = 0 # 你好，世界
special_actions[31588] = 0 # 严重错误
special_actions[31560] = 0 # 离子流出
special_actions[31583] = 0 # 红塔
special_actions[31584] = 0 # 蓝塔



# 速射式波动炮

class Wave_Repeater:
    def __init__(self):
        self.list = [[],[],[]]
        top.on_reset(self.reset) # 重新开始战斗
        top.on_cast(31567)(self.wave_repeater) # 速射式波动炮 地震
        top.on_add_status(3425)(self.on_add_spread) # 分散buff
        top.on_add_status(3426)(self.on_add_stack) # 分摊buff

        self.cnt = 0
        self.lock = threading.Lock()
        top.on_effect(31561)(self.on_start_p3)
        top.on_actor_play_action_timeline(7747, 7748)(self.on_hand_summon)

    def on_start_p3(self, msg: NetworkMessage[zone_server.ActionEffect]):
        self.cnt = 3
    # 手的这一段是直接从FPT抄的
    def on_hand_summon(self, msg: PlayActionTimelineMessage):
        actor = raid_utils.NActor.by_id(msg.id)
        if (msg.timeline_id == 7747 and actor.base_id == 15719) or (msg.timeline_id == 7748 and actor.base_id == 15718):
            with self.lock:
                if self.cnt:
                    raid_utils.draw_circle(radius=11, pos=actor, duration=13.8)
                    self.cnt -= 1       

    def reset(self):
        self.list = [[],[],[]] # 依次为 分散，分摊，闲人

    def wave_repeater(self, msg:NetworkMessage[zone_server.ActorCast]):
        raid_utils.draw_circle(radius=6, pos=center, duration=5.2) # 31567 钢铁 范围6（毒范围）
        raid_utils.sleep(5.2)
        raid_utils.draw_circle(radius=12, inner_radius=6, pos=center, duration=2) # 31568 月环 范围12 内圈6
        raid_utils.sleep(2)# 相隔 2s
        raid_utils.draw_circle(radius=18, inner_radius=12, pos=center, duration=2) # 31569 月环 范围18 内圈12
        raid_utils.sleep(2)
        raid_utils.draw_circle(radius=24, inner_radius=18, pos=center, duration=2) # 31570 月环 范围24 内圈18
    
    def on_add_spread(self, msg: ActorControlMessage[actor_control.AddStatus]):
        player = raid_utils.NActor.by_id(msg.source_id)
        if player.id in self.list[0]: return
        self.list[0].append(player.id)
        
        if len(self.list[0]) == 4: # 分散列表按优先级排序
            priority = The_Omega_Protocol.p3_Wave_Repeater_priority.value
            self.list[0].sort(key= lambda k: raid_utils.role_key(priority, k))
            logger.debug(f'分散 = {self.list[0]}')
# ！！！一定一定要把 assert_status 放在函数最后，这东西即使不是 if 内的也会卡住函数后面的所有东西直到满足条件才释放！！！
        if raid_utils.assert_status(player, msg.param.status_id, 5): # 分散画圈
            raid_utils.draw_circle(radius=6, pos=player, duration=5, surface_color=0, line_color=col.red_line)

    def on_add_stack(self, msg: ActorControlMessage[actor_control.AddStatus]):
        player = raid_utils.NActor.by_id(msg.source_id)
        if player.id in self.list[1]: return
        self.list[1].append(player.id)
        if len(self.list[1]) == 2: # 分摊列表按优先级
            priority = The_Omega_Protocol.p3_Wave_Repeater_priority.value
            self.list[1].sort(key= lambda k: raid_utils.role_key(priority, k))
            logger.debug(f'分摊 = {self.list[1]}')
            raid_utils.sleep(.1) # 稍微等下
            for a in raid_utils.iter_main_party(False):
                if not (a.status.has_status(3425) or a.status.has_status(3426)) and not a.id in self.list[2]:
                    self.list[2].append(a.id) # 闲人丢进列表按优先级
            self.list[2].sort(key= lambda k: raid_utils.role_key(priority, k))
            logger.debug(f'闲人 = {self.list[2]}')
            myself = raid_utils.get_me() # 自己的指路
            for i in range(3):
                if myself.id in self.list[i]:
                    idx = self.list[i].index(myself.id)
                    if i:
                        pos = glm.rotateY(glm.vec3(-19,0,0), -(idx+1)*math.pi/3) + center
                    else:
                        pos = glm.rotateY(glm.vec3(-19,0,0), idx*math.pi/3) + center
                    raid_utils.draw_circle(radius=1, pos=pos, duration=10, surface_color=0, line_color=col.green_line)
                    raid_utils.draw_line(myself, pos, color=col.green_line, width=5, duration=10)
# ！！！一定一定要把 assert_status 放在函数最后，这东西即使不是 if 内的也会卡住函数后面的所有东西直到满足条件才释放！！！
        if raid_utils.assert_status(player, msg.param.status_id, 5): # 分摊画圈
            raid_utils.draw_circle(radius=6, pos=player, duration=5, surface_color=0, line_color=col.yellow_line)


'''
如果实在实在很闲会加精准的指路（但应该不至于这么闲

23:19:19,983 cast 31567
23:19:25,020 effect 31567
23:19:28,219 cast 31567
23:19:33,142 effect 31567

23:22:39,878 cast 31567
23:22:44,800 effect 31567
23:22:57,403 cast 31567
23:23:02,433 effect 31567

[2023-09-04 18:21:53,745]       [DEBUG] [raid_helper/top]       出现7747
[2023-09-04 18:21:56,855]       [DEBUG] [raid_helper/top]       出现7747
[2023-09-04 18:22:07,528]       [DEBUG] [raid_helper/top]       巨能爆散
[2023-09-04 18:22:10,172]       [DEBUG] [raid_helper/top]       巨能爆散

'''

Wave_Repeater()



# 你好，世界

class Hello_World:
    def __init__(self):
        self.state = 0 # 阶段
        self.isred = 0 # 大圈是否为红
        self.near_time = 0 # 处理近线的轮次
        self.tower_id = [] # 存塔id
        top.on_reset(lambda _: setattr(self, 'state', 0)) # 重设
        top.on_cast(31593)(self.start) # 读条 你好，世界
        top.on_add_status(3437)(self.overflow) # 代码异味：上溢 大圈预备
        top.on_add_status(3526, 3429)(self.critical_bug_rot) # 处理红蓝毒
        top.on_add_status(3524, 3525)(self.critical_bug_circle) # 处理大圈分摊
        top.on_cast(31583,31584)(self.tower_cast) # 塔咏唱的东西

    def start(self, msg:NetworkMessage[zone_server.ActorCast]):
        self.state = 4 # 初始化
        self.isred = 0
        self.near_time = 0
        self.tower_id = []

    def overflow(self, msg: ActorControlMessage[actor_control.AddStatus]):
        actor = raid_utils.NActor.by_id(msg.source_id)
        raid_utils.sleep(.5) # 等待buff上全了
        if actor.status.has_status(3438): # 3438 代码异味：下溢 红毒预备
            self.isred = 1
        # 3439 代码异味：性能 蓝毒预备

        myself = raid_utils.get_me()
        raid_utils.sleep(.5)
        # 3441 代码异味：远
        self.near_time = (myself.status.find_status_remain(status_id = 3503) + 5) // 21 # 差值是21，加5提供反应时间
        # 3503 代码异味：近
        if self.near_time % 2 == 0 : # 因为后面的处理方法 所以这里这样子
            self.near_time += 2
    
    def critical_bug_rot(self, msg: ActorControlMessage[actor_control.AddStatus]):
        actor = raid_utils.NActor.by_id(msg.source_id)
        if msg.param.status_id == 3526: # 红毒
            rot_surface_color, rot_line_color = col.red_surface, col.red_line
        elif msg.param.status_id == 3429: # 蓝毒
            rot_surface_color, rot_line_color = col.blue_surface, col.blue_line
        raid_utils.draw_circle(radius=0.5, pos=actor, duration=24, surface_color=rot_surface_color, line_color=rot_line_color)
        if raid_utils.assert_status(actor, msg.param.status_id, 5): # 先画个小圈，剩5秒画个中圈
            raid_utils.draw_circle(radius=5, pos=actor, duration=5, surface_color=rot_surface_color, line_color=rot_line_color)

    def critical_bug_circle(self, msg: ActorControlMessage[actor_control.AddStatus]):
        actor = raid_utils.NActor.by_id(msg.source_id)
# ！！！一定一定要把 assert_status 放在函数最后，这东西即使不是 if 内的也会卡住函数后面的所有东西直到满足条件才释放！！！
# 这样子两个不会互卡
        if raid_utils.assert_status(actor, 3524, 5): # 分摊画圈
            raid_utils.draw_circle(radius=6, pos=actor, duration=5, surface_color=0, line_color=col.yellow_line)
        elif raid_utils.assert_status(actor, 3525, 5): # 大圈画圈
            raid_utils.draw_circle(radius=20, pos=actor, duration=5, surface_color=0, line_color=col.yellow_line)

    def tower_cast(self, msg: NetworkMessage[zone_server.ActorCast]):
        tower_id = msg.header.source_id
        if not self.isred: share_tower_action_id = 31583 # 红塔咏唱的
        else: share_tower_action_id = 31584 # 蓝塔咏唱的

        if msg.message.action_id == share_tower_action_id:
            if tower_id in self.tower_id: return
            self.tower_id.append(tower_id)
            if len(self.tower_id) == 2: # 以分摊塔的坐标来求基准坐标
                self.state -= 1
                raid_utils.NActor.by_id(self.tower_id[0]).pos
                i = (raid_utils.NActor.by_id(self.tower_id[0]).pos + raid_utils.NActor.by_id(self.tower_id[1]).pos) / 2 - center
                raid_utils.sleep(.1)
                self.guide(i)
                self.tower_id = []

    def guide(self, i: glm.vec3): # 通过上面求出的基准坐标来指路
        myself = raid_utils.get_me()
        if self.isred:
            daquan_tower_color = col.red_line
            fentan_tower_color = col.blue_line
        else:
            daquan_tower_color = col.blue_line
            fentan_tower_color = col.red_line

        match (self.near_time - self.state + 4) % 4:
            case 0 : # 分摊连线
                pos_ = [glm.rotateY(i, math.pi/10)*1.2 + center, glm.rotateY(i, -math.pi/10)*1.2 + center]
                for p in pos_:
                    raid_utils.draw_line(myself, target=p, width=5, duration=10, color=col.lightblue_line)
                    raid_utils.draw_circle(radius=1, pos=p, duration=10, surface_color=0, line_color=col.lightblue_line)
            case 1 : # 分摊塔连线
                pos_ = [glm.rotateY(i, math.pi/7.2)*1.2 + center, glm.rotateY(i, -math.pi/7.2)*1.2 + center]
                for p in pos_:
                    raid_utils.draw_line(myself, target=p, width=5, duration=10, color=fentan_tower_color)
                    raid_utils.draw_circle(radius=1, pos=p, duration=10, surface_color=0, line_color=fentan_tower_color)
            case 2 :
                if not self.state: # 分摊连线
                    pos_ = [glm.rotateY(i, math.pi/10)*1.2 + center, glm.rotateY(i, -math.pi/10)*1.2 + center]
                else: # 吃大圈连线
                    pos_ = [glm.rotateY(i, math.pi/1.65)*1.68 + center, glm.rotateY(i, -math.pi/1.65)*1.68 + center]
                for p in pos_:
                    raid_utils.draw_line(myself, target=p, width=5, duration=10, color=col.green_line)
                    raid_utils.draw_circle(radius=1, pos=p, duration=10, surface_color=0, line_color=col.green_line)
            case 3 : # 大圈连线
                pos_ = [glm.rotateY(i, math.pi/1.33)*1.8 + center, glm.rotateY(i, -math.pi/1.33)*1.8 + center]
                for p in pos_:
                    raid_utils.draw_line(myself, target=p, width=5, duration=10, color=daquan_tower_color)
                    raid_utils.draw_circle(radius=1, pos=p, duration=10, surface_color=0, line_color=daquan_tower_color)

'''
不知道有没有必要加上接谁的毒的连线
以及同buff人的位置的提示
'''

Hello_World()



# 探测式波动炮

WAVE_CANNON_LEFT = [center+glm.vec3(7,0,-17),
                    center+glm.vec3(-14,0,-6),
                    center+glm.vec3(-14,0,6),
                    center+glm.vec3(1.5,0,-9.5),
                    center+glm.vec3(9.5,0,0),
                    center+glm.vec3(18.5,0,0),
                    center+glm.vec3(1.5,0,9.5),
                    center+glm.vec3(1.5,0,18.5)]
WAVE_CANNON_RIGHT = [center+glm.vec3(-7,0,-17),
                     center+glm.vec3(-14,0,-6),
                     center+glm.vec3(-14,0,6),
                     center+glm.vec3(-1.5,0,-9.5),
                     center+glm.vec3(9.5,0,0),
                     center+glm.vec3(18.5,0,0),
                     center+glm.vec3(-1.5,0,9.5),
                     center+glm.vec3(-1.5,0,18.5)]

class Oversampled_Wave_Cannon:
    def __init__(self):
        self.state = 0 # 似乎没啥用？
        self.last_run_time = 0
        self.label_text = ['锁链1','锁链2','锁链3','攻击1','攻击2','攻击3','攻击4','攻击5']
        # 上面面坐标按照这个顺序来
        top.on_cast(31595, 31596)(self.casting)

    def casting(self, msg:NetworkMessage[zone_server.ActorCast]):
        now = time.time()
        if now - self.last_run_time < 3: return
        self.last_run_time = now # 总有莫名的重复触发
        if msg.message.action_id == 31596: # 左刀
            player_pos = WAVE_CANNON_LEFT
            raid_utils.draw_rect(width=50, length=25, pos=msg.message.pos, facing=-math.pi/2, duration=msg.message.cast_time, 
                                 surface_color=col.lightblue_surface, line_color=col.lightblue_line)
        elif msg.message.action_id == 31595: # 右刀
            player_pos = WAVE_CANNON_RIGHT
            raid_utils.draw_rect(width=50, length=25, pos=msg.message.pos, facing=math.pi/2, duration=msg.message.cast_time,
                                 surface_color=col.lightblue_surface, line_color=col.lightblue_line)
        
        dianshi, xianren = 0, 3
        # 搓个朝北的箭头，点0和其余点连线即可
        arrow = [glm.vec3(0,0,-2.5),
                 glm.vec3(0,0,0),
                 glm.vec3(-1,0,-1.5),
                 glm.vec3(1,0,-1.5)]
        arrow1 = [] # 拿来装旋转后的箭头的

        myself = raid_utils.get_me()
        priority = The_Omega_Protocol.p3_Oversampled_Wave_Cannon_priority.value
        for a in raid_utils.iter_main_party(False): # 优先级判断
            if raid_utils.role_key(priority, myself.id) > raid_utils.role_key(priority, a.id):
                if a.status.has_status(3452) or a.status.has_status(3453) :
                    dianshi += 1
                else:
                    xianren += 1
        if myself.status.has_status(3452) or myself.status.has_status(3453):
            # 3453 探测式波动炮 左 buff, 3452 探测式波动炮 右 buff
            raid_utils.draw_line(myself, target=player_pos[dianshi], width=5, duration=10, color=col.green_line)
            raid_utils.draw_circle(radius=1, pos=player_pos[dianshi], duration=10, surface_color=0, line_color=col.green_line)
            if dianshi == 0:
                for i in range(4):
                    arrow1.append(glm.rotateY(arrow[i], math.pi * ((msg.message.action_id == 31595) + myself.status.has_status(3453))))
            elif dianshi == 1:
                for i in range(4):
                    arrow1.append(glm.rotateY(arrow[i], math.pi * (myself.status.has_status(3453)+0.5)))
            elif dianshi == 2:
                for i in range(4):
                    arrow1.append(glm.rotateY(arrow[i], math.pi * (myself.status.has_status(3453)-0.5)))
            for i in range(4):
                raid_utils.draw_line(arrow1[0]+player_pos[dianshi], player_pos[i]+player_pos[dianshi], width=5, duration=10, color=col.green_line)
            # 电视画圈连线画箭头
        else:
            raid_utils.draw_line(myself, target=player_pos[xianren], width=5, duration=10, color=col.green_line)
            raid_utils.draw_circle(radius=1, pos=player_pos[xianren], duration=10, surface_color=0, line_color=col.green_line)
            # 闲人只画圈连线
        
        raid_utils.sleep(msg.message.cast_time - 5)
        for a in raid_utils.iter_main_party(False): # 分摊画圈
            raid_utils.draw_circle(radius=7, pos=a, duration=5, surface_color=0, line_color=col.red_line)

Oversampled_Wave_Cannon()
