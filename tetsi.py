import requests
from bs4 import BeautifulSoup
import time
import json
import os
import threading
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = '7658214419:AAEWOkqded6sdSZKKg_pcdT8G9bIEhiDLnI'
STOCK_CHANNEL_ID = '@autostockgag'
GROUP_ID = -4903879365  # поставь именно свой ID группы с минусом!
REQUIRED_CHANNELS = ['@autostockgag']
CHANNEL_LINKS = {'@autostockgag': 'https://t.me/autostockgag'}
STOCK_URL = 'https://www.vulcanvalues.com/grow-a-garden/stock'
USER_DB_FILE = 'telegram_users.json'
USER_PREFS_FILE = 'user_prefs.json'
POSTS_DB_FILE = 'posted_msgs.json'
LAST_USER_STOCK_FILE = 'last_user_stock.json'
AUTO_STOCK_FILE = 'auto_stock.json'

SECTION_TITLES = {
    'GEAR STOCK': 'Предметы',
    'EGG STOCK': 'Яйца',
    'SEEDS STOCK': 'Семена',
    'HONEY STOCK': 'Мёд',
    'COSMETIC STOCK': 'Косметика'
}
SECTION_EMOJI = {
    'GEAR STOCK': '🛠️',
    'EGG STOCK': '🥚',
    'SEEDS STOCK': '🌱',
    'HONEY STOCK': '🍯',
    'COSMETIC STOCK': '🎨'
}
SECTION_LIST = ['GEAR STOCK', 'EGG STOCK', 'SEEDS STOCK', 'HONEY STOCK', 'COSMETIC STOCK']

ITEM_TRANSLATE = {
    'Watering Can': 'Лейка', 'Favorite Tool': 'Инструмент фаворита', 'Recall Wrench': 'Ключ возврата',
    'Trowel': 'Совок', 'Basic Sprinkler': 'Обычный разбрызгиватель', 'Advanced Sprinkler': 'Улучшенный разбрызгиватель',
    'Godly Sprinkler': 'Годли разбрызгиватель', 'Master Sprinkler': 'Мастер разбрызгиватель', 'Shovel': 'Лопата',
    'Lightning Rod': 'Громовод', 'Common Egg': 'Обычное яйцо', 'Uncommon Egg': 'Необычное яйцо', 'Rare Egg': 'Редкое яйцо',
    'Bug Egg': 'Баг яйцо', 'Legendary Egg': 'Легендарное яйцо', 'Mythical Egg': 'Мифическое яйцо', 'Carrot': 'Морковь',
    'Strawberry': 'Клубника', 'Coconut': 'Кокос', 'Tomato': 'Томат', 'Blueberry': 'Черника', 'Apple': 'Яблоко',
    'Banana': 'Банан', 'Pineapple': 'Ананас', 'Grape': 'Виноград', 'Watermelon': 'Арбуз', 'Peach': 'Персик',
    'Mango': 'Манго', 'Cherry': 'Вишня', 'Raspberry': 'Малина', 'Blackberry': 'Ежевика', 'Pumpkin': 'Тыква',
    'Eggplant': 'Баклажан', 'Corn': 'Кукуруза', 'Pepper': 'Перец', 'Bamboo': 'Бамбук', 'Cactus': 'Кактус',
    'Dragon Fruit': 'Драконий фрукт', 'Mushroom': 'Мухомор', 'Cacao': 'Какао', 'Beanstalk': 'Бобы',
    'Orange Tulip': 'Оранжевый тюльпан', 'Daffodil': 'Нарцисс', 'Flower Seed Pack': 'Пакет семян цветов',
    'Nectarine Seed': 'Семя нектарина', 'Hive Fruit Seed': 'Семя улейного фрукта', 'Honey Sprinkler': 'Опрыскиватель с мёдом',
    'Bee Egg': 'Яйцо пчелы', 'Bee Crate': 'Ящик с пчёлами', 'Honey Comb': 'Соты', 'Honey Torch': 'Медовый факел', 'Ember Lily': 'Тлеющая лилия'
}
ITEM_EMOJI = {
    'Лейка': '💧', 'Инструмент фаворита': '💖', 'Ключ возврата': '🔧', 'Совок': '🪣', 'Обычный разбрызгиватель': '🚿',
    'Улучшенный разбрызгиватель': '🚿', 'Годли разбрызгиватель': '🌟', 'Мастер разбрызгиватель': '🏆', 'Лопата': '🛠️',
    'Громовод': '⚡️', 'Морковь': '🥕', 'Клубника': '🍓', 'Кокос': '🥥', 'Томат': '🍅', 'Черника': '🫐', 'Яблоко': '🍏',
    'Банан': '🍌', 'Ананас': '🍍', 'Виноград': '🍇', 'Арбуз': '🍉', 'Персик': '🍑', 'Манго': '🥭', 'Вишня': '🍒',
    'Малина': '🍇', 'Ежевика': '🍇', 'Тыква': '🎃', 'Баклажан': '🍆', 'Кукуруза': '🌽', 'Перец': '🌶️', 'Бамбук': '🎋',
    'Кактус': '🌵', 'Драконий фрукт': '🐉', 'Мухомор': '🍄', 'Какао': '🍫', 'Бобы': '🌱', 'Оранжевый тюльпан': '🌷',
    'Нарцисс': '🌼', 'Пакет семян цветов': '🌸', 'Семя нектарина': '🍑', 'Семя улейного фрукта': '🍯',
    'Опрыскиватель с мёдом': '💧', 'Яйцо пчелы': '🐝', 'Ящик с пчёлами': '📦', 'Соты': '🍯', 'Медовый факел': '🔥'
}
EGG_COLOR = {
    'Обычное яйцо': '⚪️', 'Необычное яйцо': '🟤', 'Редкое яйцо': '💙', 'Баг яйцо': '🟢', 'Легендарное яйцо': '🟡', 'Тлеющая лилия': '🌷🟠', 
    'Мифическое яйцо': '🟥', 'Яйцо пчелы': '🐝'
}
GEAR_ENG = [
    'Watering Can','Favorite Tool','Recall Wrench','Trowel','Basic Sprinkler','Advanced Sprinkler','Godly Sprinkler','Master Sprinkler','Shovel','Lightning Rod'
]
EGGS_ENG = [
    'Common Egg','Uncommon Egg','Rare Egg','Bug Egg','Legendary Egg','Mythical Egg','Bee Egg'
]
HONEY_ENG = [
    'Flower Seed Pack', 'Nectarine Seed', 'Hive Fruit Seed', 'Honey Sprinkler', 'Bee Egg',
    'Bee Crate', 'Honey Comb', 'Honey Torch'
]
SEEDS_ENG = [en for en in ITEM_TRANSLATE if en not in GEAR_ENG + EGGS_ENG + HONEY_ENG]

