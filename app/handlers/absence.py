from datetime import date, datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import Keyboard as key
from app.DataBASE import Request as req
from app.states import AbsenceStates

router = Router()


def _reason_label(reason_type: str) -> str:
    return "Официальная" if reason_type == "official" else "Неофициальная"


async def _check_authorized(message: Message) -> tuple[bool, object | None]:
    student = await req.get_student_by_telegram_id(message.from_user.id)
    if student is None:
        await message.answer("Сначала выполните вход через /start")
        return False, None
    return True, student


async def _check_authorized_callback(
    callback: CallbackQuery,
) -> tuple[bool, object | None]:
    student = await req.get_student_by_telegram_id(callback.from_user.id)
    if student is None:
        await callback.answer("Сначала выполните вход", show_alert=True)
        return False, None
    return True, student


@router.callback_query(F.data == "absence:start")
async def start_absence(callback: CallbackQuery, state: FSMContext) -> None:
    ok, _student = await _check_authorized_callback(callback)
    if not ok:
        return

    await callback.answer()
    await state.set_state(AbsenceStates.waiting_date_choice)
    await callback.message.answer(
        "Выберите дату отсутствия:", reply_markup=key.absence_date_keyboard
    )


@router.callback_query(F.data.startswith("absence:date:"))
async def choose_absence_date(callback: CallbackQuery, state: FSMContext) -> None:
    ok, _student = await _check_authorized_callback(callback)
    if not ok:
        return

    await callback.answer()
    date_choice = callback.data.split(":")[-1]

    if date_choice == "custom":
        await state.set_state(AbsenceStates.waiting_custom_date)
        await callback.message.answer("Введите дату в формате ГГГГ-ММ-ДД:")
        return

    target_date = date.today()
    if date_choice == "tomorrow":
        target_date = date.today() + timedelta(days=1)

    await state.update_data(absence_date=target_date.isoformat())
    await state.set_state(AbsenceStates.waiting_reason)
    await callback.message.answer(
        "Выберите тип причины:", reply_markup=key.absence_reason_keyboard
    )


@router.message(AbsenceStates.waiting_custom_date)
async def process_custom_date(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    try:
        target_date = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
        return

    if target_date < date.today():
        await message.answer("Дата не может быть в прошлом. Введите корректную дату.")
        return

    await state.update_data(absence_date=target_date.isoformat())
    await state.set_state(AbsenceStates.waiting_reason)
    await message.answer("Выберите тип причины:", reply_markup=key.absence_reason_keyboard)


@router.callback_query(F.data.startswith("absence:reason:"))
async def choose_reason(callback: CallbackQuery, state: FSMContext) -> None:
    ok, student = await _check_authorized_callback(callback)
    if not ok:
        return

    await callback.answer()
    data = await state.get_data()
    target_date_raw = data.get("absence_date")
    if not target_date_raw:
        await state.clear()
        await callback.message.answer("Дата не выбрана. Начните заново.")
        return

    target_date = datetime.strptime(target_date_raw, "%Y-%m-%d").date()
    reason_type = callback.data.split(":")[-1]

    if reason_type == "official":
        await state.update_data(reason_type=reason_type)
        await state.set_state(AbsenceStates.waiting_photo)
        await callback.message.answer("Пришлите фото подтверждающего документа.")
        return

    await req.create_absence(student.id, target_date, reason_type, None)
    await state.clear()
    await callback.message.answer(
        f"Заявка сохранена: {target_date.isoformat()}, {_reason_label(reason_type)}."
    )


@router.message(AbsenceStates.waiting_photo, F.photo)
async def process_document_photo(message: Message, state: FSMContext) -> None:
    ok, student = await _check_authorized(message)
    if not ok or student is None:
        return

    data = await state.get_data()
    target_date_raw = data.get("absence_date")
    reason_type = data.get("reason_type", "official")
    if not target_date_raw:
        await state.clear()
        await message.answer("Сессия создания заявки устарела. Начните заново.")
        return

    target_date = datetime.strptime(target_date_raw, "%Y-%m-%d").date()
    photo_file_id = message.photo[-1].file_id

    await req.create_absence(student.id, target_date, reason_type, photo_file_id)
    await state.clear()
    await message.answer("Заявка с официальной причиной и документом сохранена.")


@router.message(AbsenceStates.waiting_photo)
async def process_document_wrong_type(message: Message) -> None:
    await message.answer("Ожидаю фото документа. Отправьте изображение.")
