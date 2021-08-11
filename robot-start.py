import json
import logging
import os
import asyncio
import random
import time

from wechaty_grpc.wechaty.puppet import FriendshipType

from entity.LogContent import LogContent
from entity.Session import Session
from entity.TravelLog import TravelLog
from entity.Wander import Wander
from system.Command import Command

os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = '1c468a07-9d85-4af4-945a-db7238b53189'
os.environ['WECHATY_PUPPET'] = 'wechaty-puppet-service'

from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
    Friendship,
)

wander = Wander()


async def on_message(msg: Message):
    talker = msg.talker()
    # 关联用户的session
    session = Session(talker.get_id())

    # 理解指令意义，如果是自己，则会返回False
    (command, content) = wander.command_system.parse(msg)

    if command in (Command.CMD_SELF, Command.CMD_NONE):
        # 如果是自己发送的，或者无法识别的消息，统一不回复，并结束流程
        return

    if command is Command.CMD_TRAVEL:
        address = content
        # wander通过定位系统查找地址的GPS坐标
        try:
            location = wander.find_location(address)
        except Exception as e:
            retMessage = str(e)
            if retMessage == "10001":
                retMessage = "收到太阳风暴影响，无法定位该目的地。请求更换目标。"  # 地点搜索失败

            await talker.say(retMessage)
            return

        lng = location["lng"]
        lat = location["lat"]
        lng_str = str(lng)
        lat_str = str(lat)

        # 随机定义一个类型
        style = random.randint(0, 2)
        print("style: " + str(style))
        # 随机进入到某个时间
        year = random.randint(3050, 3090)

        retMessage = "正在前往：" + address
        await talker.say(retMessage)

        time.sleep(0.8)
        retMessage = "能量积蓄中……"
        await talker.say(retMessage)

        time.sleep(0.8)
        retMessage = "已安全着陆，记录降落位置：\n经度: " + lng_str + "\n纬度: " + lat_str
        await talker.say(retMessage)

        try:
            describe_scene_content = await wander.describe_scene(year, address, style)
            await talker.say(describe_scene_content)
        except Exception as e:
            retMessage = str(e)
            if retMessage == "10004":
                retMessage = "思维系统暂时失效，正在修复中……\n……说……说不出话了……怎么办……"

            describe_scene_content = retMessage
            await talker.say(retMessage)

        time.sleep(0.8)
        retMessage = "正在确认周围环境，回传图像……"
        await talker.say(retMessage)

        # 图片对象初始化
        photo = None

        try:
            photo = await wander.take_photo(lng, lat, style)
            await talker.say(photo)
        except Exception as e:
            # 处理根据定位传GPS，以及根据GPS返回照片+风格迁移产生的错误
            retMessage = str(e)
            if retMessage == "10002":
                retMessage = "该地点有影像屏蔽力场，无法拍摄图像。\n唉，是核辐射或静电导致的吗？"  # 照片获取失败
            elif retMessage == "10005":
                retMessage = "给图像已截取，但未能成功解码传输。"  # 给图像打Logo失败

            await talker.say(retMessage)

        talking_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        try:
            # 保存旅游日志
            travel_log = TravelLog()
            travel_log.talker_id = talker.get_id()
            travel_log.talker_name = talker.name
            travel_log.talker_gender = talker.gender()
            travel_log.talker_province = talker.province()
            travel_log.talker_city = talker.city()
            travel_log.talking_time = talking_time
            travel_log.address = address
            travel_log.location = location
            travel_log.future_year = year
            travel_log.content = describe_scene_content
            travel_log.photo = 'static/404.gif' if photo is None else '%s%s' % (
                'data:image/jpeg;base64,', str(photo.base64, encoding='utf-8'))
            travel_log.style = style

            # 创建旅行日志内容
            # TODO 优化下关联实体
            log_content = LogContent(travel_log_id=travel_log.id)
            log_content.command = Command.CMD_TRAVEL
            log_content.argument = "前往" + address
            log_content.executed_at = talking_time
            log_content.content = describe_scene_content
            log_content.photo = travel_log.photo

            result = wander.storage_system.save_travel_log(travel_log=travel_log, log_content=log_content,
                                                           log_session=session)
            # 设置会话有效期为120s，并可进行2次行动
            session.max_inactive_interval = 120
            session.remain_action_count = 2

            await talker.say(result)
        except Exception as e:
            logging.info(e)
            if talker.name == "扣扣":
                await talker.say("错误是：" + str(e))
            retMessage = '受到时空隧道波动干扰，本次行动未能记录。'
            await talker.say(retMessage)
    elif command is Command.CMD_ACTION:
        if talker.name == "扣扣":
            await talker.say(json.dumps(session.get_all_attribute()))

        travel_log = wander.storage_system.get_travel_log_by_id(session.travel_log_id)
        # 先检查此行动是否已经过期
        if not session.is_valid():
            address = travel_log.address
            await talker.say("本次时空驻留能量已耗尽，位于 {} 的旅行结束。".format(address))
        else:
            # 行动续写第一部分是自我介绍
            self_introduction = wander.thinking.self_introduction()
            # 将前面的文章、回复的行为全部衔接起来
            above_tmp = ["%s。\n%s" % (log_content.argument, log_content.content) for log_content in
                         travel_log.content_of_travel_log]
            above = self_introduction + "".join(above_tmp)
            # 遍历本次旅行前文内容，拼接起来作为本次续写的prompt
            content = ('我' + content) if content[0] != '我' else content
            prompt = above.replace("……", "。\n") + content
            if talker.name == '扣扣' or talker.name == '未命名Cheese':
                await talker.say("续写的内容为：" + prompt)
            try:
                action_result = await wander.do_action(prompt=prompt)
                await talker.say(action_result)
            except Exception as e:
                retMessage = str(e)
                if retMessage == "10004":
                    retMessage = "思维系统暂时失效，正在修复中……\n……说……说不出话了……怎么办……"

                await talker.say(retMessage)
                return

            try:
                log_content = LogContent(travel_log_id=travel_log.id)
                log_content.command = Command.CMD_ACTION
                log_content.argument = content
                log_content.executed_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                log_content.content = action_result
                log_content.photo = "static/404.gif"

                result = wander.storage_system.save_travel_log_content(log_content=log_content)

                await talker.say(result)
                # 行动完后，max_action_count减一
                session.max_inactive_interval = 120
                session.remain_action_count = int(session.remain_action_count) - 1
            except Exception as e:
                logging.info(e)
                if talker.name == "扣扣":
                    await talker.say("错误是：" + str(e))
                retMessage = '受到时空隧道波动干扰，本次行动未能记录。'
                await talker.say(retMessage)


async def on_scan(qrcode: str, status: ScanStatus, _data):
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    print(user)


async def on_friendship(friendship: Friendship):
    # FriendshipType.Confirm 发出接受添加好友
    # FriendshipType.Receive 收到添加好友请求
    if friendship.type() == FriendshipType.FRIENDSHIP_TYPE_RECEIVE:  # and friendship.hello() == "Hello Wander":
        await friendship.accept()

    if friendship.type() == FriendshipType.FRIENDSHIP_TYPE_CONFIRM:
        await friendship.contact().say(wander.say_hello(friendship.contact().name))
        await friendship.contact().say(wander.guide())


async def main():
    # 确保我们在环境变量中设置了WECHATY_PUPPET_SERVICE_TOKEN
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()

    bot.on('scan', on_scan)
    bot.on('login', on_login)
    bot.on('message', on_message)
    bot.on('friendship', on_friendship)

    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


asyncio.run(main())
