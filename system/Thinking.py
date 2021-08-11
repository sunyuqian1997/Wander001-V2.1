import random
import http.client
import json
import time

from system.config import CaiYumAI
from entity.StoryTemplate import StoryTemplate


class Thinking(object):
    _story_template = None
    _style = None
    _year = None

    def __init__(self):
        if self._year is None:
            self._year = random.randint(3050, 5090)
        if self._style is None:
            self._style = random.randint(0, 2)
        # 应答过程中使用的故事模板对象
        self._story_template = StoryTemplate(self._year, self._style)

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        self._year = value
        # 更新应答过程中使用的故事模板对象
        self._story_template = StoryTemplate(self._year, self._style)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        # 更新应答过程中使用的故事模板对象
        self._story_template = StoryTemplate(self._year, self._style)

    def say_hello(self, name):
        return "你好呀，" + name + "，" + self.self_introduction()

    def guide(self):
        return "试着对我说，\"我想去：北京南站\"(目前仅限中国大陆内地点。)"

    def self_introduction(self):
        return "我叫Wander，我不是人类，而是一个破旧的女性人形机器人，正在地球上慢慢旅行。现在地球上的人类已经不多了，世界各地或是被机械或陨石毁灭，或是在科技的进步下自由发展。"

    async def describe_scene(self, address):
        # 根据地址生成开头内容
        self._story_template.set_content(address)
        # 拼接内容作为文章素材
        material = self.self_introduction() + self._story_template.content + self._story_template.style_text
        # 使用彩云AI续写
        cai_yum_ai = CaiYumAI()
        # 续写内容
        content = self._story_template.content + "\n" + await self._create_novel(material, cai_yum_ai)

        return content

    async def do_action(self, material):
        # 使用彩云AI续写
        cai_yum_ai = CaiYumAI()
        # 续写内容
        content = await self._create_novel(material, cai_yum_ai)

        return content

    async def _create_novel(self, content, cai_yum_ai):
        """
        创建文章
        :param CaiYumAI cai_yum_ai: 彩云ai
        :return:
        """
        title = "科幻小说：机械纪元回忆录"
        conn = http.client.HTTPConnection(cai_yum_ai.host)
        payload = json.dumps({
            "content": content,
            "title": title,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", cai_yum_ai.create_url, payload, headers)

        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        data = json.loads(data)
        data = data.get("data")
        nid = data.get("nid")

        return await self._write_novel(content, title, nid, cai_yum_ai)

    async def _write_novel(self, content, title, nid, cai_yum_ai):
        """
        续写文章
        :param string content: 素材
        :param string title: 标题
        :param string nid:
        :param CaiYumAI cai_yum_ai: 彩云ai对象
        :return:
        """
        conn = http.client.HTTPConnection(cai_yum_ai.host)
        payload = json.dumps({
            "content": content,
            "title": title,
            "mid": cai_yum_ai.mid,
            "nid": nid
        })
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", cai_yum_ai.write_url, payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        data = json.loads(data)

        if data.get("status") != 0:
            # 表示续写失败
            raise Exception(10004)
        # 接收续写
        xid = data.get("data").get("xid")

        return await self._dream_loop(xid, nid, cai_yum_ai)

    async def _dream_loop(self, xid, nid, cai_yum_ai):
        conn = http.client.HTTPConnection(cai_yum_ai.host)
        payload = json.dumps({
            "xid": xid,
            "nid": nid
        })
        headers = {
            'Content-Type': 'application/json'
        }

        while True:
            time.sleep(1)
            conn.request("POST", cai_yum_ai.dream_loop_url, payload, headers)
            res = conn.getresponse()
            data = res.read()
            data = data.decode("utf-8")
            data = json.loads(data)
            data = data.get("data")
            # 续写平均在8秒左右
            if data.get("count") == 0:
                content = data.get("rows").pop().get("content")
                content = content + '……'

                return content
            else:
                print(data)