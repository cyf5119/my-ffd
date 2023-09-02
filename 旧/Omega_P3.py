
import logging
import glm

from raid_helper import utils as raid_utils
from raid_helper.utils.typing import *
from raid_helper.data import special_actions

omega_p3 = raid_utils.MapTrigger(1122)
center = glm.vec3(100, 0, 100)
logger = logging.getLogger('raid_helper/omega_p3')
yxj = omega_p3.add_value(raid_utils.BoolCheckBox('绝欧P3/先勾再进本设位置', False))

# 零基础土制画图

special_actions[31573] = 0 # 你好，世界
special_actions[31588] = 0 # 严重错误
special_actions[31560] = 0 # 离子流出
special_actions[31583] = 0 # 红塔
special_actions[31584] = 0 # 蓝塔

youxianji = raid_utils.make_role_rule('h1mtstd1d2d3d4h2')
    # HTDH 0-7 优先级定义
class hw:
    wrong_time = 0 # 严重错误计数器
    daquan = 0 # 谁是大圈
    near_time = 0 # 我第几次近线
    jizhun = 0 # 用来当基准向量的
    t_pos = []
# P2.5

@omega_p3.on_cast(31567)
def bujinquan(evt: NetworkMessage[zone_server.ActorCast]):
    # 速射式波动炮
    myself = raid_utils.main.mem.actor_table.me
    if yxj :
        fensan = 0
        fentan = 1
        xianren = 1
        fangwuchu = 0 # 防止在P4触发
        pos = glm.vec3(-19,0,0)
        for a in raid_utils.iter_main_party(False):
            if a.status.has_status(3425) :
                fangwuchu = 1
            if raid_utils.role_key(youxianji,myself.id) > raid_utils.role_key(youxianji,a.id):
                if a.status.has_status(3425) : # 狙击式波动炮，分散
                    fensan += 1
                elif a.status.has_status(3426) : # 狙击式大功率波动炮，分摊
                    fentan += 1
                else :
                    xianren += 1
        if fangwuchu :
            if myself.status.has_status(3425) :
                pos1 = glm.rotateY(pos,glm.radians(60)*fensan)+center
                raid_utils.draw_line(myself,pos1,color=glm.vec4(.5, 1, 0, .8),width=5,duration=5)
            elif myself.status.has_status(3426) :
                pos1 = glm.rotateY(pos,glm.radians(60)*fentan*-1)+center
                raid_utils.draw_line(myself,pos1,color=glm.vec4(.5, 1, 0, .8),width=5,duration=5)
            else :
                pos1 = glm.rotateY(pos,glm.radians(60)*xianren*-1)+center
                raid_utils.draw_line(myself,pos1,color=glm.vec4(.5, 1, 0, .8),width=5,duration=5)
                # 画个连线指方位

    raid_utils.draw_circle(radius=6, pos=center, duration=5.2)
    raid_utils.sleep(5.2)
    raid_utils.draw_circle(radius=12,inner_radius=6,pos=center,duration=2)
    raid_utils.sleep(2)
    raid_utils.draw_circle(radius=18,inner_radius=12,pos=center,duration=2)
    raid_utils.sleep(2)
    raid_utils.draw_circle(radius=24,inner_radius=18,pos=center,duration=2)
    # 步进月环 P4 也会触发出来
# P3

# @omega_p3.on_cast(31593)
# def on_cast_hello_world(msg:NetworkMessage[zone_server.ActorCast]): 
#     # 读条 你好，世界

@omega_p3.on_add_status(3437)
def on_add_daquan_yubei(evt: 'ActorControlMessage[actor_control.AddStatus]'):
    # 上buff 代码异味：上溢  这里进行HW的初始化
    myself = raid_utils.main.mem.actor_table.me
    hw.wrong_time = 0
    hw.jizhun = 0
    hw.daquan = 0
    hw.t_pos = []

    # 判断大圈
    if (raid_utils.NActor.by_id(evt.source_id)).status.has_status(status_id=3438):
        hw.daquan = 'red' #3438 红毒预备 代码异味：下溢
    elif (raid_utils.NActor.by_id(evt.source_id)).status.has_status(status_id=3439):
        hw.daquan = 'blue' #3439 蓝毒预备 Performance Code Smell
    
    raid_utils.sleep(1)
    # 判断远近线轮次
    # hw.far_time = (myself.status.find_status_remain(status_id=3441)+5)//21
    # 远线轮次 代码异味：远
    hw.near_time = (myself.status.find_status_remain(status_id=3503)+5)//21
    # 近线轮次 代码异味：近
    if hw.near_time % 2 == 0 :
        hw.near_time += 2

