from urllib.parse import quote


class Baidu(object):
    _web_ak = "" # 百度有效ak

    _host = "https://api.map.baidu.com"

    _geocoding_url = ""
    _panorama_url = ""

    @property
    def geocoding_url(self):
        return self._geocoding_url

    def set_geocoding_url(self, address):
        self._geocoding_url = self._host + "/geocoding/v3/?output=json&ak=" + self._web_ak + "&address=" + quote(address)

    @property
    def panorama_url(self):
        return self._panorama_url

    def set_panorama_url(self, location_str):
        self._panorama_url = self._host + "/panorama/v2?&width=1024&height=512&fov=180&ak=" + self._web_ak + "&location=" + location_str


class CaiYumAI(object):
    _token = "" # 彩云小梦有效token
    _mid = "" # 彩云小梦有效mid
    _host = "writter.ai"
    _version = "v1"

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def host(self):
        return self._host

    @property
    def mid(self):
        return self._mid

    @property
    def create_url(self):
        if self._version == "v1":
            return "/v1/dream/" + self._token + "/novel_save"
        else:
            raise Exception("暂未支持其他版本的api")

    @property
    def write_url(self):
        if self._version == "v1":
            return "/v1/dream/" + self._token + "/novel_ai"
        else:
            raise Exception("暂未支持其他版本的api")

    @property
    def dream_loop_url(self):
        if self._version == "v1":
            return "/v1/dream/" + self._token + "/novel_dream_loop"
        else:
            raise Exception("暂未支持其他版本的api")
