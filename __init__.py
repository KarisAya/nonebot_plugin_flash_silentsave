from nonebot.plugin.on import on_command,on_message
from nonebot.rule import to_me

from nonebot.adapters.onebot.v11 import (
    GROUP,
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    Event,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
    Message
    )
from nonebot.permission import SUPERUSER

from nonebot.params import CommandArg, Arg
from pathlib import Path

import nonebot
import os
import re
import time

try:
    import ujson as json
except ModuleNotFoundError:
    import json

import requests

from nonebot import require

scheduler = require("nonebot_plugin_apscheduler").scheduler

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]

path = Path() / "data" / "flash"

flash_url_file = Path(path) / "flash_url.json"
group_namelist_file = Path(path) / "group_namelist.json"
config_file = Path(path) / "config.json"

if path.exists():
    pass
else:
    path.mkdir(parents=True, exist_ok=True)

if flash_url_file.exists():
    with open(flash_url_file, "r", encoding="utf8") as f:
        flash_url = json.load(f)
else:
    flash_url = {}

if group_namelist_file.exists():
    with open(group_namelist_file, "r", encoding="utf8") as f:
        group_namelist = json.load(f)
else:
    group_namelist = {}

if config_file.exists():
    with open(config_file, "r", encoding="utf8") as f:
        config = json.load(f)
else:
    config = {
        "count":5,
        "CUSTOMER": []
        }

# 定义is_flash匹配规则
async def is_flash(event: GroupMessageEvent) -> bool:
    return 'type=flash' in str(event.get_message())

# 定义CUSTOMER权限
async def CUSTOMER(bot: Bot, event: Event) -> bool:
    return int(event.get_user_id()) in config["CUSTOMER"]

# 保存闪照
save_flash = on_message(rule = is_flash, permission = GROUP, priority = 1)

@save_flash.handle()
async def _(event: GroupMessageEvent):
    group_id = str(event.group_id)
    msg = str(event.get_message())
    comment = str(re.compile(r'file=(.*?).image',re.S).findall(msg))
    comment = str(re.sub("[^0-9A-Za-z\u4e00-\u9fa5]", '', comment.upper()))
    url = ('https://gchat.qpic.cn/gchatpic_new/' + event.get_user_id() + '/2640570090-2264725042-' + comment + '/0?term=3')
    global flash_url, flash_url_file
    flash_url.setdefault(group_id,[])
    flash_url[group_id].append(url)

    with open(flash_url_file, "w", encoding="utf8") as f:
        json.dump(flash_url, f, ensure_ascii=False, indent=4)

# 查看闪照
flashimg = on_command("查看闪照", permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | CUSTOMER, priority = 20, block = True)

@flashimg.handle()
async def _(bot:Bot ,event: MessageEvent):
    global flash_url, config
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        msg_list =[]
        n = config["count"] if len(flash_url.get(group_id,[])) > config["count"] else len(flash_url.get(group_id,[]))
        if n > 0:
            for i in range (n):
                msg_list.append(
                    {
                        "type": "node",
                        "data": {
                            "name": Bot_NICKNAME,
                            "uin": event.self_id,
                            "content": MessageSegment.image(flash_url[group_id][-i-1])
                            }
                        }
                    )
            else:
                await bot.send_group_forward_msg(group_id = event.group_id, messages = msg_list)
                await flashimg.finish()
        else:
            await flashimg.finish("无本群闪照记录")
    else:
        global group_namelist
        msg = ""
        Now = time.time()
        flag = 0
        for i in flash_url.keys():
            if i in group_namelist.keys() and group_namelist[i][1] + 604800 > Now:
                group_name = group_namelist[i][0]
            else:
                flag = 1
                try:
                    info = await bot.get_group_info(group_id = int(i))
                    group_name = info["group_name"]
                except:
                    group_name = "群名获取失败"
                group_namelist.update({i:[group_name,Now]})
            msg += f'{group_name}【{i}】\n'
        else:
            if flag == 1:
                with open(group_namelist_file, "w", encoding="utf8") as f:
                    json.dump(group_namelist, f, ensure_ascii=False, indent=4)
            else:
                pass
        if msg:
            await flashimg.send("请选择你要查看的群号：\n" + msg[:-1])
        else:
            await flashimg.finish("无闪照记录")

