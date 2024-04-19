from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from config import admins


class IsUser(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id not in admins


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in admins