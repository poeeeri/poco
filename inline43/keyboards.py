from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='btn1')
inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
inline_kb_full.add(InlineKeyboardButton('Вторая кнопка', callback_data='btn2'))
inline_btn_3 = InlineKeyboardButton('Третья кнопка!', callback_data='btn3')
inline_btn_4 = InlineKeyboardButton('Четвертая кнопка!', callback_data='btn4')
inline_btn_5 = InlineKeyboardButton('Пятая кнопка!', callback_data='btn5')

inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.insert(InlineKeyboardButton("query='qwerty'", switch_inline_query=''))

inline_kb_full.insert(InlineKeyboardButton("query='qwerty'", switch_inline_query='привет'))
inline_kb_full.insert(InlineKeyboardButton("Inline в этом же чате", switch_inline_query_current_chat='qwerty'))
inline_kb_full.insert(InlineKeyboardButton('Яндекс', url='https://ya.ru'))



