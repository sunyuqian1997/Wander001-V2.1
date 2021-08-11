from system.Command import Command
from system.Position import Position
from system.RobotImage import RobotImage
from system.Thinking import Thinking
from system.Storage import Storage


class Wander(object):
    _thinking = False
    _positioning_system = False
    _image_system = False
    _storage_system = False
    _command_system = False

    _message = ""
    _location = ""

    def __init__(self):
        # 初始化Wander
        # 1、初始化思维系统
        self._thinking = Thinking()
        # 2、初始化定位系统
        self._positioning_system = Position()
        # 3、初始化图像系统
        self._image_system = RobotImage()
        # 4、初始化存储系统
        self._storage_system = Storage()
        # 5、初始化听觉系统
        self._command_system = Command()

    @property
    def thinking(self):
        if not self._thinking:
            raise Exception("思维系统已失效，正在修复中……\n……说……说不出话了……怎么办……")

        return self._thinking

    @thinking.setter
    def thinking(self, thinking):
        self._thinking = thinking

    @property
    def positioning_system(self):
        if not self._positioning_system:
            raise Exception("时空定位系统暂时失效，正在维修……\n怎么又坏了呀！老式飞行器果然不好使吗？")

        return self._positioning_system

    @positioning_system.setter
    def positioning_system(self, position_system):
        self._positioning_system = position_system

    @property
    def image_system(self):
        if not self._image_system:
            raise Exception("哎？！摄像头坏掉了？这样就看不见了……\n正在尝试修复视觉模组……")

        return self._image_system

    @image_system.setter
    def image_system(self, image_system):
        self._image_system = image_system

    @property
    def storage_system(self):
        if not self._storage_system:
            raise Exception("储存内存失效，无法储存信息……正在修复……")

        return self._storage_system

    @storage_system.setter
    def storage_system(self, storage_system):
        self._storage_system = storage_system

    @property
    def command_system(self):
        if not self._command_system:
            raise Exception("命令识别失效，未能成功解析命令……正在修复……")

        return self._command_system

    @command_system.setter
    def command_system(self, command_system):
        self._command_system = command_system

    # 刚加好友，打招呼的话术
    def say_hello(self, name):
        return self._thinking.say_hello(name)

    # 加完好友，指引对方说出指定指令
    def guide(self):
        return self._thinking.guide()

    # 通过地址获取GPS坐标
    def find_location(self, address):
        if address == "":
            raise Exception("请告诉我您想去哪里")

        return self._positioning_system.find_location(address)

    # 拍摄指定GPS坐标的图片（未来时）
    async def take_photo(self, longitude, latitude, style):
        return await self._image_system.take_photo(longitude, latitude, style)

    # 描述当前场景
    async def describe_scene(self, year, address, style):
        self._thinking.style = style
        self._thinking.year = year

        return await self._thinking.describe_scene(address)

    # 描述当前场景
    async def do_action(self, prompt):
        return await self._thinking.do_action(prompt)


