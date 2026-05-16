import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ─── CONFIG ────────────────────────────────────────────────────────────────────
TOKEN = "8747421328:AAHwxVAA3bU-bEwHQ4BVoJRRctw9xavXkLA"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ─── DATA: GUIDES ─────────────────────────────────────────────────────────────
GUIDES = {
    "study": {
        "title": "📚 Учёба",
        "text": (
            "<b>📚 Всё об учёбе в Московском Политехе</b>\n\n"
            "<b>🔑 Личный кабинет студента</b>\n"
            "Зайти можно на <a href='https://lk.mospolytech.ru'>lk.mospolytech.ru</a>\n"
            "Там: расписание, оценки, зачётная книжка, заявления.\n\n"
            "<b>📅 Расписание</b>\n"
            "• Расписание пар — в ЛК и на сайте\n"
            "• Пары: 1⃣ 9:00–10:30 | 2⃣ 10:45–12:15\n"
            " 3⃣ 13:00–14:30 | 4⃣ 14:45–16:15\n"
            " 5⃣ 16:30–18:00 | 6⃣ 18:15–19:45\n\n"
            "<b>📝 Сессия</b>\n"
            "• Зимняя: январь–февраль\n"
            "• Летняя: июнь\n\n"
            "<b>💡 Лайфхак</b>\n"
            "Не пропускай первые недели — именно тогда преподаватели формируют мнение о тебе."
        ),
    },
    "dormitory": {
        "title": "🏠 Общежития",
        "text": (
            "<b>🏠 Общежития Московского Политеха</b>\n\n"
            "У Политеха несколько общежитий в разных районах Москвы.\n\n"
            "<b>💰 Стоимость и правила</b>\n"
            "Актуальную информацию смотри на официальном сайте.\n\n"
            "<b>📞 Диспетчерская общежитий</b>\n"
            "+7 (499) 972-94-00"
        ),
    },
    "food": {
        "title": "🍽 Еда на кампусе",
        "text": (
            "<b>🍽 Где поесть в Московском Политехе</b>\n\n"
            "<b>🏛 Столовые</b>\n"
            "• Главный корпус (Б. Семёновская, 38) — 1 этаж\n"
            "• Корпус на Прянишникова — столовая на 2 этаже\n\n"
            "<b>💸 Средний чек</b>\n"
            "~200–350 ₽ за полноценный обед\n\n"
            "<b>💡 Совет</b>\n"
            "Приноси еду из дома — везде есть микроволновки."
        ),
    },
    "help": {
        "title": "🤝 Помощь студентам",
        "text": (
            "<b>🤝 Виды помощи для студентов</b>\n\n"
            "<b>💊 Медицинская</b>\n"
            "Здравпункт в главном корпусе\n\n"
            "<b>💰 Стипендии и материальная помощь</b>\n"
            "• Академическая\n"
            "• Социальная\n"
            "• Повышенная\n\n"
            "<b>🧠 Психологическая</b>\n"
            "Психологическая служба Политеха — бесплатно."
        ),
    },
    "lk": {
        "title": "💻 Личный кабинет",
        "text": (
            "<b>💻 Личный кабинет студента</b>\n\n"
            "<b>🔗 Адрес:</b> <a href='https://lk.mospolytech.ru'>lk.mospolytech.ru</a>\n\n"
            "В ЛК можно:\n"
            "• Смотреть расписание\n"
            "• Проверять оценки\n"
            "• Подавать заявления\n"
            "• Записываться на дисциплины"
        ),
    },
    "studentlife": {
        "title": "🎭 Студенческая жизнь",
        "text": (
            "<b>🎭 Студенческая жизнь в Политехе</b>\n\n"
            "<b>🎨 Творчество</b>\n"
            "Танцы, театр, музыка и многое другое.\n\n"
            "<b>🏆 Спорт</b>\n"
            "Секции по футболу, баскетболу, киберспорту и др.\n\n"
            "<b>🌱 Волонтёрство и карьера</b>\n"
            "Много возможностей для развития."
        ),
    },
    "international": {
        "title": "🌍 Иностранным студентам",
        "text": (
            "<b>🌍 Иностранным студентам</b>\n\n"
            "• Миграционный учёт в течение 7 дней\n"
            "• Международный отдел поможет с документами"
        ),
    },
    "science": {
        "title": "🔬 Наука и исследования",
        "text": (
            "<b>🔬 Наука в Политехе</b>\n\n"
            "Лаборатории, конкурсы, гранты УМНИК и возможность участвовать в исследованиях уже с 1 курса."
        ),
    },
}

# ─── TIPS ──────────────────────────────────────────────────────────────────────
TIPS = [
    "☕ Заведи знакомство с преподавателями с первых дней — они любят активных студентов!",
    "📱 Вступи в групповой чат своей учебной группы сразу.",
    "🗓 Записывай дедлайны в календарь телефона.",
    "💤 Сон 7–8 часов сильно повышает эффективность учёбы.",
    "🚇 Купи карту «Тройка» — выгоднее разовых билетов.",
    "📝 Ходи на все первые лекции — там объясняют систему оценки.",
]

