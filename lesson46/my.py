import asyncio
import io
import logging
import traceback
from pprint import pprint
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter
from datetime import datetime, timedelta, time
import requests
from aiogram.utils.exceptions import BadRequest

from config import token, WEATHER_API

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
        if not message['reply_to_message']['from']['id']:
            member = message['external_reply']['origin']['sender_user']['id']
        else:
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

# @dp.message_handler()
# async def del_m(message: types.Message):
#    await bot.delete_message(message.chat.id, message.message_id)

#
commands = [
    types.BotCommand(command='cube', description='скидывает эмодзи кубика'),
    types.BotCommand(command='bascetball', description='скидывает эмодзи баскетбольного мяча'),
    types.BotCommand(command='drotiki', description='скидывает эмодзи дротиков'),
    types.BotCommand(command='football', description='скидывает эмодзи футбольного мяча'),
    types.BotCommand(command='bascetball', description='скидывает эмодзи баскетбольного мяча'),
    types.BotCommand(command='casino', description='скидывает эмодзи казино'),
    types.BotCommand(command='weather', description='сообщение с погодой в уу на сегодня'),
]


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
       types.BotCommand('set_photo', 'установить фотов группе'),
       types.BotCommand('set_title', 'установить название группы'),
       types.BotCommand('ro', 'read only'),
       types.BotCommand('unro', 'read only off'),
       types.BotCommand('dice', 'read only off'),
       types.BotCommand('casino', 'read only off'),
    ])


@dp.message_handler(IsGroup(), commands='set_photo')
async def set_new_photo(message: types.Message):
    source_message = message.reply_to_message
    photo = source_message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())
    # Асинхронная загрузка фото и сохранение ее в объекте
    input_file = types.InputFile(path_or_bytesio=photo)
    await message.chat.set_photo(photo=input_file)


@dp.message_handler(commands='about')
async def about(message: types.Message):
    await message.answer('Команды бота:\n'
                        '/bascetball - скидывает эмодзи баскетбольного мяча\n'
                        '/cube - скидывает эмодзи кубика \n'
                        '/drotiki - скидывает дротиков \n'
                        '/football - скидывает эмодзи футбольного мяча \n'
                        '/casino - скидывает эмодзи казино')


@dp.message_handler(commands='set_cmds')
async def set_cmds(message: types.Message):
    await message.answer('Команды для бота установлены')
    await bot.set_my_commands(commands)


@dp.message_handler(commands='cube')
async def dice(message: types.Message):
    await message.reply_dice('🎲')
    print(message.reply_to_message.as_json())


@dp.message_handler(commands='drotiki')
async def dice(message: types.Message):
    await message.reply_dice('🎯')


@dp.message_handler(commands='casino')
async def dice(message: types.Message):
    await message.reply_dice('🎰')


@dp.message_handler(commands='football')
async def dice(message: types.Message):
    await message.reply_dice('⚽')


@dp.message_handler(commands='bascetball')
async def dice(message: types.Message):
    await message.reply_dice('🏀')


@dp.message_handler(commands='weather')
async def echo(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Ясно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    try:
        par = {
            "lang": "ru",
            "lat": 51.8261,
            "lon": 107.6098,
            "appid": WEATHER_API,
            "units": "metric"
        }
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q=Ulan-Ude&appid={WEATHER_API}&units=metric')
        data = r.json()
        city = data['name']
        cur_weather = data['main']['temp']
        r_hourly = requests.get('http://api.openweathermap.org/data/2.5/forecast?', params=par)
        re = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q=Ulan-Ude,643&appid={WEATHER_API}')
        pprint(re)

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Посмотри в окно сам'
        humidity = data['main']["humidity"]
        pressure = data['main']['pressure']
        sunrise_timestamp = datetime.date.fromtimestamp(data['sys']['sunrise']).strftime('в %H:%M')
        sunset_timestamp = datetime.date.fromtimestamp(data['sys']['sunset']).strftime('в %H:%M')
        length_of_the_day = datetime.date.fromtimestamp(data['sys']['sunset']) - \
                            datetime.date.fromtimestamp(data['sys']['sunrise'])
        wind = data['wind']['speed']
        await message.answer(f'***{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}***\n'
                             f'Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n'
                             f'Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/c\n'
                             f'Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n'
                             f'Хорошего дня братки!\n\n\n')
        forecast = r_hourly.json().get('list')[:5]

        # for i in forecast:
        #     dt = i.get('dt_txt')
        #     print(dt, ':')
        #
        #     print("Будет {}".format(i.get("weather")[0].get("description")))
        #     print("Подробно:")
        #     print("	Температура:", i.get("main").get("temp"), "*C")
        #     print("	Влажность:", i.get("main").get("humidity"), "%")
        #     press = int(i.get("main").get("pressure"))
        #     print("	Давление(мм.рт.ст):", press / 133)
        #     print("-----------------------------------------------------------------------------")
        x = 0
        for i in forecast:
            dt = i.get('dt_txt')
            x += 3

            des = "Будет {}".format(i.get("weather")[0].get("description"))
            temp = i.get("main").get("temp")
            print("	Влажность:", i.get("main").get("humidity"), "%")
            press = int(i.get("main").get("pressure"))
            print("	Давление(мм.рт.ст):", press / 133)
            print("-----------------------------------------------------------------------------")
            time = datetime.datetime.now() + timedelta(hours=x)
            await message.answer(f'{str(time)[:16]}:\n'
                                 f'Температура: {temp}C°\n'
                                 f'{des}')

            # temp = i.get("main").get("temp")
            # des = i.get("weather")[0].get("description")
            # pprint(dt)
    except Exception as err:
        await message.reply('какая-то ошибочка!')
        await message.reply(traceback.format_exc())
        pprint(data)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
