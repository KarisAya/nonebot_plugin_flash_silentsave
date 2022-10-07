<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot_plugin_flash_silentsave

静默保存群聊中的闪照。

</div>

## 介绍

本插件无配置项，但可以通过指令或者修改 bot.py目录下 .\data\flash\config.json 配置本插件

__config.json__

    {
        "count": 5,       # 闪照发送数量
        "CUSTOMER": [     # 闪照管理员
            1048827424,   # 管理员qq号（int）
            1000000000,
            2000000000
       ]
    }

本插件会把闪照转成可以查看闪照的url然后储存 bot.py目录下 .\data\flash\flash_url.json 文件里。

__如果没有配置过此插件和没有储存过闪照，那么没有这两个文件是正常的__

## 指令

### 【超管，群主，管理员，闪照管理员】

群内发送 `查看闪照` 在群内查看本群闪照（默认发送前5个）

### 【超管，闪照管理员】

私聊发送 `查看闪照` 然后发送 `群号` 通过私聊查看特定群的闪照（默认发送前5个）

### 【超管】

可以通过指令设置闪照储存数量，闪照发送数量，添加或删除闪照管理员等。

`设置闪照发送数量 N` 设置闪照发送数量（1 <= N <= 20）

`添加闪照管理员 @a@b@c...` 添加at的用户为闪照管理员（只能通过群内at添加或删除闪照管理员。）

`删除闪照管理员 @a@b@c...` 从闪照管理员中删除at的用户（同上，还有at了不是闪照管理员的用户也没有影响。）

`清理闪照` 清理失效的url

### ~~【服务器机主】~~

~~修改config.json~~

~~话说这是指令吗~~

## 需要安装

[nonebot_plugin_apscheduler](https://github.com/nonebot/plugin-apscheduler) APScheduler 定时任务插件

## 安装
    pip install nonebot_plugin_flash_silentsave
## 使用
    nonebot.load_plugin('nonebot_plugin_flash_silentsave')
    
## 其他

借鉴~~抄~~自[nonebot_plugin_antiflash](https://github.com/MinatoAquaCrews/nonebot_plugin_antiflash)：群聊反闪照
