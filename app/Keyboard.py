from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
Register_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Войти",callback_data="register") ]
])
                           
choose_reason = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Уважительная",callback_data="serious_reason"),InlineKeyboardButton(text="Неуважительная",callback_data="not_serious_reason") ]
])