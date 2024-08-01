import asyncio
from enum import Enum
from pyrogram import Client
from pyrogram.types import Message
from datetime import datetime, timezone, timedelta
import random

cn_tz = timezone(offset=timedelta(hours=8))

rooms = {}
reservations = {}


class Room:
    def __init__(self, room_number: int):
        self.room_number = room_number
        self.room_status = room_status.available
        self.room_member = []


class room_status(Enum):
    available = 0
    occupied = 1


class Guest:
    def __init__(self, name, room_number):
        self.name = name
        self.room_number = room_number


class Member(Guest):
    def __init__(self, name, room_number, member_id):
        super().__init__(name, room_number)
        self.member_id = member_id


class Reservation:
    def __init__(self, checkin_date, duration_days, member_id=None):
        self.member_id = member_id
        self.checkin_date = checkin_date
        self.checkout_date = checkin_date + duration_days


async def handle_checkin(client: Client, message: Message):
    reservation = reservations.get(message.from_user.id)
    if reservation is None:
        r_msg = await message.reply('亲亲找不到您的预定信息哦')
        await asyncio.sleep(30)
        await r_msg.delete()
        await message.delete()
        return
    available_rooms = [room for room in rooms.values() if room.room_status == room_status.available]
    if len(available_rooms) == 0:
        r_msg = await message.reply('亲亲没有空房间了哦')
        await asyncio.sleep(30)
        await r_msg.delete()
        await message.delete()
        return
    room = random.choice(available_rooms)
    if reservation.checkin_date > datetime.now(reservation.checkin_date.tzinfo):
        r_msg = await message.reply(f'亲亲请在入住日期当天来哦，现在是{datetime.now(cn_tz).strftime("%Y-%m-%d %H:%M:%S")}')
        await asyncio.sleep(30)
        await r_msg.delete()
        await message.delete()
        return
    room.room_status = room_status.occupied
    room.room_member.append(Member(message.from_user.first_name, room.room_number, message.from_user.id))
    await message.reply(
        f'亲亲您的房间是{room.room_number}，电梯在右手边左转，wifi 用您的 first name 加房间号连接，早餐是 7:00-9:00，行政酒廊开到晚上 10:00')
    return


async def handle_reservation(client: Client, message: Message):
    args = message.text.split(' ')
    if len(args) < 3:
        r_msg = await message.reply('亲亲请按照 /reserve [入住日期] [入住天数] [信用卡卡号] [姓名] [有效期] [账单地址] [cvv] 的格式预定哦')
        await asyncio.sleep(30)
        await r_msg.delete()
        await message.delete()
        return
    if len(args) > 3:
        if args[3] is not None and args[3].startswith('37'):
            r_msg = await message.reply('亲亲 no AMEX 哦')
            await asyncio.sleep(30)
            await r_msg.delete()
            await message.delete()
            return
    checkin_date = datetime.strptime(args[1], '%Y-%m-%d').replace(tzinfo=cn_tz)
    duration_days = timedelta(days=int(args[2]))
    reservations[message.from_user.id] = Reservation(checkin_date, duration_days, message.from_user.id)
    await message.reply('亲亲您的预定已经收到了，取消不退款哦')


async def handle_checkout(client: Client, message: Message):
    room_number = next((room_number for room_number, room in rooms.items() if
                        any(member.member_id == message.from_user.id for member in room.room_member)), None)
    if room_number is None:
        r_msg = await message.reply('亲亲找不到您的房间信息哦')
        await asyncio.sleep(10)
        await r_msg.delete()
        await message.delete()
        return
    room = rooms.get(room_number)
    room.room_status = room_status.available
    member = next((member for member in room.room_member if member.member_id == message.from_user.id), None)
    if member is not None:
        room.room_member = []
    await message.reply('亲亲慢走，receipt 会发到您的邮箱的哦')