def ru_translate(text):
    tr = {
        'Hat': 'Шапка', 'Cape': 'Плащ', 'Wings': 'Крылья', 'Dress': 'Платье', 'Crown': 'Корона',
        'Scarf': 'Шарф', 'Mask': 'Маска', 'Glasses': 'Очки', 'Token': 'Токен', 'Crate': 'Сундук',
        'Dye': 'Краска', 'Flower': 'Цветок', 'Bee': 'Пчела', 'Honey': 'Мёд', 'Sunflower': 'Подсолнух', 'Nectar': 'Нектар'
    }
    for k, v in tr.items():
        text = text.replace(k, v)
    return text

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

def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates'
    params = {'timeout': 10}
    if offset:
        params['offset'] = offset
    try:
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
        return {}

def delete_telegram_message(chat_id, message_id):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage'
    payload = {'chat_id': chat_id, 'message_id': message_id}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка удаления сообщения: {e}")

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

def parse_section_stock(soup, section_title):
    section = None
    if section_title == "HONEY STOCK":
        for h2 in soup.find_all('h2'):
            if "HONEY" in h2.get_text(strip=True).upper() or "МЁД" in h2.get_text(strip=True).upper():
                section = h2
                break
    elif section_title == "COSMETIC STOCK":
        for h2 in soup.find_all('h2'):
            if "COSMETIC" in h2.get_text(strip=True).upper() or "КОСМЕТИКА" in h2.get_text(strip=True).upper():
                section = h2
                break
    else:
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
        if section_title == "COSMETIC STOCK":
            rus = ru_translate(name)
            emoji = "🎨"
            text = f"{emoji} {rus}"
        else:
            rus = ITEM_TRANSLATE.get(name, name)
            emoji = ITEM_EMOJI.get(rus, '')
            text = f"{emoji} {rus}".strip()
        if name in EGG_COLOR:
            text = f"{EGG_COLOR[name]} {rus}"
        if qty and qty != "1":
            items.append(f"<b>•</b> {text} x{qty}")
        else:
            items.append(f"<b>•</b> {text}")
    return items