CONTACTS = """
<b>📞 Важные контакты Московского Политеха</b>

🏛 <b>Главный корпус</b>
Большая Семёновская ул., 38

📞 <b>Приёмная комиссия</b>
+7 (499) 972-94-07

🏥 <b>Здравпункт</b>
+7 (499) 972-94-00 (доб. 21-03)

🧠 <b>Психологическая служба</b>
psychology@mospolytech.ru

🌍 <b>Международный отдел</b>
inter@mospolytech.ru

💻 <b>Техподдержка ЛК</b>
help@mospolytech.ru
"""

MAP_TEXT = """
<b>📍 Адреса и кампус Московского Политеха</b>

<b>🏛 Главный корпус</b>
• Большая Семёновская ул., 38 (м. Семёновская)

<b>📍 Основные корпуса</b>
• Большая Семёновская, 38
• Павла Корчагина, 22
• Прянишникова, 2А
• Автозаводская, 16

<b>🏠 Общежития</b>
• Малая Семёновская, 12
• 7-я Парковая, 9/26
• 1-я Дубровская, 16А
• 800-летия Москвы, 28 к.1
• Бориса Галушкина, 9
• Павла Корчагина, 20А и 22А

<b>🔗 Официальная информация</b>
<a href='https://mospolytech.ru/ob-universitete/adresa-i-kontakty/'>Все адреса и контакты</a>

<b>💡 Совет</b>
Заранее посмотри на карте, где находится твой корпус и общежитие — в первый день это очень поможет!
"""

# ─── KEYBOARDS ─────────────────────────────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Гайды для первокурсника")],
            [KeyboardButton(text="📍 Карта кампуса")],
            [KeyboardButton(text="📞 Важные контакты"), KeyboardButton(text="💡 Совет дня")],
            [KeyboardButton(text="🌐 Электронная брошюра")],
        ],
        resize_keyboard=True,
    )


def guides_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data["title"], callback_data=f"guide_{key}")]
        for key, data in GUIDES.items()
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_guides_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ К гайдам", callback_data="back_guides")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_main")],
    ])


# ─── HANDLERS ──────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    name = message.from_user.first_name or "студент"
    await message.answer(
        f"👋 Привет, <b>{name}</b>!\n\n"
        "Я — бот-помощник первокурсника <b>Московского Политеха</b> 🎓\n\n"
        "Здесь ты найдёшь всё самое важное для начала учёбы!",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>🤖 Команды бота</b>\n\n"
        "/start — Главное меню\n"
        "/guides — Гайды\n"
        "/contacts — Контакты\n"
        "/tip — Совет дня\n"
        "/map — Карта кампуса",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ── GUIDES ─────────────────────────────────────────────────────────────────────
@dp.message(F.text == "📚 Гайды для первокурсника")
@dp.message(Command("guides"))
async def show_guides_menu(message: Message):
    await message.answer(
        "📚 <b>Выбери тему</b>",
        parse_mode="HTML",
        reply_markup=guides_kb(),
    )


@dp.callback_query(F.data.startswith("guide_"))
async def show_guide(callback: CallbackQuery):
    key = callback.data.replace("guide_", "")
    guide = GUIDES.get(key)
    if not guide:
        await callback.answer("Раздел не найден")
        return
    await callback.message.edit_text(
        guide["text"],
        parse_mode="HTML",
        reply_markup=back_guides_kb(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@dp.callback_query(F.data == "back_guides")
async def back_to_guides(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 <b>Выбери тему</b>",
        parse_mode="HTML",
        reply_markup=guides_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ── MAP ───────────────────────────────────────────────────────────────────────
@dp.message(F.text == "📍 Карта кампуса")
@dp.message(Command("map"))
async def map_handler(message: Message):
    await message.answer(
        MAP_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# ── TIP / CONTACTS / BROCHURE ────────────────────────────────────────────────
@dp.message(F.text == "💡 Совет дня")
@dp.message(Command("tip"))
async def tip_handler(message: Message):
    tip = random.choice(TIPS)
    await message.answer(
        f"💡 <b>Совет от старшекурсника</b>\n\n{tip}",
        parse_mode="HTML",
    )


@dp.message(F.text == "📞 Важные контакты")
@dp.message(Command("contacts"))
async def contacts_handler(message: Message):
    await message.answer(CONTACTS, parse_mode="HTML", disable_web_page_preview=True)


@dp.message(F.text == "🌐 Электронная брошюра")
@dp.message(Command("brochure"))
async def brochure_handler(message: Message):
    await message.answer(
        "🌐 <b>Электронная брошюра «В помощь первокурснику»</b>\n\n"
        "🔗 <a href='https://pd-chi-khaki.vercel.app/'>pd-chi-khaki.vercel.app</a>",
        parse_mode="HTML",
        disable_web_page_preview=False,
    )


# ── FALLBACK ───────────────────────────────────────────────────────────────────
@dp.message()
async def fallback(message: Message):
    await message.answer(
        "🤔 Не понял команду. Воспользуйся меню ниже или напиши /help",
        reply_markup=main_menu_kb(),
    )


# ─── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    print("🤖 Бот «В помощь первокурснику» успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
