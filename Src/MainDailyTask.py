import asyncio
import platform
import random
import time
import copy

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from BasicRequest import BasicRequest
from Base import std235959ptm, std235959
from Config import *


class MainDailyTask:
    def __init__(self):
        self.ok = 0

    async def work(self):
        if config["Function"]["MainDailyTask"] == "False":
            return

        Log.info("检查主站每日任务")

        # 必须有房间号才能运行
        if config["MainDailyTask"]["ROOM_ID"] == "":
            Log.warning("主站任务模块up主号未配置,已停止...")
        else:
            await self.share()
            await self.watch()
            await self.coin()

    async def watch(self):
        var = 0
        MainDailyTask_Watch = int(config["MainDailyTask"]["Watch"])
        if MainDailyTask_Watch == 0:
            return
        else:
            need_watch = MainDailyTask_Watch
        if need_watch < 0:
            need_watch = -need_watch
        while var < need_watch:
            check_reward_data = await self.Reward_Request()
            if check_reward_data["data"]["watch"]:
                Log.info('观看任务获取经验已经完成，退出观看任务')
                return
            var = var + 1
            Log.info("本次观看视频为第 %s 次" % (var))
            Room_Id = random.choice(config["MainDailyTask"]["ROOM_ID"].split(","))
            Log.info("本次观看选择UP的ID为 %s" % (Room_Id))
            url = "https://api.bilibili.com/x/space/arc/search?ps=100&pn=1&mid=" + str(Room_Id)
            data = await AsyncioCurl().request_json("GET", url)
            need_vilst = random.choice(data["data"]["list"]["vlist"])

            Log.info("本次观看的视频信息如下")
            Log.info("标题  %s" % (need_vilst["title"]))
            Log.info("作者  %s" % (need_vilst["author"]))
            # Log.info("简介  %s" % (need_vilst["description"]))
            Log.info("视频BV号  %s" % (need_vilst["bvid"]))
            Log.info("视频AV号  %s" % (need_vilst["aid"]))

            # 获取视频分P
            url = "https://api.bilibili.com/x/player/pagelist?bvid=" + need_vilst["bvid"]

            data = await AsyncioCurl().request_json("GET", url)

            video_cid = data["data"][0]["cid"]

            url = "https://api.bilibili.com/x/click-interface/web/heartbeat"

            payload = {
                "aid": need_vilst["aid"],
                "cid": video_cid,
                "bvid": need_vilst["bvid"],
                "mid": Room_Id,
                "csrf": account["Token"]["CSRF"],
                "played_time": 0,
                "realtime": 0,
                "start_ts": int(time.time()),
                "type": 3,
                "dt": 2,
                "play_type": 1}

            data = await AsyncioCurl().request_json("POST", url, headers = config["pcheaders"], data = payload)
            if data["code"] == 0:
                if var < need_watch:
                    sleep_time = random.randint(60, 300)
                    Log.info('视频观看成功，休眠 %d s' % sleep_time)
                    await asyncio.sleep(sleep_time)
                else:
                    Log.info('视频观看任务完成，退出任务')

            else:
                Log.error("出现错误 %s" % (data["message"]))

    async def coin(self):
        add_coin = 0
        MainDailyTask_Coin = int(config["MainDailyTask"]["Coin"])
        if MainDailyTask_Coin == 0:
            return
        else:
            if MainDailyTask_Coin < 5:
                need_coin = MainDailyTask_Coin
            else:
                need_coin = 5
        while add_coin < need_coin:

            check_reward_data = await self.Reward_Request()
            Log.info("第一次检查今日已投币： {}".format(check_reward_data["data"]["coins"]))
            if check_reward_data["data"]["coins"] >= 50:
                Log.info('投币任务获取经验已经达到最大值,投币任务完成,退出投币任务')
                return

            if add_coin < check_reward_data["data"]["coins"] / 10:
                add_coin = check_reward_data["data"]["coins"] // 10

            if check_reward_data["data"]["coins"] >= need_coin * 10 or add_coin >= need_coin:
                # 有时候有延迟自己开了一个add_coin变量
                Log.info('今日设置的投币任务完成,退出投币任务')
                return

            data = await self.Nav_Request()
            if data["data"]["money"] < 1:
                Log.warning('家境贫寒.jpg，退出投币任务')
                Log.warning('下次一定！')
                return

            Log.info("本次投币任务为第 %s 次执行" % (add_coin + 1))
            Room_Id = random.choice(config["MainDailyTask"]["ROOM_ID"].split(","))
            Log.info("本次投币选择UP的ID为 %s" % (Room_Id))
            url = "https://api.bilibili.com/x/space/arc/search?ps=100&pn=1&mid=" + str(Room_Id)
            data = await AsyncioCurl().request_json("GET", url)
            need_vilst = random.choice(data["data"]["list"]["vlist"])

            Log.info("本次投币的视频信息如下")
            Log.info("标题  %s" % (need_vilst["title"]))
            Log.info("作者  %s" % (need_vilst["author"]))
            # Log.info("简介  %s" % (need_vilst["description"]))
            Log.info("视频BV号  %s" % (need_vilst["bvid"]))
            Log.info("视频AV号  %s" % (need_vilst["aid"]))

            check_reward_data = await self.Reward_Request()
            Log.info("第二次检查今日已投币： {}".format(check_reward_data["data"]["coins"]))
            if check_reward_data["data"]["coins"] >= 50:
                Log.info('投币任务获取经验已经达到最大值,投币任务完成,退出投币任务')
                return

            if add_coin < check_reward_data["data"]["coins"] / 10:
                add_coin = check_reward_data["data"]["coins"] // 10

            url = "https://api.bilibili.com/x/web-interface/coin/add"

            payload = {
                "aid": need_vilst["aid"],
                "multiply": 1,
                "select_like": 1,
                "csrf": account["Token"]["CSRF"]}

            data = await AsyncioCurl().request_json("POST", url, headers = config["pcheaders"], data = payload)

            if data["code"] == 0:
                add_coin = add_coin + 1
                if add_coin < need_coin:
                    sleep_time = random.randint(60, 300)
                    Log.info('投币成功，休眠 %d s' % sleep_time)
                    await asyncio.sleep(sleep_time)
                else:
                    Log.info('投币任务完成，退出任务')
            else:
                Log.error("投币错误 %s" % (data["message"]))

            await asyncio.sleep(3)

        if add_coin > 5:
            # 如果执行了5次还没完成任务，那么就是错误，那么就是见鬼了
            Log.warning('投币任务执行5次以上，触发硬币保护（雾 ，退出投币任务')

    async def share(self):
        var = 0
        MainDailyTask_Share = int(config["MainDailyTask"]["Share"])
        if MainDailyTask_Share == 0:
            return
        else:
            need_Share = MainDailyTask_Share
        if need_Share < 0:
            need_Share = -need_Share
        while var < need_Share:
            check_reward_data = await self.Reward_Request()
            if check_reward_data["data"]["share"]:
                Log.info('分享任务获取经验已经完成，退出分享任务')
                return
            var = var + 1
            Log.info("本次分享视频为第 %s 次" % (var))
            Room_Id = random.choice(config["MainDailyTask"]["SHARE_ID"].split(","))
            Log.info("本次分享选择UP的ID为 %s" % (Room_Id))
            url = "https://api.bilibili.com/x/space/arc/search?ps=100&pn=1&mid=" + str(Room_Id)
            data = await AsyncioCurl().request_json("GET", url)
            need_vilst = random.choice(data["data"]["list"]["vlist"])

            Log.info("本次分享的视频信息如下")
            Log.info("标题  %s" % (need_vilst["title"]))
            Log.info("作者  %s" % (need_vilst["author"]))
            # Log.info("简介  %s" % (need_vilst["description"]))
            Log.info("视频BV号  %s" % (need_vilst["bvid"]))
            Log.info("视频AV号  %s" % (need_vilst["aid"]))

            url = "https://api.bilibili.com/x/web-interface/share/add"

            payload = {
                "aid": need_vilst["aid"],
                "jsonp": "jsonp",
                "csrf": account["Token"]["CSRF"]}

            data = await AsyncioCurl().request_json("POST", url, headers = config["pcheaders"], data = payload)

            if data["code"] == 0:
                if var < need_Share:
                    sleep_time = random.randint(60, 300)
                    Log.info('视频分享成功，休眠 %d s' % sleep_time)
                    await asyncio.sleep(sleep_time)
                else:
                    Log.info('视频分享任务完成，退出任务')
            else:
                Log.error("分享错误 %s" % (data["message"]))

    async def Reward_Request(self):
        url = "https://api.bilibili.com/x/member/web/exp/reward"

        data = await AsyncioCurl().request_json("GET", url, headers = config["pcheaders"])

        return data

    async def Nav_Request(self):
        url = "https://api.bilibili.com/x/web-interface/nav"

        data = await AsyncioCurl().request_json("GET", url, headers = config["pcheaders"])

        return data
