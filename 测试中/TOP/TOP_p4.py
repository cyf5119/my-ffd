from .utils import *
# 31611 蓝屏 是给人看的读条 4.7s
special_actions[31612] = 0 # 蓝屏 血量打下20%的隐藏的0.7s读条
special_actions[31613] = 0 # 蓝屏 血量高于20%的隐藏的0.7s读条，狂暴

# 步进月环P3里有了，这里不用写了

# 蓝屏 Blue_Screen

class p4:
    state = 0
    last_time = 0
    share_list = []
    spread_point = [glm.vec3(87.65, 0, 94.53), # MTSTD3D4H1H2D1D2
                    glm.vec3(112.32, 0, 94.26),
                    glm.vec3(86.47, 0, 99.94),
                    glm.vec3(113.86, 0, 100.08),
                    glm.vec3(87.50, 0, 105.328),
                    glm.vec3(112.64, 0, 104.973),
                    glm.vec3(90.59, 0, 109.81),
                    glm.vec3(109.65, 0, 109.55)]
    share_point = [glm.vec3(95.89, 0, 113.629), # 左右
                   glm.vec3(104.18, 0, 113.61)]
    priority = The_Omega_Protocol.p4_priority # 此优先级较特殊 先远后近先左后右
    
@top.on_cast(31617) # 读条的波动炮
def start(msg: NetworkMessage[zone_server.ActorCast]):
    p4.state = 3
    p4.share_list = []
    raid_utils.sleep(.1) # 这里不等一下上下两行顺序会串
    wave_cannon_spread()

@top.on_effect(22393) # 分摊点名
def share(msg: NetworkMessage[zone_server.ActionEffect]):
    actor = raid_utils.NActor.by_id(msg.message.target_ids[0])

    # 请不要问我这一坨是什么，我也不知道，我精神状态很好
    if actor.id in p4.share_list: return
    p4.share_list.append(actor.id)
    if len(p4.share_list) == 2:
        if raid_utils.role_key(p4.priority, p4.share_list[0]) >raid_utils.role_key(p4.priority, p4.share_list[1]):
            p4.share_list[0], p4.share_list[1] = p4.share_list[1], p4.share_list[0]
        is_right_list = [0,1,0,1,0,1,0,1] # 是否在右分摊
        idx_list = [raid_utils.role_key(p4.priority, a_id) for a_id in p4.share_list]
        if idx_list[0]%2 == idx_list[1]%2:
            if idx_list[0]%2: # 分摊都在右 D1换更近的分摊
                is_right_list[idx_list[1]], is_right_list[-2] = is_right_list[idx_list[1]], is_right_list[-2]
            else: # 分摊都在左 D2换更近的分摊
                is_right_list[idx_list[1]], is_right_list[-1] = is_right_list[idx_list[1]], is_right_list[-1]
        myself = raid_utils.get_me()
        mypriority = raid_utils.role_key(p4.priority, myself.id)
        mypos = p4.share_point[is_right_list[mypriority]] # 拿自己的位置
        mypos0 = p4.spread_point[mypriority]

        raid_utils.draw_circle(radius=1, pos=mypos, duration=3, surface_color=0, line_color=col.orange_line)
        raid_utils.draw_line(mypos0, mypos, color=col.orange_line, width=5, duration=3)
        raid_utils.sleep(3) # 等待分散完
        raid_utils.draw_circle(radius=1, pos=mypos, duration=5, surface_color=0, line_color=col.green_line)
        raid_utils.draw_line(myself, mypos, color=col.green_line, width=5, duration=5)
        for a_id in p4.share_list:
            wave_cannon_share(a_id)
        p4.share_list = []

@top.on_effect(31615) # 分摊判定
def spread(msg: NetworkMessage[zone_server.ActionEffect]):
    wave_cannon_spread()

def wave_cannon_spread(): # 分散画个矩形
    now = time.time()
    if now - p4.last_time < 1: return
    p4.last_time = now
    if not p4.state: return
    p4.state -= 1
    omega = next(raid_utils.find_actor_by_base_id(15717))
    def play(target: raid_utils.NActor):  
        raid_utils.draw_rect(pos=omega, width=6, length=30,duration=5, line_color=col.purple_line, surface_color=col.purple_surface,
                             facing= lambda _: glm.polar(target.update().pos - omega.update().pos).y)
    for a in raid_utils.iter_main_party(False):
        play(a)
    # 因为 for 会影响 lambda 里面 actor 的值，所以包一个函数

    myself = raid_utils.get_me()
    my_priority = raid_utils.role_key(p4.priority, myself.id)
    my_pos = p4.spread_point[my_priority]
    raid_utils.draw_circle(radius=1, pos=my_pos, duration=5, surface_color=0, line_color=col.green_line)
    raid_utils.draw_line(myself, my_pos, color=col.green_line, width=5, duration=5)

def wave_cannon_share(a_id): # 分摊画个矩形
    actor = raid_utils.NActor.by_id(a_id)
    omega = next(raid_utils.find_actor_by_base_id(15717))
    raid_utils.draw_rect(pos=omega, width=6, length=30, duration=5, line_color=col.yellow_line, surface_color=col.yellow_surface,
                         facing= lambda _: glm.polar(actor.update().pos - omega.update().pos).y)
