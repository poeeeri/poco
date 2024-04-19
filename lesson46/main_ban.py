import asyncio
import io
import logging
import traceback

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils.exceptions import BadRequest

from config import token

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()


class IsGroup(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand('set_photo', 'установить фото в группе'),
        types.BotCommand('set_title', 'установить название'),
        types.BotCommand('ro', 'read only'),
        types.BotCommand('unro', 'read only off'),
    ])


@dp.message_handler(IsGroup(), AdminFilter(), commands="set_photo")
async def set_new_photo(message: types.Message):
    photo = message.reply_to_message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())
    input_file = types.InputFile(path_or_bytesio=photo)
    await message.chat.set_photo(photo=input_file)


@dp.message_handler(IsGroup(), commands='ban')
async def ban_user(message: types.Message):
    try:
        member = message['reply_to_message']['from']['id']
        await bot.kick_chat_member(message.chat.id, member)

        chat_id = message.chat.id
        await message.chat.kick(user_id=member)
        await message.reply(f"пользователь был забанен")

    except Exception as err:
        print(message.as_json())
        await message.reply(traceback.format_exc())
        await message.reply(f"вы не админ")


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    await message.reply(f"Привет {message.new_chat_members[0].full_name}, в нашей группе запрещеные политичиские споры")


@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def ban_member(message: types.Message):
    await message.reply(f"Пользователь {message.left_chat_member.full_name}, покинул чат")


@dp.message_handler(IsGroup(), AdminFilter(), commands='unban')
async def unban_user(message: types.Message):
    print(message.as_json())
    member = message['reply_to_message']['from']['id']
    name = message['reply_to_message']['from']['first_name']
    chat_id = message.chat.id
    try:
        await message.chat.unban(user_id=member)
        await message.reply(f'Пользователь {name} был разбанен')
        await member
        service_message = await message.reply('Сообщение удалится через 5 секунд')
        await asyncio.sleep(5)
        await message.delete()
        await service_message.delete()
    except BadRequest:
        await message.reply('Вы не админ')


import re
import datetime


dp.filters_factory.bind(AdminFilter)


# @dp.message_handler(IsGroup(), AdminFilter(), commands='ro')
# async def read_only_mode(message: types.Message):
#     member = message['external_reply']['origin']['sender_user']['id']
#     chat_id = message.chat.id
#     command_parse = re.compile(r'(!ro|/ro) ?(\d+)? ?([a-zA-Z ])+?')
#     parsed = command_parse.match(message.text)
#     print(message.as_json())
#     time = parsed.group(2)
#     comment = parsed.group(3)
#     if not time:
#         time = 5
#     else:
#         time = int(time)
#     until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)
#     ReadOnlyPermission = types.ChatPermissions(
#         can_send_messages=False,
#         can_send_media_messages=False,
#         can_send_polls=False,
#         can_invite_users=False,
#         can_pin_messages=False,
#         can_change_info=False,
#         can_add_web_page_previews=False,
#     )
#     try:
#         await bot.restrict_chat_member(chat_id, user_id=member, permissions=ReadOnlyPermission, until_date=until_date)
#         await message.answer(f'Пользователю {member.get_mention(as_html=True)} запрещено писать на {time} минут
#         по причине {comment}')
#     except BadRequest:
#         logging.error(f'BadRequest {BadRequest}')
#         await message.answer('Пользователь является админом')
#         service_message = await message.reply('Сообщение удалится через 5 секунд')
#         await asyncio.sleep(5)
#         await message.delete()
#         await service_message.delete


@dp.message_handler(IsGroup(), AdminFilter(), commands='ro')
async def read_only_mode(message: types.Message):
    print(message.as_json())
    if not message.reply_to_message:
        member = message['reply_to_message']['from']['id']
    else:
        member = message.reply_to_message.from_user.id

    chat_id = message.chat.id
    command_parse = re.compile(r'(!ro|/ro) ?(\d+)? ?([a-zA-Z ])+?')
    parsed = command_parse.match(message.text)
    print(message.as_json())
    name = message['reply_to_message']['from']['username']
    time = 1
    reason = 'што за лев этот тигар'
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    ReadOnlyPermission = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_change_info=False,
        can_add_web_page_previews=False,
    )
    try:
        await bot.restrict_chat_member(chat_id, user_id=member, permissions=ReadOnlyPermission, until_date=until_date)
        await message.answer(f'Пользователю {name} запрещено писать на {time} минут '
                             f'по причине {reason}')
    except BadRequest as e:
        logging.error(f'BadRequest {e}')
        await message.answer('Пользователь является админом')
    service_message = await message.reply('Сообщение удалится через 5 секунд')
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
