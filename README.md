# Telegram-CAPTCHA-bot

一个用于禁止公开群成员使用频道发言的 Bot

[![Python 3.10](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org) [![Pyrogram](https://img.shields.io/badge/Pyrogram-asyncio-green.svg)](https://github.com/pyrogram/pyrogram/)

## 安装与使用

**本 Bot 在 Python 3.10 环境下进行开发，建议使用不低于 3.10 的 python 进行部署**  
1. 请先向 [@BotFather](https://t.me/botfather) 申请一个 Bot API Token  
> 你申请到的机器人会在你的 Telegram 账号所在数据中心上运行（即申请机器人的账号A位于 DC 5 (新加坡)，则 A 申请到的机器人也将会在 DC5 上运行)
2. 在 [Obtaining Telegram API ID](https://core.telegram.org/api/obtaining_api_id) 申请 API ID 与 API Hash
3. 使用 Python Virtual Environment 部署: 
```
# 若未安装pip3，请先安装 python3-pip
apt update && apt install -y python3-pip python3
git clone https://github.com/NimaQu/Anti-channel-bot.git
cd Anti-channel-bot
python3 -m venv venv
venv/bin/pip install wheel
venv/bin/pip install -r requirements.txt
```

4. 将项目文件夹中 bot.ini 里的 auth 字段（与等号间存在一个空格）修改为你在 [@BotFather](https://t.me/botfather) 获取到的 API Token，api_hash 和 api_id 修改为你在步骤2中获得的两串内容，其中 API ID 为数字，而 API Hash 为一组字符。

5. 使用 `venv/bin/python` 直接运行这个 bot,或者在 `/etc/systemd/system/ `下新建一个 .service 文件，使用 systemd 控制这个bot的运行，配置文件示例请参考本项目目录下的 `example.service` 文件进行修改。

```bash
cp example.service /etc/systemd/system/acbot.service
nano /etc/systemd/system/acbot.service
#编辑参数
systemctl start acbot
#启动
systemctl enable acbot
#开机自启
```

6. 将本 bot 加入一个群组，并给予封禁用户的权限，即可开始使用

## 配置说明
使用方法:
/acset [配置项] [值]

配置项:
operate: 发现频道发言执行的动作，值为 ban, del(删除消息), all(ban + 删除消息)。 注意：因为 Telegram 限制，这个 ban 并不能实际 ban 掉使用频道发言的用户，但可以禁用他使用频道发言的能力

message: 发现频道发言后发送的提醒消息

silent_mode: 是否启用静默模式（不发送提醒消息）1(开启) 或者 0(关闭)

例如: 
`/acset operate ban`

`/acset silent_mode 0`

`/acset message 禁止在此群使用频道发送消息`

## 日志
在安装了 systemd ，且已经在 /etc/systemd/system 下部署了服务的 Linux 操作系统环境下，请使用命令：
```bash
journalctl -u acbot.service 
#查看从启动时的日志
journalctl -f -u acbot.service
#查看实时日志
# 这里的 acbot.service 请自行更名为你在服务器上部署的服务名
```