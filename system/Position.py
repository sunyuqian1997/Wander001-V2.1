# -*- coding: utf-8 -*-
import urllib.request
from system.config import Baidu


class Position(object):
    def find_location(self, address) -> dict:
        baidu = Baidu()
        baidu.set_geocoding_url(address)  # 根据位置，配置查询GPS坐标的地址
        # 根据地址构建请求对象
        request = urllib.request.Request(baidu.geocoding_url)
        with urllib.request.urlopen(request) as response:
            res = eval(str(response.read(), encoding="utf-8"))

        if res["status"] != 0:
            # 10001表示获取坐标失败
            raise Exception(10001)
        else:
            return res["result"]["location"]
