import logging
import glm

from raid_helper import utils as raid_utils
from raid_helper.utils.typing import *
from raid_helper.data import special_actions

special_actions[33344] = raid_utils.fan_shape(180) # 老一半场刀
special_actions[33354] = raid_utils.fan_shape(180) # 老三半场刀
special_actions[33348] = raid_utils.fan_shape(120) # 老三触手扇形
special_actions[33355] = raid_utils.donut_shape(20, 26) # 灵动之眼，月环
special_actions[34551] = raid_utils.fan_shape(120) # 老三半场刀与触手组合技

dg = raid_utils.MapTrigger(1126)
logger = logging.getLogger('raid_helper/aetherfont')

is_enable = dg.add_value(raid_utils.BoolCheckBox('default/enable', True))