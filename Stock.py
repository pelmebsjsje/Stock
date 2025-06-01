import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from bs4 import BeautifulSoup

# Настройки через переменные окружения
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
STOCK_CHANNEL_ID = os.environ.get('STOCK_CHANNEL_ID', '@autostockgag')
REQUIRED_CHANNELS = [os.environ.get('REQUIRED_CHANNEL', '@autostockgag')]
CHANNEL_LINKS = {'@autostockgag': 'https://t.me/autostockgag'}
STOCK_URL = 'https://www.vulcanvalues.com/grow-a-garden/stock'

USER_PREFS_FILE = "user_prefs.json"
POSTS_DB_FILE = "posted_msgs.json"
LAST_USER_STOCK_FILE = "last_user_stock.json"

SECTION_TITLES = {
    'GEAR STOCK': 'Предметы',
    'EGG STOCK': 'Яйца',
    'SEEDS STOCK': 'Семена'
}
SECTION_EMOJI = {
    'GEAR STOCK': '🛠️',
    'EGG STOCK': '🥚',
    'SEEDS STOCK': '🌱'
}
SECTION_LIST = ['GEAR STOCK', 'EGG STOCK', 'SEEDS STOCK']

ITEM_TRANSLATE = {
    'Watering Can': 'Лейка',
    'Favorite Tool': 'Инструмент любви',
    'Recall Wrench': 'Ключ возврата',
    'Trowel': 'Совок',
    'Basic Sprinkler': 'Обычный разбрызгиватель',
    'Advanced Sprinkler': 'Улучшенный разбрызгиватель',
    'Godly Sprinkler': 'Годли разбрызгиватель',
    'Master Sprinkler': 'Мастер разбрызгиватель',
    'Shovel': 'Лопата',
    'Lightning Rod': 'Громовод',
    'Common Egg': 'Обычное яйцо',
    'Uncommon Egg': 'Необычное яйцо',
    'Rare Egg': 'Редкое яйцо',
    'Bug Egg': 'Баг яйцо',
    'Legendary Egg': 'Легендарное яйцо',
    'Mythical Egg': 'Мифическое яйцо',
    'Carrot': 'Морковь',
    'Strawberry': 'Клубника',
    'Coconut': 'Кокос',
    'Tomato': 'Томат',
    'Blueberry': 'Черника',
    'Apple': 'Яблоко',
    'Banana': 'Банан',
    'Pineapple': 'Ананас',
    'Grape': 'Виноград',
    'Watermelon': 'Арбуз',
    'Peach': 'Персик',
    'Mango': 'Манго',
    'Cherry': 'Вишня',
    'Raspberry': 'Малина',
    'Blackberry': 'Ежевика',
    'Pumpkin': 'Тыква',
    'Eggplant': 'Баклажан',
    'Corn': 'Кукуруза',
    'Pepper': 'Перец',
    'Bamboo': 'Бамбук',
    'Cactus': 'Кактус',
    'Dragon Fruit': 'Драконий фрукт',
    'Mushroom': 'Мухомор',
    'Cacao': 'Какао',
    'Beanstalk': 'Бобы',
    'Orange Tulip': 'Оранжевый тюльпан',
    'Daffodil': 'Нарцисс',
}
ITEM_EMOJI = {
    'Лейка': '💧', 'Инструмент любви': '💖', 'Ключ возврата': '🔧', 'Совок': '🪣',
    'Обычный разбрызгиватель': '🚿', 'Улучшенный разбрызгиватель': '🚿',
    'Годли разбрызгиватель': '🌟', 'Мастер разбрызгиватель': '🏆', 'Лопата': '🛠️', 'Громовод': '⚡️',
    'Морковь': '🥕', 'Клубника': '🍓', 'Кокос': '🥥', 'Томат': '🍅', 'Черника': '🫐',
    'Яблоко': '🍏', 'Банан': '🍌', 'Ананас': '🍍', 'Виноград': '🍇', 'Арбуз': '🍉',
    'Персик': '🍑', 'Манго': '🥭', 'Вишня': '🍒', 'Малина': '🍇', 'Ежевика': '🍇',
    'Тыква': '🎃', 'Баклажан': '🍆', 'Кукуруза': '🌽', 'Перец': '🌶️', 'Бамбук': '🎋',
    'Кактус': '🌵', 'Драконий фрукт': '🐉', 'Мухомор': '🍄', 'Какао': '🍫', 'Бобы': '🌱',
    'Оранжевый тюльпан': '🌷', 'Нарцисс': '🌼',
}
EGG_COLOR = {
    'Обычное яйцо': '⚪️', 'Необычное яйцо': '🟤', 'Редкое яйцо': '💙',
    'Баг яйцо': '🟢', 'Легендарное яйцо': '🟡', 'Мифическое яйцо': '🟥',
}

GEAR_ENG = [
    'Watering Can','Favorite Tool','Recall Wrench','Trowel','Basic Sprinkler','Advanced Sprinkler','Godly Sprinkler','Master Sprinkler','Shovel','Lightning Rod'
]
EGGS_ENG = [
    'Common Egg','Uncommon Egg','Rare Egg','Bug Egg','Legendary Egg','Mythical Egg'
]
SEEDS_ENG = [en for en in ITEM_TRANSLATE if en not in GEAR_ENG+EGGS_ENG]

