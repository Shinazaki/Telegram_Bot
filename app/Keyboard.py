from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


register_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Войти", callback_data="auth:start")]]
)


def get_main_menu(role: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="Сообщить об отсутствии", callback_data="absence:start")]]
    if role == "leader":
        rows.append([InlineKeyboardButton(text="Получить отчет", callback_data="report:group")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


absence_date_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="absence:date:today")],
        [InlineKeyboardButton(text="Завтра", callback_data="absence:date:tomorrow")],
        [InlineKeyboardButton(text="Выбрать дату", callback_data="absence:date:custom")],
    ]
)


absence_reason_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Официальная", callback_data="absence:reason:official")],
        [InlineKeyboardButton(text="Неофициальная", callback_data="absence:reason:unofficial")],
    ]
)