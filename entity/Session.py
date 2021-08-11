import time

import redis

from common.redis_pool import redis_pool


class Session(object):
    """
    表示用户的一次会话，以用户talker_id为键，默认session包含四个字段：
    travel_log_id：旅行日志id
    expire_at：会话过期时间
    remain_action_count：剩余执行行动指令的次数

    完整的会话包括一次`travel`指令和若干条`action`指令。
    开始执行`travel`指令时，默认开启一次新的会话，之前的会话状态会被覆盖；
    会话状态以用户(Contact类)的`contact_id`为主键，另包含以下字段：
    1、remain_action_count: 表示剩余行动的次数，为0时，无法继续行动，为-1时不限制
    2、expire_at: 表示当前会话的过期时间，与字段`remain_action_count`共同控制会话的状态，值为时间
    规则：
    1、每次执行完`travel`指令后，会给`remain_action_count`赋值，表示可执行的行动指令次数
    2、当`remain_action_count`大于0，且`expire_at`未到当前时间（即未过期）时，才可执行`action`指令
    3、当`remain_action_count`等于0，或者`expire_at`大于或等于当前时间（即过期）时，无法执行`action`指令
    """
    _cache = redis.StrictRedis(connection_pool=redis_pool)

    _talker_id = None

    def __init__(self, talker_id):
        self._talker_id = talker_id
        # 如果第一次交谈，则进行初始化，此处更多的是为了说明，应该包含这些属性
        if not self._cache.exists(talker_id):
            self.travel_log_id = ""
            self.expire_at = -1
            self.remain_action_count = 2

    @property
    def travel_log_id(self):
        return self.get_attribute("travel_log_id")

    @travel_log_id.setter
    def travel_log_id(self, travel_log_id):
        self.set_attribute("travel_log_id", travel_log_id)

    @property
    def expire_at(self):
        return self.get_attribute("expire_at")

    @expire_at.setter
    def expire_at(self, expire_at):
        self.set_attribute("expire_at", expire_at)

    @property
    def remain_action_count(self):
        return self.get_attribute("remain_action_count")

    @remain_action_count.setter
    def remain_action_count(self, remain_action_count):
        self.set_attribute("remain_action_count", remain_action_count)

    @property
    def max_inactive_interval(self):
        return self.get_attribute("max_inactive_interval")

    @max_inactive_interval.setter
    def max_inactive_interval(self, interval):
        """
        给session设置过期时间
        :param interval:
        :return:
        """
        self.set_attribute("max_inactive_interval", interval)
        self.expire_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + interval))

    def exists_attribute(self, name):
        """
        查看哈希表的指定字段是否存在。如果哈希表含有给定字段，返回`True`。如果哈希表不含有给定字段，或`key`不存在，返回`False`。
        :param name:
        :return:
        """
        return self._cache.hexists(self._talker_id, name)

    def get_id(self):
        return self._talker_id

    def set_attribute(self, name, value):
        """
        为哈希表中的字段赋值 。如果哈希表不存在，一个新的哈希表被创建并进行`HSET`操作。如果字段已经存在于哈希表中，旧值将被覆盖。
        如果字段是哈希表中的一个新建字段，并且值设置成功，返回 1 。 如果哈希表中域字段已经存在且旧值已被新值覆盖，返回 0 。
        :param name:
        :param value:
        :return:
        """
        self._cache.hset(self._talker_id, name, value)

    def get_attribute(self, name):
        """
        返回哈希表中指定字段的值。返回给定字段的值。如果给定的字段或`key`不存在时，返回`None`
        :param name:
        :return:
        """
        return self._cache.hget(self._talker_id, name)

    def del_attribute(self, name):
        """
        删除哈希表`key`中的一个或多个指定字段，不存在的字段将被忽略。
        :param name:
        :return:
        """
        self._cache.hdel(self._talker_id, name)

    def get_all_attribute(self):
        """
        返回哈希表中，所有的字段和值。在返回值里，紧跟每个字段名(field name)之后是字段的值(value)，所以返回值的长度是哈希表大小的两倍。
        :return:
        """
        return self._cache.hgetall(self._talker_id)

    def invalidate(self):
        """
        使session失效
        :return:
        """
        self.remain_action_count = 0

    def is_valid(self):
        """
        1、每次执行完`travel`指令后，会给`remain_action_count`赋值，表示可执行的行动指令次数
        2、当`remain_action_count`大于0，且`expire_at`未到当前时间（即未过期）时，才可执行`action`指令
        3、当`remain_action_count`等于0，或者`expire_at`大于或等于当前时间（即过期）时，无法执行`action`指令
        4、当`remain_action_count`等于-1，不限次数
        :return:
        """
        is_expired = False if self.expire_at == '-1' else (time.localtime() > time.strptime(self.expire_at, "%Y-%m-%d %H:%M:%S"))

        if self.travel_log_id == "" or int(self.remain_action_count) < 1 or is_expired:
            return False

        return True