@flashimg.got("group_id")
async def _(group_id: Message = Arg()):
    global flash_url, config
    group_id = str(group_id)
    msg = ""
    n = config["count"] if len(flash_url.get(group_id,[])) > config["count"] else len(flash_url.get(group_id,[]))
    if n:
        for i in range (n):
            msg += MessageSegment.image(flash_url[group_id][-i-1])
        else:
            await flashimg.finish(msg)
    else:
        await flashimg.finish(f"群号【{group_id}】未记录")

# 设置闪照显示数量
set_config_count = on_command("设置闪照发送数量" ,aliases = {"设置闪照显示数量"}, permission = SUPERUSER, priority = 20, block = True)

@set_config_count.handle()
async def _(event: MessageEvent,arg: Message = CommandArg()):
    global config
    try:
        msg = int(arg.extract_plain_text().strip())
        config["count"] = msg if 1 <= msg <= 20 else 5
        with open(config_file, "w", encoding="utf8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        await set_config_count.finish(f'闪照显示数量已设置成{config["count"]}')
    except Exception as error:
        await set_config_count.finish(str(error))

def get_message_at(data: str) -> list:
    qq_list = []
    data = json.loads(data)
    try:
        for msg in data['message']:
            if msg['type'] == 'at':
                qq_list.append(int(msg['data']['qq']))
        return qq_list
    except Exception:
        return []

# 添加闪照管理员
add_CUSTOMER = on_command("添加闪照管理员", permission = SUPERUSER, priority = 20, block = True)

@add_CUSTOMER.handle()
async def _(event: GroupMessageEvent):
    at = get_message_at(event.json())
    global config
    try:
        config.setdefault("CUSTOMER",[])
        config["CUSTOMER"] = list(set(config["CUSTOMER"]) | set(at))
        with open(config_file, "w", encoding="utf8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        await add_CUSTOMER.finish("添加成功")
    except Exception as error:
        await add_CUSTOMER.finish(str(error))

# 删除闪照管理员
del_CUSTOMER = on_command("删除闪照管理员", permission = SUPERUSER, priority = 20, block = True)

@del_CUSTOMER.handle()
async def _(event: GroupMessageEvent):
    at = get_message_at(event.json())
    global config
    try:
        config.setdefault("CUSTOMER",set())
        config["CUSTOMER"] = list(set(config["CUSTOMER"]) - set(at))
        with open(config_file, "w", encoding="utf8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        await del_CUSTOMER.finish("删除成功")
    except Exception as error:
        await del_CUSTOMER.finish(str(error))

clean = on_command("清理闪照", aliases = {"清理失效闪照","清除失效闪照"}, permission = SUPERUSER, priority = 20, block = True)
@clean.handle()
@scheduler.scheduled_job("cron",hour = 0)
def _():
    global flash_url, flash_url_file
    nonebot.logger.info("正在清理失效url...")
    requests.packages.urllib3.disable_warnings()
    for group_id in flash_url.keys():
        for url in flash_url[group_id]:
            try:
                resp = requests.get(url, verify=False, allow_redirects=True, timeout=5)
                if resp.status_code != 200:
                    nonebot.logger.info(f"{url}已失效")
                    flash_url[group_id].remove(url)
            except requests.RequestException as e:
                nonebot.logger.warning(e)
                continue

    New_flash_url = {}
    for group_id in flash_url.keys():
        if flash_url[group_id]:
            New_flash_url[group_id] = flash_url[group_id]
    else:
        flash_url = New_flash_url
    nonebot.logger.success("清理完成！")
    with open(flash_url_file, "w", encoding="utf8") as f:
        json.dump(flash_url, f, ensure_ascii=False, indent=4)