def get_stock():
    try:
        response = requests.get(STOCK_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        stocks = {}
        for section in SECTION_LIST:
            stocks[section] = parse_section_stock(soup, section)
        return stocks
    except Exception as e:
        print(f"Ошибка загрузки стока: {e}")
        return {section: [] for section in SECTION_LIST}

def post_to_telegram(msg, chat_id, reply_markup=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': msg,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, data=payload)
        res = resp.json()
        if res.get("ok") and "result" in res:
            return res["result"]["message_id"]
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
    return None

def check_subscription(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember'
        params = {'chat_id': channel, 'user_id': user_id}
        try:
            resp = requests.get(url, params=params, timeout=10).json()
            if not resp.get('ok') or resp['result']['status'] not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            return False
    return True

def send_subscription_message(user_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Подписаться на autostockgag", "url": CHANNEL_LINKS['@autostockgag']}],
            [{"text": "✅ Я подписался", "callback_data": "checksub"}]
        ]
    }
    msg = (
        "👋 <b>Чтобы пользоваться ботом, подпишитесь на канал:</b>\n"
        f"1️⃣ <a href='{CHANNEL_LINKS['@autostockgag']}'>@autostockgag</a>\n"
        "После этого нажмите «Я подписался»."
    )
    post_to_telegram(msg, user_id, reply_markup=keyboard)

def send_reply_menu(user_id):
    reply_markup = {
        "keyboard": [
            ["Весь сток 📝"],
            ["Настроить выборочно ⚙️"],
            ["Показать текущий сток 📦"],
            ["Настройки ⚙️"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    msg = (
        "🔔 <b>Что присылать в личку?</b>\n"
        "Выберите <b>Весь сток</b> — чтобы получать всё, или <b>Настроить выборочно</b> — только нужные предметы/семена/яйца.\n"
        "Или используйте дополнительные функции:"
    )
    post_to_telegram(msg, user_id, reply_markup=reply_markup)

def send_section_choose(user_id):
    reply_markup = {
        "keyboard": [
            ["Семена 🌱", "Предметы 🛠️", "Яйца 🥚", "Мёд 🍯"],
            ["⬅️ В меню"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    msg = "Что хотите настроить? Выберите категорию:"
    post_to_telegram(msg, user_id, reply_markup=reply_markup)

def send_item_choose_menu(user_id, section, user_prefs):
    if section == "GEAR STOCK":
        items = [ITEM_TRANSLATE[en] for en in GEAR_ENG if en in ITEM_TRANSLATE]
    elif section == "SEEDS STOCK":
        items = [ITEM_TRANSLATE[en] for en in SEEDS_ENG if en in ITEM_TRANSLATE]
    elif section == "EGG STOCK":
        items = [ITEM_TRANSLATE[en] for en in EGGS_ENG if en in ITEM_TRANSLATE]
    elif section == "HONEY STOCK":
        items = [ITEM_TRANSLATE[en] for en in HONEY_ENG if en in ITEM_TRANSLATE]
    else:
        items = []
    chosen = set(user_prefs.get(user_id, {}).get('chosen_items', {}).get(section, []))
    keyboard = []
    for name in sorted(items):
        checked = "✅" if name in chosen else ""
        keyboard.append([f"{name}{checked}"])  # <-- ОДНА кнопка в каждой строке
    keyboard.append(["Сохранить выбор", "⬅️ К выбору категорий"])
    reply_markup = {
        "keyboard": keyboard,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    msg = f"Отметьте, что получать из раздела «{SECTION_TITLES[section]}» (можно несколько):"
    post_to_telegram(msg, user_id, reply_markup=reply_markup)

def get_auto_stock_status():
    auto_stock = load_json_file(AUTO_STOCK_FILE, {"enabled": True})
    return auto_stock.get("enabled", True)

def set_auto_stock_status(enabled: bool):
    save_json_file(AUTO_STOCK_FILE, {"enabled": enabled})

def send_settings_menu(user_id):
    auto_stock_enabled = get_auto_stock_status()
    status = "🟢 Включен" if auto_stock_enabled else "🔴 Отключен"
    keyboard = [
        [
            {"text": "Включить авто сток ✅", "callback_data": "auto_stock_on"},
            {"text": "Выключить авто сток ❌", "callback_data": "auto_stock_off"}
        ],
        [
            {"text": "⬅️ Назад", "callback_data": "back_to_menu"}
        ]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    msg = f"⚙️ <b>Настройки</b>\n\nАвто сток: <b>{status}</b>\n\nВыберите действие:"
    post_to_telegram(msg, user_id, reply_markup=reply_markup)

# --- МАССОВАЯ РАССЫЛКА С ПОДТВЕРЖДЕНИЕМ ---
massmail_state = {
    "waiting": False,
    "confirm": False,
    "from_user": None,
    "from_group": None,
    "pending_message_id": None
}

def send_massmail_confirm_buttons(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Подтвердить рассылку", "callback_data": "massmail_confirm"}],
            [{"text": "❌ Отмена", "callback_data": "massmail_cancel"}]
        ]
    }
    post_to_telegram(
        "Вы уверены, что хотите разослать это сообщение всем пользователям?\n\n"
        "Нажмите <b>Подтвердить рассылку</b> для отправки или <b>Отмена</b> для отмены.",
        chat_id,
        reply_markup=keyboard
    )

def handle_callback_query(callback_query, user_ids, user_prefs):
    global massmail_state
    user_id = str(callback_query['from']['id'])
    data = callback_query['data']
    # Стандартные кнопки
    if data == "auto_stock_on":
        set_auto_stock_status(True)
        post_to_telegram("✅ Авто сток теперь включен.", user_id)
        send_settings_menu(user_id)
    elif data == "auto_stock_off":
        set_auto_stock_status(False)
        post_to_telegram("❌ Авто сток теперь выключен.", user_id)
        send_settings_menu(user_id)
    elif data == "back_to_menu":
        send_reply_menu(user_id)
    elif data == "checksub":
        if check_subscription(user_id):
            user_ids.add(user_id)
            save_json_file(USER_DB_FILE, list(user_ids))
            send_reply_menu(user_id)
        else:
            post_to_telegram("❗️ Вы еще не подписались.", user_id)
    elif data == "massmail_confirm" and massmail_state["confirm"]:
        count_sent = 0
        for uid in user_ids:
            try:
                forward_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/forwardMessage'
                payload = {
                    'chat_id': uid,
                    'from_chat_id': massmail_state["from_group"],
                    'message_id': massmail_state["pending_message_id"]
                }
                requests.post(forward_url, data=payload)
                count_sent += 1
            except Exception as e:
                print(f"Ошибка рассылки: {e}")
        post_to_telegram(f"✅ Сообщение переслано {count_sent} пользователям.", massmail_state["from_group"])
        massmail_state.update({"waiting": False, "confirm": False, "from_user": None, "from_group": None, "pending_message_id": None})
    elif data == "massmail_cancel" and massmail_state["confirm"]:
        post_to_telegram("❌ Рассылка отменена.", massmail_state["from_group"])
        massmail_state.update({"waiting": False, "confirm": False, "from_user": None, "from_group": None, "pending_message_id": None})

def process_group_command(message, user_ids):
    global massmail_state
    chat_id = message['chat']['id']
    text = message.get('text', '').strip() if 'text' in message else ""
    from_user = message['from']['id']

    if text == '/users':
        count = len(user_ids)
        post_to_telegram(f"Всего пользователей бота: <b>{count}</b>", chat_id)
    elif text == '/rasik':
        massmail_state.update({
            "waiting": True,
            "confirm": False,
            "from_user": from_user,
            "from_group": chat_id,
            "pending_message_id": None
        })
        post_to_telegram(
            "✉️ Отправьте <b>любое сообщение (текст/фото/файл/тг пост)</b> для рассылки всем пользователям.\n\n"
            "Будет именно переслано! После отправки сообщения появится кнопка подтверждения.",
            chat_id
        )
    elif massmail_state["waiting"] and from_user == massmail_state["from_user"] and chat_id == massmail_state["from_group"]:
        # Ждем подтверждение
        massmail_state.update({
            "waiting": False,
            "confirm": True,
            "pending_message_id": message['message_id']
        })
        send_massmail_confirm_buttons(chat_id)

def process_user_menu(message, user_ids, user_prefs):
    user_id = str(message['from']['id'])
    text = message.get('text', '').strip() if 'text' in message else ""
    if user_id not in user_ids:
        send_subscription_message(user_id)
        return
    prefs = user_prefs.get(user_id, {})
    if text == "Показать текущий сток 📦":
        stocks = get_stock()
        if not any(stocks[section] for section in SECTION_LIST):
            post_to_telegram(
                "😔 Извините за неудобства!\n"
                "В данный момент мы не можем получить данные стока. Это временные трудности на стороне сайта, который поставляет данные, а не у нашей команды. Пожалуйста, попробуйте позже — мы восстановим отправку, как только появятся данные!",
                user_id
            )
        else:
            blocks = [
                make_stock_block(stocks[section], section) for section in SECTION_LIST if stocks[section]
            ]
            msg = (
                "✨ Сейчас на стоке:\n"
                "─────────────────────\n\n"
                + "".join(blocks)
                + "─────────────────────"
            )
            post_to_telegram(msg, user_id)
        send_reply_menu(user_id)
    elif text == "Настройки ⚙️":
        send_settings_menu(user_id)
    elif text == "Весь сток 📝":
        user_prefs[user_id] = {"mode": "all"}
        save_json_file(USER_PREFS_FILE, user_prefs)
        post_to_telegram("✅ Теперь вы будете получать весь сток!", user_id)
        send_reply_menu(user_id)
    elif text == "Настроить выборочно ⚙️":
        user_prefs[user_id] = {"mode": "custom", "chosen_items": {}}
        save_json_file(USER_PREFS_FILE, user_prefs)
        send_section_choose(user_id)
    elif text == "Семена 🌱":
        send_item_choose_menu(user_id, "SEEDS STOCK", user_prefs)
    elif text == "Предметы 🛠️":
        send_item_choose_menu(user_id, "GEAR STOCK", user_prefs)
    elif text == "Яйца 🥚":
        send_item_choose_menu(user_id, "EGG STOCK", user_prefs)
    elif text == "Мёд 🍯":
        send_item_choose_menu(user_id, "HONEY STOCK", user_prefs)
    elif text == "⬅️ В меню":
        send_reply_menu(user_id)
    elif text == "⬅️ К выбору категорий":
        send_section_choose(user_id)
    elif text == "Сохранить выбор":
        send_section_choose(user_id)
    else:
        for section, items_eng in [
            ("GEAR STOCK", GEAR_ENG),
            ("SEEDS STOCK", SEEDS_ENG),
            ("EGG STOCK", EGGS_ENG),
            ("HONEY STOCK", HONEY_ENG)
        ]:
            items = [ITEM_TRANSLATE[en] for en in items_eng if en in ITEM_TRANSLATE]
            name = text.replace("✅", "")
            if name in items:
                prefs = user_prefs.setdefault(user_id, {"mode": "custom", "chosen_items": {}})
                chosen = set(prefs.setdefault("chosen_items", {}).get(section, []))
                if name in chosen:
                    chosen.remove(name)
                else:
                    chosen.add(name)
                prefs["chosen_items"][section] = list(chosen)
                user_prefs[user_id] = prefs
                save_json_file(USER_PREFS_FILE, user_prefs)
                send_item_choose_menu(user_id, section, user_prefs)
                return
        send_reply_menu(user_id)

def get_period(section_name):
    now = datetime.now()
    if section_name in ['GEAR STOCK', 'SEEDS STOCK', 'HONEY STOCK']:
        if section_name == 'HONEY STOCK':
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(minutes=30)
        else:
            minute = now.minute - (now.minute % 5)
            start = now.replace(minute=minute, second=0, microsecond=0)
            end = start + timedelta(minutes=5)
    elif section_name == 'EGG STOCK':
        minute = 0 if now.minute < 30 else 30
        start = now.replace(minute=minute, second=0, microsecond=0)
        end = start + timedelta(minutes=30)
    elif section_name == 'COSMETIC STOCK':
        hour = (now.hour // 4) * 4
        start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=4)
    else:
        start = now
        end = now
    return start.strftime('%H:%M'), end.strftime('%H:%M')

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

def only_own_channel_posts(new_msg_id):
    posts = load_json_file(POSTS_DB_FILE, [])
    for post in list(posts):
        if post['msg_id'] != new_msg_id:
            delete_telegram_message(STOCK_CHANNEL_ID, post['msg_id'])
            posts.remove(post)
    posts = [p for p in posts if p['msg_id'] == new_msg_id]
    save_json_file(POSTS_DB_FILE, posts)

def user_listener(user_ids, user_prefs):
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates and 'result' in updates:
            for upd in updates['result']:
                last_update_id = upd['update_id'] + 1
                if 'message' in upd:
                    msg = upd['message']
                    if 'chat' in msg and (msg['chat']['type'] == 'group' or msg['chat']['type'] == 'supergroup') and msg['chat']['id'] == GROUP_ID:
                        process_group_command(msg, user_ids)
                    elif msg['chat']['type'] == 'private':
                        process_user_menu(msg, user_ids, user_prefs)
                elif 'callback_query' in upd:
                    callback = upd['callback_query']
                    handle_callback_query(callback, user_ids, user_prefs)
        time.sleep(2)

def main():
    user_ids = set(load_json_file(USER_DB_FILE, []))
    user_prefs = load_json_file(USER_PREFS_FILE, {})
    last_user_stock = load_json_file(LAST_USER_STOCK_FILE, {})
    threading.Thread(target=user_listener, args=(user_ids, user_prefs), daemon=True).start()
    prev_stock = None
    stock_error = False
    while True:
        try:
            auto_stock_enabled = get_auto_stock_status()
            if not auto_stock_enabled:
                time.sleep(30)
                continue
            stocks = get_stock()
            has_data = any(stocks[section] for section in SECTION_LIST)
            if not has_data:
                if not stock_error:
                    for user_id in list(user_ids):
                        post_to_telegram(
                            "😔 Извините за неудобства!\n"
                            "В данный момент мы не можем получить данные стока. Это временные трудности на стороне сайта, который поставляет данные, а не у нашей команды. Пожалуйста, попробуйте позже — мы восстановим отправку, как только появятся данные!",
                            user_id
                        )
                    stock_error = True
                prev_stock = stocks
                time.sleep(60)
                continue
            else:
                if stock_error:
                    stock_error = False
            if stocks != prev_stock:
                msg = (
                    "✨ Актуальный СТОК Grow a Garden ✨\n"
                    "──────────────────────────────\n\n"
                    f"{make_stock_block(stocks['GEAR STOCK'], 'GEAR STOCK') if stocks['GEAR STOCK'] else ''}"
                    f"{make_stock_block(stocks['EGG STOCK'], 'EGG STOCK') if stocks['EGG STOCK'] else ''}"
                    f"{make_stock_block(stocks['SEEDS STOCK'], 'SEEDS STOCK') if stocks['SEEDS STOCK'] else ''}"
                    f"{make_stock_block(stocks['HONEY STOCK'], 'HONEY STOCK') if stocks['HONEY STOCK'] else ''}"
                    f"{make_stock_block(stocks['COSMETIC STOCK'], 'COSMETIC STOCK') if stocks['COSMETIC STOCK'] else ''}"
                    "──────────────────────────────\n"
                    "🤍 Сделано командой @sbtdrasik для вашего удобства 🤍"
                )
                msg_id = post_to_telegram(msg, STOCK_CHANNEL_ID)
                if msg_id:
                    posts = load_json_file(POSTS_DB_FILE, [])
                    posts.append({'msg_id': msg_id, 'timestamp': time.time()})
                    save_json_file(POSTS_DB_FILE, posts)
                    only_own_channel_posts(msg_id)
                for user_id in list(user_ids):
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
                            post_to_telegram(ls_msg, user_id)
                            last_user_stock[user_id] = ls_msg
                            save_json_file(LAST_USER_STOCK_FILE, last_user_stock)
                prev_stock = stocks
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()