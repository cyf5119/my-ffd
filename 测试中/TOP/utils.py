import logging
import glm
import math
import threading
import time

from raid_helper import utils as raid_utils
from raid_helper.utils.typing import *
from raid_helper.data import special_actions
from raid_helper.data import omen_color

top = raid_utils.MapTrigger(1122)
center = glm.vec3(100, 0, 100)
logger = logging.getLogger('raid_helper/top')

class col():
    red_line = glm.vec4(1, .2, .2, .8)
    red_surface = glm.vec4(1, .6, .6, .2)
    green_line = glm.vec4(.2, 1, .2, .8)
    green_surface = glm.vec4(.6, 1, .6, .2)
    blue_line = glm.vec4(.2, .2, 1, .8)
    blue_surface = glm.vec4(.6, .6, 1, .2)

    lightblue_line = glm.vec4(.2, 1, 1, .8)
    lightblue_surface = glm.vec4(.6, 1, 1, .2)
    purple_line = glm.vec4(1, .2, 1, .8)
    purple_surface = glm.vec4(1, .6, 1, .2)
    yellow_line = glm.vec4(1, 1, .2, .8)
    yellow_surface = glm.vec4(1, 1, .6, .2)

    orange_line = glm.vec4(1, .6, .2, .8)
    orange_surface = glm.vec4(1, .8, .6, .2)

class The_Omega_Protocol():

    p1_Program_Loop_priority = top.add_value(raid_utils.Select(
        '绝欧米茄/优先级设置/P1-循环程序', [('HTDH', 'h1mtstd1d2d3d4h2'),('THD', 'mtsth1h2d1d2d3d4'),], 'h1mtstd1d2d3d4h2'))
#    p1_Pantokrator_priority = top.add_value(raid_utils.Select( # 这个目前还没屁用，先写上再说
#        '绝欧米茄/优先级设置/P1-全能之主', [('HTDH', 'h1mtstd1d2d3d4h2'),('THD', 'mtsth1h2d1d2d3d4'),], 'h1mtstd1d2d3d4h2'))
    p2_Party_Synergy_priority = top.add_value(raid_utils.Select(
        '绝欧米茄/优先级设置/P2-一运', [('HTDH', 'h1mtstd1d2d3d4h2'),('THD', 'mtsth1h2d1d2d3d4'),], 'h1mtstd1d2d3d4h2'))
    p3_Wave_Repeater_priority = top.add_value(raid_utils.Select(
        '绝欧米茄/优先级设置/P2.5-速射式波动炮', [('HTDH', 'h1mtstd1d2d3d4h2'),('THD', 'mtsth1h2d1d2d3d4'),], 'h1mtstd1d2d3d4h2'))
    p3_Oversampled_Wave_Cannon_priority = top.add_value(raid_utils.Select(
        '绝欧米茄/优先级设置/P3-探测式波动炮', [('HTDH', 'h1mtstd1d2d3d4h2'),('THD', 'mtsth1h2d1d2d3d4'),], 'h1mtstd1d2d3d4h2'))
    p4_priority = top.add_value(raid_utils.Select(
        '绝欧米茄/优先级设置/P4-由远到近', [('坦克远程奶妈近战', 'mtstd3d4h1h2d1d2'),('坦克远程近战奶妈', 'mtstd3d4d1d2h1h2'),], 'mtstd3d4h1h2d1d2'))