@omega_p3.on_add_status(3526,3429)
def p3_draw_rots(evt: 'ActorControlMessage[actor_control.AddStatus]'):
    actor = raid_utils.NActor.by_id(evt.source_id)
    if evt.param.status_id == 3526: # 红毒
        rot_color = glm.vec4(1,.6,.6,.7)
        rot_line_color = glm.vec4(1,.2,.2,.9)
    elif evt.param.status_id == 3429: # 蓝毒
        rot_color = glm.vec4(.6,.6,1,.7)
        rot_line_color = glm.vec4(.2,.2,1,.9)

    raid_utils.draw_circle(radius=0.5, pos=actor, duration=24, color=rot_line_color, line_color=0)
    # 标带毒
    if raid_utils.assert_status(actor, evt.param.status_id, 3):
        raid_utils.draw_circle(radius=5, pos=actor, duration=3, color=rot_color, line_color=rot_line_color)
        # 画炸毒

@omega_p3.on_add_status(3524)
def p3_draw_tan(evt: 'ActorControlMessage[actor_control.AddStatus]'):
    actor = raid_utils.NActor.by_id(evt.source_id) # 分摊画圈
    if raid_utils.assert_status(actor, evt.param.status_id, 5):
        raid_utils.draw_circle(radius=6, pos=actor, duration=5)
        
@omega_p3.on_add_status(3525)
def p3_draw_quan(evt: 'ActorControlMessage[actor_control.AddStatus]'):
    actor = raid_utils.NActor.by_id(evt.source_id) # 大圈画圈
    if raid_utils.assert_status(actor, evt.param.status_id, 5):
        raid_utils.draw_circle(radius=20, pos=actor, duration=5)
        
@omega_p3.on_add_status(3530)
def p3_hw_0(evt: 'ActorControlMessage[actor_control.AddStatus]'):
    # 回归方程：远 没记错应该是吃分摊的
    hw.t_pos = []

# HW
@omega_p3.on_cast(31583,31584)
def p3_line_towers(evt: NetworkMessage[zone_server.ActorCast]):
    tower_pos = glm.vec3(evt.message.pos.x, evt.message.pos.y, evt.message.pos.z)
    myself = raid_utils.main.mem.actor_table.me
    if evt.message.action_id == 31583: # 红塔
        tower_color = 'red'
        tower_color_vec1 = glm.vec4(1, 0, 0, .8)
        tower_color_vec2 = glm.vec4(0, 0, 1, .8)
    elif evt.message.action_id == 31584: # 蓝塔
        tower_color = 'blue'
        tower_color_vec1 = glm.vec4(0, 0, 1, .8)
        tower_color_vec2 = glm.vec4(1, 0, 0, .8)
    if tower_color != hw.daquan :
        if tower_pos in hw.t_pos :
            return
        hw.t_pos.append(tower_pos)
        if len(hw.t_pos) == 2:
            hw.wrong_time += 1
            hw.jizhun = (hw.t_pos[0] + hw.t_pos[1] - 2 * center) / 2
            # 计算基准向量
            match (hw.near_time + hw.wrong_time) % 4 :
                case 0 : # 分摊连线
                    pos1 = glm.rotateY(hw.jizhun,3.1416/9.2)*1.2+center
                    pos2 = glm.rotateY(hw.jizhun,-3.1416/9.2)*1.2+center
                    raid_utils.draw_line(myself, target=pos1, width=5, duration=10, color=glm.vec4(0, 1, 1, .8))
                    raid_utils.draw_line(myself, target=pos2, width=5, duration=10, color=glm.vec4(0, 1, 1, .8))
                case 1 : # 分摊塔连线
                    pos1 = glm.rotateY(hw.jizhun,3.1416/7.2)*1.2+center
                    pos2 = glm.rotateY(hw.jizhun,-3.1416/7.2)*1.2+center
                    raid_utils.draw_line(myself, target = pos1, width = 5, duration = 10, color = tower_color_vec1)
                    raid_utils.draw_line(myself, target = pos2, width = 5, duration = 10, color = tower_color_vec1)
                case 2 :
                    if hw.wrong_time == 4 : # 分摊连线
                        pos1 = glm.rotateY(hw.jizhun,3.1416/9.2)*1.2+center
                        pos2 = glm.rotateY(hw.jizhun,-3.1416/9.2)*1.2+center
                        raid_utils.draw_line(myself, target=pos1, width=5, duration=10, color=glm.vec4(0, 1, 1, .8))
                        raid_utils.draw_line(myself, target=pos2, width=5, duration=10, color=glm.vec4(0, 1, 1, .8))
                    else : # 吃大圈连线
                        pos1 = glm.rotateY(hw.jizhun,3.1416/1.65)*1.8+center
                        pos2 = glm.rotateY(hw.jizhun,-3.1416/1.65)*1.8+center
                        raid_utils.draw_line(myself, target=pos1, width=5, duration=10, color=glm.vec4(.5, 1, 0, .8))
                        raid_utils.draw_line(myself, target=pos2, width=5, duration=10, color=glm.vec4(.5, 1, 0, .8))
                case 3 : # 大圈连线
                    pos1 = glm.rotateY(hw.jizhun,3.1416*0.75)*1.8+center
                    pos2 = glm.rotateY(hw.jizhun,-3.1416*0.75)*1.8+center
                    raid_utils.draw_line(myself, target=pos1, width=5, duration=10, color=tower_color_vec2)
                    raid_utils.draw_line(myself, target=pos2, width=5, duration=10, color=tower_color_vec2)
                
