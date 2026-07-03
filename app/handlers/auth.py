import logging
import re
import smtplib
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import Keyboard as key
from app.DataBASE import Request as req
from app.config import VERIFICATION_CODE_TTL_MINUTES
from app.services.email_service import generate_verification_code, send_verification_code
from app.states import AuthStates

router = Router()
logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _menu_text(role: str) -> str:
    if role == "leader":
        return "Вы авторизованы как староста."
    return "Вы авторизованы как студент."


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    student = await req.get_student_by_telegram_id(message.from_user.id)

    if student is None:
        await message.answer(
            "Добро пожаловать! Для первого входа нажмите кнопку ниже.",
            reply_markup=key.register_button,
        )
        return

    role = req.resolve_role(student)
    await message.answer(_menu_text(role), reply_markup=key.get_main_menu(role))


@router.callback_query(F.data == "auth:start")
async def start_auth(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(AuthStates.waiting_email)
    await callback.message.answer("Введите ваш университетский email:")


@router.message(AuthStates.waiting_email)
async def process_email(message: Message, state: FSMContext) -> None:
    email = req.normalize_email(message.text or "")
    if not EMAIL_PATTERN.match(email):
        await message.answer("Некорректный формат email. Попробуйте снова.")
        return

    student = await req.get_student_by_email(email)
    if student is None:
        await message.answer("Email не найден в базе студентов.")
        return

    if student.tg_id and student.tg_id != message.from_user.id:
        await message.answer("Этот email уже привязан к другому Telegram-аккаунту.")
        return

    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_TTL_MINUTES)

    try:
        await send_verification_code(email, code)
    except RuntimeError as exc:
        logger.exception("SMTP is not configured")
        await message.answer(
            "SMTP не настроен: заполните SMTP_USER и SMTP_PASSWORD в .env, затем перезапустите бота."
        )
        return
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed")
        await message.answer(
            "SMTP отклонил авторизацию. Для Mail.ru нужен пароль приложения, а не обычный пароль от почты. "
            "Создайте пароль приложения в настройках безопасности почты и укажите его в SMTP_PASSWORD."
        )
        return
    except smtplib.SMTPRecipientsRefused:
        logger.exception("SMTP recipients refused")
        await message.answer(
            "SMTP отклонил отправку: адрес отправителя должен совпадать с авторизованным ящиком. "
            "Укажите одинаковые SMTP_USER и SMTP_FROM в .env."
        )
        return
    except smtplib.SMTPException:
        logger.exception("SMTP error during verification code sending")
        await message.answer(
            "Ошибка SMTP при отправке кода. Проверьте SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD и SMTP_FROM."
        )
        return
    except Exception:
        logger.exception("Failed to send verification code")
        await message.answer(
            "Не удалось отправить код на email. Проверьте SMTP настройки и попробуйте снова."
        )
        return

    await state.update_data(email=email, code=code, expires_at=expires_at.isoformat())
    await state.set_state(AuthStates.waiting_code)
    await message.answer("Код отправлен на email. Введите 6-значный код:")


@router.message(AuthStates.waiting_code)
async def process_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    code = (message.text or "").strip()

    expected = data.get("code")
    expires_at_raw = data.get("expires_at")
    email = data.get("email")

    if not expected or not expires_at_raw or not email:
        await state.clear()
        await message.answer("Сессия авторизации устарела. Нажмите /start и попробуйте снова.")
        return

    expires_at = datetime.fromisoformat(expires_at_raw)
    if datetime.utcnow() > expires_at:
        await state.clear()
        await message.answer("Срок действия кода истек. Нажмите /start для повторной авторизации.")
        return

    if code != expected:
        await message.answer("Неверный код. Попробуйте снова.")
        return

    student = await req.get_student_by_email(email)
    if student is None:
        await state.clear()
        await message.answer("Студент не найден. Обратитесь к администратору.")
        return

    await req.bind_telegram_id(student.id, message.from_user.id)
    role = req.resolve_role(student)

    await state.clear()
    await message.answer("Авторизация успешно завершена.")
    await message.answer(_menu_text(role), reply_markup=key.get_main_menu(role))
