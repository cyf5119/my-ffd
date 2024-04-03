import logging
import glm
import enum
import typing

from raid_helper import utils as raid_utils
from raid_helper.utils.typing import *
from raid_helper.data import special_actions, omen_color, delay_until

tea = raid_utils.MapTrigger.get(887)

center = glm.vec3(100, 0, 100)

logger = logging.getLogger('raid_helper/tea')

is_enable = tea.add_value(raid_utils.BoolCheckBox('总开关/启用', True))
tea.decorators.append(lambda f: (lambda *args, **kwargs: f(*args, **kwargs) if is_enable.value else None))


class Colors(enum.Enum):
    red = glm.vec3(1, .2, .2)
    green = glm.vec3(.2, 1, .2)
    blue = glm.vec3(.2, .2, 1)

    cyan = glm.vec3(.2, 1, 1)
    violet = glm.vec3(1, .2, 1)
    yellow = glm.vec3(1, 1, .2)

    orange = glm.vec3(1, .6, .2)
    pink = glm.vec3(1, .2, .6)
    grass = glm.vec3(.6, 1, .2)
    spring = glm.vec3(.2, 1, .6)
    purple = glm.vec3(.6, .2, 1)
    lake = glm.vec3(.2, .6, 1)

    @property
    def surface(self):
        return glm.vec4(self.value.x/2 + 0.5, self.value.y/2 + 0.5, self.value.z/2 + 0.5, 0.2)

    @property
    def line(self):
        return glm.vec4(self.value.x, self.value.y, self.value.z, 0.8)

    @property
    def color(self):
        return glm.vec4(self.value.x, self.value.y, self.value.z, 0.5)

