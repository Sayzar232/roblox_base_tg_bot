import logging

from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMINS_IDS
from database import db
from utils import (
    ReportScammer,
    get_report_skip_keyboard,
    get_admin_report_keyboard,
    get_menu_keyboard,
)

logger = logging.getLogger(__name__)

router = Router()

NO_INFO_PLACEHOLDER = "Нет информации"

# Жалобы, ожидающие решения админа: {target_id: report_data}
# Нужна, т.к. кнопка "занести в базу скама" нажимается админом в его чате,
# где FSM-состояние автора жалобы недоступно.
pending_reports = {}


@router.message(ReportScammer.waiting_for_id)
async def handle_report_scammer_id(message: types.Message, state: FSMContext):
    argument = message.text.strip() if message.text else ""

    if not argument:
        await message.answer("❗ Пожалуйста, отправьте <b>id</b> или <b>@username</b> пользователя.")
        return

    if argument.lstrip("@").isdigit():
        target_id = int(argument.lstrip("@"))
    else:
        target_id = await db.get_user_id_by_username(argument)

        if target_id is None:
            await message.answer(
                "❗ Пользователь с таким @username не найден в базе данных.\n"
                "Пожалуйста, введите id пользователя."
            )
            return

    _, db_username, *_ = await db.get_user_type(target_id)

    await state.update_data(target_id=target_id, db_username=db_username)
    await state.set_state(ReportScammer.waiting_for_username)

    await message.answer(
        f"👤 <b>Пользователь:</b> <code>{target_id}</code>\n\n"
        "Теперь отправьте <b>@username</b> этого пользователя 👇\n"
        "Если он вам неизвестен — нажмите «Пропустить».",
        reply_markup=get_report_skip_keyboard(),
    )


@router.callback_query(ReportScammer.waiting_for_username, F.data == "report:skip")
async def handle_report_skip_username(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reported_username=None)
    await state.set_state(ReportScammer.waiting_for_reason)

    await callback.message.answer(
        "❗ Теперь опишите <b>причину жалобы</b> — что случилось:\n\n"
        "📎 Можно отправить текст или <b>фото с описанием</b> (пруфами)."
    )

    await callback.answer("Пропущено")


@router.message(ReportScammer.waiting_for_username)
async def handle_report_username(message: types.Message, state: FSMContext):
    username = message.text.strip().lstrip("@") if message.text else None

    if not username:
        await message.answer("❗ Пожалуйста, отправьте @username пользователя или нажмите «Пропустить».")
        return

    await state.update_data(reported_username=username)
    await state.set_state(ReportScammer.waiting_for_reason)

    await message.answer(
        "❗ Теперь опишите <b>причину жалобы</b> — что случилось:\n\n"
        "📎 Можно отправить текст или <b>фото с описанием</b> (пруфами)."
    )


@router.message(ReportScammer.waiting_for_reason, F.photo)
async def handle_report_reason_photo(message: types.Message, state: FSMContext):
    reason = message.caption.strip() if message.caption else "Нет описания"
    proof_photo_file_id = message.photo[-1].file_id

    await state.update_data(reason=reason, proof_photo_file_id=proof_photo_file_id)

    data = await state.get_data()
    await finish_report(message, state, data)


@router.message(ReportScammer.waiting_for_reason, F.text)
async def handle_report_reason(message: types.Message, state: FSMContext):
    reason = message.text.strip()

    if not reason:
        await message.answer("❗ Причина не может быть пустой. Опишите, что случилось:")
        return

    await state.update_data(reason=reason, proof_photo_file_id=None)

    data = await state.get_data()
    await finish_report(message, state, data)


@router.message(ReportScammer.waiting_for_reason)
async def handle_report_wrong_reason(message: types.Message):
    await message.answer("❗ Отправьте <b>текст</b> или <b>фото с описанием</b> причины жалобы:")


def build_report_text(data: dict, reporter: types.User) -> str:
    reported_username = data.get("reported_username") or data.get("db_username") or NO_INFO_PLACEHOLDER
    username_text = f"@{reporter.username}" if reporter.username else "нет @username"

    return (
        "🚨 <b>Новая жалоба на скам!</b>\n\n"
        f"👤 <b>Скаммер:</b> <code>{data.get('target_id')}</code>\n"
        f"🔗 <b>Username:</b> {reported_username}\n"
        f"❗ <b>Причина:</b> {data.get('reason')}\n\n"
        "ℹ <b>Отправитель жалобы:</b>\n"
        f"👤 {username_text}\n"
        f"ℹ <b>ID:</b> <code>{reporter.id}</code>"
    )


async def finish_report(message: types.Message, state: FSMContext, data: dict):
    target_id = data.get("target_id")

    pending_reports[target_id] = data

    report_text = build_report_text(data, message.from_user)
    kb = get_admin_report_keyboard(target_id)

    for admin_id in ADMINS_IDS:
        try:
            if data.get("proof_photo_file_id"):
                await message.bot.send_photo(
                    admin_id,
                    photo=data["proof_photo_file_id"],
                    caption=report_text,
                    reply_markup=kb,
                )
            else:
                await message.bot.send_message(admin_id, report_text, reply_markup=kb)
        except Exception as e:
            logger.warning("Failed to send report to admin %s: %s", admin_id, e)

    await state.clear()

    await message.answer(
        "✅ <b>Жалоба отправлена модераторам!</b>\n\n"
        "🔍 Они рассмотрят её и при подтверждении занесут пользователя в базу скаммеров.\n\n"
        "Спасибо, что помогаете делать сообщество безопаснее! 🙏",
        reply_markup=get_menu_keyboard(),
    )


@router.callback_query(F.data == "report:cancel")
async def handle_report_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer(
        "❌ Жалоба отменена. Возвращайтесь в меню 👇",
        reply_markup=get_menu_keyboard(),
    )

    await callback.answer("Отменено")


@router.callback_query(F.data.startswith("report:scam:"))
async def handle_report_add_scammer(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS_IDS:
        return

    try:
        target_id = int(callback.data.rsplit(":", 1)[1])
    except ValueError:
        await callback.answer("Некорректные данные жалобы", show_alert=True)
        return

    report = pending_reports.pop(target_id, None)

    if report is None:
        await callback.answer("Жалоба уже обработана или не найдена", show_alert=True)
        return

    reason = report.get("reason") or "Нет информации"
    proofs = "Фото-пруф приложено к жалобе" if report.get("proof_photo_file_id") else "Нет информации"
    username = report.get("reported_username") or report.get("db_username")

    # Создаём запись в users, если пользователя там нет,
    # иначе добавление в скаммеры упадёт из-за внешнего ключа
    await db.ensure_user_exists(target_id, username=username)
    await db.add_user_scammer(target_id, reason, proofs)

    status_text = "\n\n✅ <b>Пользователь занесён в базу скаммеров</b> ❌"

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=callback.message.caption + status_text)
        else:
            await callback.message.edit_text(callback.message.html_text + status_text)
    except Exception as e:
        logger.warning("Failed to edit report message for admin %s: %s", callback.from_user.id, e)

    await callback.answer("✅ Занесён в базу скама", show_alert=True)