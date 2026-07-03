import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.DataBASE import Request as req
from app.services.report_service import build_group_report

router = Router()


async def _build_report_for_user(bot_user_id: int) -> tuple[str | None, str | None]:
    student = await req.get_student_by_telegram_id(bot_user_id)
    if student is None:
        return "Сначала выполните вход через /start", None

    role = req.resolve_role(student)
    if role != "leader":
        return "Отчет доступен только старосте группы.", None

    rows = await req.get_group_absences_for_leader(student.id)
    if not rows:
        return "По вашей группе пока нет записей о пропусках.", None

    report_path = build_group_report(rows, student.group)
    return None, str(report_path)


async def _send_report_to_message(message: Message) -> None:
    error_text, report_path_raw = await _build_report_for_user(message.from_user.id)

    if error_text:
        await message.answer(error_text)
        return

    report_path = report_path_raw or ""
    try:
        await message.answer_document(
            document=FSInputFile(report_path),
            caption="Отчет по пропускам вашей группы.",
        )
    finally:
        if report_path and os.path.exists(report_path):
            os.remove(report_path)


async def _send_report_to_callback(callback: CallbackQuery) -> None:
    error_text, report_path_raw = await _build_report_for_user(callback.from_user.id)

    if error_text:
        await callback.message.answer(error_text)
        return

    report_path = report_path_raw or ""
    try:
        await callback.message.answer_document(
            document=FSInputFile(report_path),
            caption="Отчет по пропускам вашей группы.",
        )
    finally:
        if report_path and os.path.exists(report_path):
            os.remove(report_path)


@router.callback_query(F.data == "report:group")
async def callback_group_report(callback: CallbackQuery) -> None:
    await callback.answer()
    await _send_report_to_callback(callback)


@router.message(Command("report"))
async def command_group_report(message: Message) -> None:
    await _send_report_to_message(message)
