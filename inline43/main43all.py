from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import token
from keyboards import inline_kb_full
from aiogram.dispatcher.filters import Text


# создание экземпляра класса бота передаем в него токен
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)

# создание диспетчера для управления обработчиками сообщение
dp = Dispatcher(bot, storage=MemoryStorage())


# Функция, реагирующая на команду start и возвращающая клавиатуру
@dp.message_handler(commands=['start'])
async def process_rm_command(message: types.Message):
    await message.reply('Inline', reply_markup=inline_kb_full)


# Функция, реагирующая на данные = button1
@dp.callback_query_handler(text='btn1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка')


@dp.callback_query_handler(Text(startswith=('btn')))
async def process_callback_btn(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 2:
        await bot.answer_callback_query(callback_query.id, text='Нажата вторая кнопка')
    elif code == 5:
        await bot.answer_callback_query(callback_query.id, text='Нажата кнопка 5\n текст не более 200 символов',
                                        show_alert=True)
    else:
        await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка {code}')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

