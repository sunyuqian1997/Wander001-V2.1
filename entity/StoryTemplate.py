import random


class StoryTemplate(object):
    _year = False
    _style = False
    _content = ""

    def __init__(self, year=False, style=False):
        if not year:
            self._year = random.randint(3050, 5090)
        elif year not in range(3050, 5091):
            raise Exception("年份范围是3050~5090")
        else:
            self._year = year

        if not style:
            self._style = random.randint(0, 2)
        elif style not in range(0, 3):
            raise Exception("故事类型范围是0~2")
        else:
            self._style = style

    @property
    def content(self):
        return self._content

    def set_content(self, address):
        self._content = "这里是" + str(self._year) + "年的" + address + "。我启动环境感知模组，飞行器缓缓降落。"

    @property
    def style_text(self):
        if self._style == 0:
            return "我被废墟包围着。环顾四周，这里空无一人，空气中弥漫着夹杂着金属粒的尘土。"
        elif self._style == 1:
            return "计算模组显示，在辐射的影响下，景色变得色彩斑斓。"
        else:
            return "这里的植物异常茂盛，枝叶如同外星生物一般将建筑物环绕，形成了奇异的景色。"
