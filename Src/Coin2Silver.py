# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了硬币换银瓜子功能

import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from Config import *


class Coin2Silver:

    async def work(self):
        if config["Function"]["COIN2SILVER"] == "False":
            return
        await self.exchange(config["Coin2Silver"]["COIN"])

    async def exchange(self, num):
        url = "https://api.live.bilibili.com/pay/v1/Exchange/coin2silver"

        payload = {
            "num": num,
            "csrf_token": account["Token"]["CSRF"]
        }

        data = await AsyncioCurl().request_json("POST", url, headers = config["pcheaders"], data = payload)

        if data["code"] != 0:
            Log.warning(data["message"])
            return

        Log.info(data["message"] + ", %s 枚硬币兑换了 %s 个银瓜子" % (num, data["data"]["silver"]))
