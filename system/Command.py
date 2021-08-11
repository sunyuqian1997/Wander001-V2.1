import time

from wechaty import (
    Message,
    Contact
)

from entity.Session import Session


class Command(object):
    CMD_TRAVEL = "travel"
    CMD_ACTION = "action"
    CMD_SELF = "self"
    CMD_NONE = None

    @staticmethod
    def parse(input_command: Message):
        """
        输出识别的指令内容
        :param input_command: 接收到的指令，如果是自己发的
        :return: 返回指令识别结果
        """
        # 自己发出的指令，则返回self跟False
        if input_command.is_self():
            return Command.CMD_SELF, False

        # 兼容一下中英文冒号(: and ：)，将文本中的冒号统一替换成半角冒号:
        msg_text = input_command.text().replace("：", ":")
        # "我想去"是旅行指令
        if "我想去:" in msg_text:
            address = msg_text.replace("我想去:", "")
            return Command.CMD_TRAVEL, address
        # ”行动“是继续旅行指令
        elif "行动:" in msg_text:
            action = msg_text.replace("行动:", "")
            return Command.CMD_ACTION, action
        # 其他指令则不识别
        return Command.CMD_NONE, None
