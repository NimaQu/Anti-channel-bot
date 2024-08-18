import asyncio
import logging
from configparser import ConfigParser

from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, RPCError
from pyrogram.types import (Message, ChatPermissions)
from pyrogram.enums import ChatType, ChatMembersFilter

from dbhelper import DBHelper
from nyamediamarriot import *

botconfig = ConfigParser()
botconfig.read('bot.ini', encoding='utf-8')
default_config = {}
logging.basicConfig(level=logging.INFO)
db = DBHelper()
mute_user = {}


def init_default_config():
    global default_config
    default_config = dict(botconfig.items('config'))


def nyamediamarriot_init():
    def init_room():
        for i in range(1, 27):
            for j in range(1, 20):
                room_number = i * 100 + j
                rooms[room_number] = Room(room_number)
    init_room()


def get_group_config(chat_id):
    try:
        int(chat_id)
    except ValueError:
        return None
    db_config = db.get_group_config(chat_id, 'all')
    if db_config is None:
        return default_config
    else:
        final_config = {**default_config, **db_config}
        return final_config


async def command_ban_add(client: Client, message: Message, force=False):
    if not force:
        administrators = []
        async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            administrators.append(m.user.id)
        if message.from_user.id in administrators:
            return
    msg_user_id = message.from_user.id
    last_mute_time = mute_user.get(msg_user_id)
    mute_seconds = 60
    if last_mute_time is None:
        mute_user[msg_user_id] = mute_seconds
    else:
        ban_seconds = last_mute_time * 2
        mute_user[msg_user_id] = ban_seconds
    await message.delete()
    await client.restrict_chat_member(message.chat.id, msg_user_id, ChatPermissions(can_send_messages=True), until_date=datetime.now() + timedelta(seconds=mute_seconds))


def bot(app):
    @app.on_message(filters.command("acset") & filters.group)
    async def set_config(client: Client, message: Message):
        if message.from_user is None:
            reply_message = await message.reply("请从个人账号发送指令。")
            await asyncio.sleep(10)
            await reply_message.delete()
            return
        chat_id = message.chat.id
        user_id = message.from_user.id
        admins = []
        async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            admins.append(m.user.id)
        help_message = "使用方法:\n" \
                       "/acset [配置项] [值]\n\n" \
                       "配置项:\n" \
                       "`operate`: 发现频道发言执行的动作，值为 `ban`, `del`(删除消息), `all`(ban + 删除消息)。" \
                       "注意：因为 Telegram 限制，这个 ban 并不能实际 ban 掉使用频道发言的用户，但可以禁用他使用频道发言的能力\n" \
                       "`message`: 发现频道发言后发送的消息\n" \
                       "`silent_mode`: 是否启用静默模式（不发送消息）1(开启) 或者 0(关闭)\n\n" \
                       "例如: \n" \
                       "`/acset operate ban`"
        if user_id not in admins:
            reply_message = await message.reply("您没有权限使用此命令。")
            await command_ban_add(client, message, force=True)
            await asyncio.sleep(10)
            await reply_message.delete()
            return

        args = message.text.split(" ", maxsplit=2)
        if len(args) < 3:
            await message.reply(help_message)
            return
        key = args[1]
        value = args[2]
        if db.set_group_config(chat_id, key, value):
            await message.reply("配置项设置成功")
        else:
            await message.reply("配置项设置失败, 请输入 /acset 查看帮助")

    @app.on_message(filters.command("acgm") & filters.group)
    async def get_message_info(client: Client, message: Message):
        target_message = message.reply_to_message
        if target_message is None:
            return
        await message.reply(str(target_message))

    @app.on_message(filters.chat(chats=[-1001730617795, -1001502675110]))
    async def nyamedia(client: Client, message: Message):
        args = message.text.split(' ')
        if len(args) == 0:
            return
        if '/checkin' in args[0]:
            await handle_checkin(client, message)
        elif '/reserve' in args[0]:
            await handle_reservation(client, message)
        elif '/checkout' in args[0]:
            await handle_checkout(client, message)
        elif '/acset' in args[0]:
            await command_ban_add(client, message)

    @app.on_message(filters.group)
    async def group_message(client, message):
        if message.sender_chat is None:
            return
        if message.sender_chat.type != ChatType.CHANNEL or message.chat.type != ChatType.SUPERGROUP:
            return
        chat_id = message.chat.id
        channel_id = message.sender_chat.id
        group_config = get_group_config(chat_id)
        if group_config is None:
            return

        try:
            if group_config['operate'] == 'del':
                await message.delete()
            elif group_config['operate'] == 'ban':
                await client.ban_chat_member(chat_id=chat_id, user_id=channel_id)
            elif group_config['operate'] == 'all':
                await message.delete()
                await client.ban_chat_member(chat_id=chat_id, user_id=channel_id)

            if int(group_config['silent_mode']) == '1':
                return
            else:
                reply_message = await message.reply(group_config['message'])
                await asyncio.sleep(10)
                await reply_message.delete()
                return
        except ChatAdminRequired:
            logging.error('机器人权限不足，无法操作, 群组 ID:' + str(chat_id))
            return
        except RPCError as e:
            logging.error('rpc error: ' + str(e))
            return
        except KeyError:
            logging.error('配置项缺失')
            return
        except Exception as e:
            logging.error('未知错误：' + str(e))
            return


def main():
    db.setup()
    init_default_config()
    nyamediamarriot_init()
    app = Client("Anti channel bot",
                 api_id=botconfig.get('auth', 'api_id'),
                 api_hash=botconfig.get('auth', 'api_hash'),
                 bot_token=botconfig.get('auth', 'bot_token'))
    bot(app)
    app.run()


if __name__ == "__main__":
    main()