def load_json_file(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_period(section_name):
    now = datetime.now()
    if section_name == 'GEAR STOCK' or section_name == 'SEEDS STOCK':
        minute = now.minute - (now.minute % 5)
        start = now.replace(minute=minute, second=0, microsecond=0)
        end = start + timedelta(minutes=5)
    elif section_name == 'EGG STOCK':
        minute = 0 if now.minute < 30 else 30
        start = now.replace(minute=minute, second=0, microsecond=0)
        end = start + timedelta(minutes=30)
    else:
        start = now
        end = now
    return start.strftime('%H:%M'), end.strftime('%H:%M')

async def fetch_stock():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(STOCK_URL, timeout=10) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                stocks = {}
                for section in SECTION_LIST:
                    stocks[section] = parse_section_stock(soup, section)
                return stocks
        except Exception as e:
            print(f"Ошибка загрузки стока: {e}")
            return {section: [] for section in SECTION_LIST}

def parse_section_stock(soup, section_title):
    section = None
    for h2 in soup.find_all('h2'):
        if h2.get_text(strip=True).upper() == section_title:
            section = h2
            break
    if not section:
        return []
    ul = section.find_next('ul')
    if not ul:
        return []
    items = []
    for li in ul.find_all('li'):
        spans = li.find_all('span')
        if not spans:
            continue
        main_span = spans[0]
        name = main_span.contents[0].strip()
        qty_span = main_span.find('span')
        qty = None
        if qty_span:
            qty = qty_span.get_text(strip=True).replace('x', '')
        for en, ru in ITEM_TRANSLATE.items():
            if name.startswith(en):
                name = name.replace(en, ru, 1)
        emoji = ITEM_EMOJI.get(name, '')
        if name in EGG_COLOR:
            emoji = f"{EGG_COLOR[name]}"
        if qty and qty != "1":
            items.append(f"<b>•</b> {emoji} {name} x{qty}")
        else:
            items.append(f"<b>•</b> {emoji} {name}")
    return items

def make_stock_block(items, section_eng):
    start, end = get_period(section_eng)
    rus_title = SECTION_TITLES.get(section_eng, section_eng)
    emoji = SECTION_EMOJI.get(section_eng, '')
    body = "\n".join(items) if items else ""
    block = (
        f"<b>{emoji} {rus_title.upper()}</b>\n"
        f"<b>Действует:</b> <u>{start}</u> — <u>{end}</u>\n"
        f"{body}\n"
        f"<b>─────────────</b>\n"
    )
    return block

def filter_stocks_for_user(stocks, prefs):
    if prefs.get('mode') == 'all':
        return stocks
    chosen_items = prefs.get('chosen_items', {})
    filtered = {}
    for section in SECTION_LIST:
        allowed = set(chosen_items.get(section, []))
        if allowed:
            filtered[section] = [x for x in stocks[section] if any(n in x for n in allowed)]
        else:
            filtered[section] = []
    return filtered

# Telegram bot setup
bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# FastAPI app
app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

# Функции рассылки и логики
async def post_to_telegram(msg, chat_id, reply_markup=None):
    try:
        reply_markup_obj = None
        if reply_markup:
            reply_markup_obj = reply_markup
        await bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=reply_markup_obj)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

async def stock_poster():
    # Для простоты — prefs/last_user_stock храним в памяти и иногда сохраняем на диск
    user_prefs = load_json_file(USER_PREFS_FILE, {})
    last_user_stock = load_json_file(LAST_USER_STOCK_FILE, {})
    prev_stock = None
    while True:
        stocks = await fetch_stock()
        has_data = any(stocks[section] for section in SECTION_LIST)
        if has_data and stocks != prev_stock:
            msg = (
                "✨ Актуальный СТОК Grow a Garden ✨\n"
                "──────────────────────────────\n\n"
                f"{make_stock_block(stocks['GEAR STOCK'], 'GEAR STOCK') if stocks['GEAR STOCK'] else ''}"
                f"{make_stock_block(stocks['EGG STOCK'], 'EGG STOCK') if stocks['EGG STOCK'] else ''}"
                f"{make_stock_block(stocks['SEEDS STOCK'], 'SEEDS STOCK') if stocks['SEEDS STOCK'] else ''}"
                "──────────────────────────────\n"
                "🤍 Сделано командой @sbtdrasik для вашего удобства 🤍"
            )
            await post_to_telegram(msg, STOCK_CHANNEL_ID)
            # Рассылка пользователям
            for user_id in list(user_prefs.keys()):
                prefs = user_prefs.get(str(user_id), {'mode': 'all'})
                user_stocks = filter_stocks_for_user(stocks, prefs)
                blocks = []
                for section in SECTION_LIST:
                    if prefs.get("mode") == "all" or user_stocks[section]:
                        blocks.append(make_stock_block(user_stocks[section], section))
                if any(user_stocks[section] for section in SECTION_LIST) or prefs.get("mode") == "all":
                    ls_msg = (
                        "✨ Ваши выбранные категории стока: ✨\n"
                        "─────────────────────\n\n" +
                        "".join(blocks) +
                        "─────────────────────\n"
                        "🤍 Сделано командой @sbtdrasik 🤍"
                    )
                    if last_user_stock.get(user_id) != ls_msg:
                        await post_to_telegram(ls_msg, user_id)
                        last_user_stock[user_id] = ls_msg
            save_json_file(LAST_USER_STOCK_FILE, last_user_stock)
            prev_stock = stocks
        await asyncio.sleep(60)

@app.on_event("startup")
async def on_startup():
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        await bot.set_webhook(f"{webhook_url}/webhook")
    asyncio.create_task(stock_poster())  # Запуск рассылки стока

# Пример базового хендлера на команды
@dp.message(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Добро пожаловать! Вы будете получать сток в личку, если подписаны на канал.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
