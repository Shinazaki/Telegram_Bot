from aiogram import F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.Keyboard as key
import app.DataBASE.Request as req
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Добро пожаловать, ввойдите", reply_markup = key.Register_button)
    
@router.callback_query(F.data == "register")
async def register(callback:CallbackQuery,):
    await callback.message.answer(text="Введите ФИО",reply_markup=key.choose_reason)


@router.message(F.text)
async def recieve(message: Message):
    await req.get_student_SNF(message)
    
# @router.message()
# async def recieve(message: Message,state:FSMContext):


# @router.message()
# async def recieve(message: Message,state:FSMContext):