#@omega_p3.on_cast(31599)
#def on_cast_qianzaicuowu(msg: NetworkMessage[zone_server.ActorCast]):
#    # 潜在错误

# 日基脑死固定小电视
# 探测式波动炮
@omega_p3.on_cast(31596,31595)
def on_cast_p3xiaodianshi(msg:NetworkMessage[zone_server.ActorCast]):
    myself = raid_utils.main.mem.actor_table.me
    biaoqian = ['锁链1','锁链2','锁链3','攻击1','攻击2','攻击3','攻击4','攻击5']
    # 下面的坐标是按照这个顺序的
    l_c = glm.vec4(.2, 1, .2, .7)
    if msg.message.action_id == 31596: # 左刀
        weizhi = [center+glm.vec3(6,0,-18),
                  center+glm.vec3(-13,0,-6),
                  center+glm.vec3(-13,0,6),
                  center+glm.vec3(1.5,0,-10),
                  center+glm.vec3(10,0,0),
                  center+glm.vec3(19,0,0),
                  center+glm.vec3(1.5,0,10),
                  center+glm.vec3(1.5,0,18.5)]
    elif msg.message.action_id == 31595: # 右刀
        weizhi = [center+glm.vec3(-6,0,-18),
                  center+glm.vec3(-13,0,-6),
                  center+glm.vec3(-13,0,6),
                  center+glm.vec3(-1.5,0,-10),
                  center+glm.vec3(10,0,0),
                  center+glm.vec3(19,0,0),
                  center+glm.vec3(-1.5,0,10),
                  center+glm.vec3(-1.5,0,18.5)]
    if yxj :
        dianshi = 0
        xianren = 3 # 电视在前闲人在后
        # 搓个朝北的箭头，点0和其余点连线即可
        point = [glm.vec3(0,0,-2.5),
                 glm.vec3(0,0,0),
                 glm.vec3(-1,0,-1.5),
                 glm.vec3(1,0,-1.5)]
        point1 = [] # 拿来装旋转后的箭头的
        for a in raid_utils.iter_main_party(False): # 优先级判断
            if raid_utils.role_key(youxianji,myself.id) > raid_utils.role_key(youxianji,a.id):
                if a.status.has_status(3452) or a.status.has_status(3453) :
                    dianshi += 1
                else:
                    xianren += 1
        if myself.status.has_status(3452) or myself.status.has_status(3453):
            # 3453 探测式波动炮 左 buff, 3452 探测式波动炮 右 buff
            raid_utils.draw_line(myself, target=weizhi[dianshi], width=5, duration=10, color=glm.vec4(.5, 1, 0, .8))
            raid_utils.draw_circle(radius=1, pos=weizhi[dianshi], duration=10)
            if dianshi == 0:
                for i in range(4):
                    point1.append(glm.rotateY(point[i], glm.radians(180) * ((msg.message.action_id == 31595) + myself.status.has_status(3453))))
            elif dianshi == 1:
                for i in range(4):
                    point1.append(glm.rotateY(point[i],glm.radians(180) * (myself.status.has_status(3453)+0.5)))
            elif dianshi == 2:
                for i in range(4):
                    point1.append(glm.rotateY(point[i],glm.radians(180) * (myself.status.has_status(3453)-0.5)))
            for i in range(4):
                raid_utils.draw_line(point1[0]+weizhi[dianshi],point1[i]+weizhi[dianshi],width=5,duration=10,color=glm.vec4(1,.2,.2,.8))
            # 电视画圈连线画箭头
        else:
            raid_utils.draw_line(myself, target=weizhi[xianren], width=5, duration=10, color=glm.vec4(.5, 1, 0, .8))
            raid_utils.draw_circle(radius=1, pos=weizhi[xianren], duration=10)
            # 闲人只画圈连线
    else :
        for i in range(0,7):
            raid_utils.draw_circle(radius=1, pos=weizhi[i], label=biaoqian[i], label_color=l_c,duration=10)
            # 没勾优先级就只画所有点位
