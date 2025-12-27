import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import asyncio
import random
import time
from datetime import datetime, timedelta
from aiogram.types import ParseMode


admin_id = 1621495791


conn = sqlite3.connect('base_mainn.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        ZBX_coins INT DEFAULT 15000,
        kd_work TEXT DEFAULT '0',
        coins_win INT DEFAULT 0,
        coins_loss INT DEFAULT 0,
        sms_day INT DEFAULT 0,
        sms_week INT DEFAULT 0,
        sms_main INT DEFAULT 0,
        stars INT DEFAULT 0
)
""")
conn.commit()


API_TOKEN = '7912798466:AAGYMfVx-SFjKL9SMA1HxzJXPfvpu_2PwQY'


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def reset_logic():
    while True:
        now = datetime.now()
        
        if now.hour == 1 and now.minute == 26:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET sms_day = 0')
            
            if now.weekday() == 0:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET sms_week = 0')
                print("Недельная статистика обнулена")
                
            conn.commit()
            print("Дневная статистика обнулена")
            
            await asyncio.sleep(61)
        
        await asyncio.sleep(30) 

async def on_startup(_):
    asyncio.create_task(reset_logic())
    print("Фоновая задача по сбросу статистики запущена")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        await message.answer(f"🖐️ Приветствую тебя, {message.from_user.full_name}")
    else:
        await message.answer(f"🖐️ Приветствую тебя, {message.from_user.full_name}")
 
 
@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    menu_message = (
        "<blockquote expandable>📋 <b>Главное меню:</b>\n\n"
        "/RP – Рп-команды\n"
        "/profile – Профиль\n\n"
        "/foot – Игра футбол\n"
        "/slot – Игра в слоты\n"
        "/dice – Игра в кости\n"
        "/dart – Игра в дартс\n"
        "/bask – Игра в баскетбол\n\n"
        "/top_day – Дневной топ по смс\n"
        "/top_week – Недельный топ по смс\n"
        "/top_main – Топ по смс за всё время\n"
        "/top_stars – Рейтинг\n"
        "/top_lvl – Топ по уровням\n\n"
        "/trade – Обмен на звёзды (рейтинг бота)\n"
        "/work – Работа (+коины)\n</blockquote>"
    )
    
    await message.answer(menu_message, parse_mode='html')

    
@dp.message_handler(commands=['about'])
async def menu(message: types.Message):
    menu_message = (
        "Пока что бета тест бота, проверяю хостинг... Основая цель бота здесь пока что играть и повысить свой рейтинг, так же бот личный, и невозможно его добавить в разные группы, бот отслежтвает статистику чата и выдает топ по ней... Пока что играйте, тестите повышайте рейтинг чтоб быть в топе... Бот от Мэдли Софта"
    )
    
    await message.answer(menu_message, parse_mode='html')
                        
    
@dp.message_handler(commands=['RP'])
async def menu(message: types.Message):
    menu_message = (
    " 👀 <b>Список RP-команд:</b>\n\n"
    "<code>погладить</code>, <code>обнять</code>, <code>ущипнуть</code>, <code>поцеловать</code>, "
    "<code>ударить</code>, <code>пнуть</code>, <code>выебать</code>, <code>похлопать</code>, "
    "<code>трахнуть</code>, <code>иди нахуй</code>, <code>застрелить</code>, <code>убить</code>, "
    "<code>удачи</code>, <code>спасибо</code>, <code>дать голды</code>, <code>уебать</code>, "
    "<code>изнасиловать</code>, <code>облизать</code>, <code>задушить</code>, <code>засосать</code>, "
    "<code>облизать ноги</code>, <code>облизать руки</code>, <code>полизать ухо</code>, <code>отсосать</code>"
)
    
    await message.answer(menu_message, parse_mode='html')

        
@dp.message_handler(commands=['slot_info'])
async def menu(message: types.Message):
    menu_message = (
        "🎰 Слоты: информация...\n\n\n7️⃣7️⃣7️⃣ = 3Х\n\n🍋🍋🍋 = 2.5X\n\nBAR|BAR|BAR = 3.25X\n\n🍇🍇🍇 = 3Х\n\n7️⃣7️⃣ = 1.15Х\n\n🍋🍋 = 0.75X\n\nBAR|BAR = 0.70X\n\n🍇🍇 = 0.65Х"
    )
    
    await message.answer(menu_message, parse_mode='html')


last_top_usage = {}

@dp.message_handler(commands=['top_stars'])
async def top_players_coins(message: types.Message):
    now = time.time()
    if message.chat.id in last_top_usage and now - last_top_usage[message.chat.id] < 30:
        await message.answer("⏳ Использование статистики разрешена в раз в 30 сек", parse_mode='html')
        return
    
    last_top_usage[message.chat.id] = now
    cursor.execute('SELECT user_id, stars FROM users ORDER BY stars DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("🏆 <b>Топ игроков:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "🏆 <b>Топ 10 людей по рейтингу:</b>\n\n"
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name 
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win} 🌟\n"

    await message.answer(top_message, parse_mode='html')


@dp.message_handler(commands=['top_day'])
async def top_players_day(message: types.Message):
    now = time.time()
    if message.chat.id in last_top_usage and now - last_top_usage[message.chat.id] < 30:
        await message.answer("⏳ Использование статистики разрешена в раз в 30 сек", parse_mode='html')
        return
    
    last_top_usage[message.chat.id] = now
    cursor.execute('SELECT user_id, sms_day FROM users ORDER BY sms_day DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("📊 <b>Топ пользователей по сообщениям в сутки:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "📊 <b>Топ пользователей по сообщениям в день:</b>\n\n"
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name 
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win}\n"

    await message.answer(top_message, parse_mode='html')

    
@dp.message_handler(commands=['top_week'])
async def top_players_week(message: types.Message):
    now = time.time()
    if message.chat.id in last_top_usage and now - last_top_usage[message.chat.id] < 30:
        await message.answer("⏳ Использование статистики разрешена в раз в 30 сек", parse_mode='html')
        return
    
    last_top_usage[message.chat.id] = now
    cursor.execute('SELECT user_id, sms_week FROM users ORDER BY sms_week DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("📊 <b>Топ пользователей по сообщениям в сутки:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "📊 <b>Топ пользователей по сообщениям в неделю</b>\n\n"
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name 
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win}\n"

    await message.answer(top_message, parse_mode='html')


@dp.message_handler(commands=['top_main'])
async def top_players_main(message: types.Message):
    now = time.time()
    if message.chat.id in last_top_usage and now - last_top_usage[message.chat.id] < 30:
        await message.answer("⏳ Использование статистики разрешена в раз в 30 сек", parse_mode='html')
        return
    
    last_top_usage[message.chat.id] = now
    cursor.execute('SELECT user_id, sms_main FROM users ORDER BY sms_main DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("📊 <b>Топ пользователей по сообщениям в сутки:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "📊 <b>Общая статистика группы по сообщениям:</b>\n\n"
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name 
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win}\n"

    await message.answer(top_message, parse_mode='html')


@dp.message_handler(commands=['top_lvl'])
async def top_players_levels(message: types.Message):
    now = time.time()
    if message.chat.id in last_top_usage and now - last_top_usage[message.chat.id] < 30:
        await message.answer("⏳ Использование статистики разрешена в раз в 30 сек", parse_mode='html')
        return
    
    last_top_usage[message.chat.id] = now
    cursor.execute('SELECT user_id, coins_win, coins_loss FROM users ORDER BY sms_main DESC') 
    all_users_data = cursor.fetchall()

    if not all_users_data:
        await message.answer("📊 <b>Топ пользователей по уровням:</b> Нет данных о пользователях.", parse_mode='html')
        return

    user_levels = []
    for user_id, coins_win, coins_loss in all_users_data:
        total_exp = int((coins_win / 5) + (coins_loss / 10))
        
        level = 1
        exp_for_next_level = 500
        temp_exp = total_exp

        while temp_exp >= exp_for_next_level:
            temp_exp -= exp_for_next_level
            level += 1
            exp_for_next_level += 500
        
        user_levels.append((user_id, level))

    user_levels.sort(key=lambda item: item[1], reverse=True)

    top_message = "📊 <b>Топ пользователей по уровням:</b>\n\n"
    for rank, (user_id, level) in enumerate(user_levels[:10], start=1): 
        user = await bot.get_chat(user_id)
        full_name = user.full_name 
        top_message += f'<b>{rank}. <a href="tg://openmessage?user_id={user_id}">{full_name}</a></b> – {level} 🆙\n'

    await message.answer(top_message, parse_mode='html')


@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss, sms_day, sms_week, sms_main FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        await message.answer("⚠️ У вас еще нет профиля.")
        return

    ZBX_coins, coins_win, coins_loss, sd, sw, sm = result

    total_exp = int((coins_win / 5) + (coins_loss / 10))
    
    level = 1
    exp_for_next_level = 500
    temp_exp = total_exp

    while temp_exp >= exp_for_next_level:
        temp_exp -= exp_for_next_level
        level += 1
        exp_for_next_level += 500 

    profile_message = (
        f"👤 <b><a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a>:</b>\n\n"
        f"🔑 <b>ID:</b> <code>{user_id}</code>\n"
        f"🧬 <b>Уровень:</b> {level}\n"
        f"✨ <b>Опыт:</b> {temp_exp} / {exp_for_next_level}\n\n"
        f"💰 <b>Баланс:</b> {ZBX_coins} 🪙 ZBX\n\n"
        f"📈 <b>Выигрышей:</b> {coins_win} 🪙 \n"
        f"📉 <b>Проигрышей:</b> {coins_loss} 🪙 \n\n"
        f"📊 <b>Актив в группе (день | неделя | общая):</b> <code>{sd} | {sw} | {sm}</code>"
    )

    await message.answer(profile_message, parse_mode='html')


@dp.message_handler(commands=['trade'])
async def trade_coins_for_stars(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) == 1:  
            await message.reply("Используйте команду в формате: /trade (количество звезд).\
Курс обмена: 50 🪙 ZBX = 1 ⭐ звезда.")
            return

        stars_to_get = int(command_parts[1])
        if stars_to_get <= 0:
            await message.reply("Ошибка: Количество звезд должно быть положительным числом.")
            return

        coins_per_star = 50
        required_coins = stars_to_get * coins_per_star

        user_id = message.from_user.id

        cursor.execute("SELECT ZBX_coins FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()

        if user_data is None:
            await message.reply("Ошибка: Ваш профиль не найден в базе данных.")
            return

        current_coins = user_data[0]

        if current_coins < required_coins:
            await message.reply(f"Недостаточно средств. Вам нужно {required_coins} 🪙 ZBX для получения {stars_to_get} ⭐ звезд. Ваш текущий баланс: {current_coins} 🪙 ZBX.")
            return

        new_coins_balance = current_coins - required_coins
        cursor.execute("UPDATE users SET ZBX_coins = ?, stars = stars + ? WHERE user_id = ?", (new_coins_balance, stars_to_get, user_id))
        conn.commit()

        await message.reply(f"💸 Обмен выполнен успешно!\n\nВы обменяли {required_coins} 🪙 ZBX на {stars_to_get} ⭐ звезд.")

    except ValueError:
        await message.reply("Ошибка: Убедитесь, что вы ввели правильный формат команды: /trade (количество звезд)")
    except sqlite3.Error as e:
        await message.reply(f"Ошибка базы данных: {e}")
    except Exception as e:
        await message.reply(f"Произошла непредвиденная ошибка: {e}")


@dp.message_handler(commands=['pay'])
async def pay_coins(message: types.Message):
    if message.from_user.id != admin_id:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    try:
        _, user_id, amount = message.text.split()
        user_id = int(user_id)  
        amount = int(amount) 

        cursor.execute("UPDATE users SET ZBX_coins = ZBX_coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

        await message.reply(f"💸 Баланс пользователя – ID: {user_id} был пополнен на +{amount} 🪙 ZBX...")

        try:
            user_message = f"<b>💸 Пополнение:</b>\n\n✅ Ваш баланс изменён:<code>\n+ {amount} 🪙 ZBX</code>"
            await bot.send_message(user_id, user_message, parse_mode='html')
        except Exception as e:
            await message.reply(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    except ValueError:
        await message.reply("Ошибка: убедитесь, что вы ввели правильный формат команды: /pay (user_id) (amount)")
    except sqlite3.Error as e:
        await message.reply(f"Ошибка базы данных: {e}")


@dp.message_handler(commands=['nopay'])
async def withdraw_coins(message: types.Message):
    if message.from_user.id != admin_id:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 4:
            await message.reply("Ошибка: убедитесь, что вы ввели правильный формат команды: /withdraw (user_id) (amount) (reason)")
            return

        user_id = int(parts[1])  
        amount = int(parts[2])  
        reason = ' '.join(parts[3:])
        
        cursor.execute("SELECT ZBX_coins FROM users WHERE user_id = ?", (user_id,))
        ZBX_coins = cursor.fetchone()
        
        if ZBX_coins is None:
            await message.reply(f"Пользователь с ID {user_id} не найден.")
            return

        current_ZBX_coins = ZBX_coins[0]
        if current_ZBX_coins < amount:
            await message.reply(f"Недостаточно коинов на балансе пользователя {user_id}. Текущий баланс: {current_ZBX_coins} 🪙 ZBX.")
            return

        cursor.execute("UPDATE users SET ZBX_coins = ZBX_coins - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

        await message.reply(f"💰 Баланс пользователя – ID: {user_id} был уменьшен на –{amount} 🪙 ZBX по причине: {reason}.")

        try:
            user_message = f"<b>💰 Вывод средств:</b>\n\n❌ Ваш баланс уменьшён:<code>\n– {amount} 🪙 ZBX</code>\n\n🔍 <b>Причина:</b> <i>{reason}</i>"
            await bot.send_message(user_id, user_message, parse_mode='html')
        except Exception as e:
            await message.reply(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    except ValueError:
        await message.reply("Ошибка: убедитесь, что вы ввели правильный формат команды: /withdraw (user_id) (amount) (reason)")
    except sqlite3.Error as e:
        await message.reply(f"Ошибка базы данных: {e}")


def get_combo_text(dice_value: int):
    values = ["BAR", "виноград", "лимон", "семь"]
    dice_value -= 1
    result = []
    for _ in range(3):
        result.append(values[dice_value % 4])
        dice_value //= 4
    return result

def calculate_multiplier(combo: list):
    if combo.count('семь') == 3:
        return 4
    elif combo.count('лимон') == 3:
        return 3.5
    elif combo.count('BAR') == 3:
        return 3.25
    elif combo.count('виноград') == 3:
        return 3
    elif combo.count('семь') == 2:
        return 1.15
    elif combo.count('лимон') == 2:
        return 0.75
    elif combo.count('BAR') == 2:
        return 0.70
    elif combo.count('виноград') == 2:
        return 0.65
    return 0.0


@dp.message_handler(commands=['slot'])
async def roll_slot(message: types.Message):
    try:
        args = message.text.split()
        bet = int(args[1])
    except (IndexError, ValueError):
        await message.answer("<b>⚠️ Используйте формат:</b>\n\n/slot «ставка» (от 50 до 1000)", parse_mode='html')
        return

    if bet < 50 or bet > 100000:
        await message.answer("⚠️ Ставка должна быть от 🪙 50 до 🪙 100000 ZBX")
        return

    user_id = message.from_user.id
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    ZBX_coins = result[0] if result else 0
    c_wins = result[1]
    c_loss = result[2]

    if bet > ZBX_coins:
        await message.answer("У вас недостаточно средств для этой ставки.")
        return

    new_ZBX_coins = ZBX_coins - bet
    cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins) VALUES (?, ?)', (user_id, new_ZBX_coins))

    data = await bot.send_dice(message.chat.id, emoji='🎰')
    combo = get_combo_text(data.dice.value)
    multiplier = calculate_multiplier(combo)

    if multiplier >= 1:
        winnings = int(bet * multiplier) 
        coins_win = winnings - bet + c_wins
        coins_loss = c_loss
        new_ZBX_coins += winnings
        emoji = "<b>🟢 Повезло!</b>"
    else:
        winnings = int(bet * multiplier)  
        coins_loss = bet - winnings + c_loss
        coins_win = c_wins
        new_ZBX_coins += winnings
        emoji = "<b>🔴 Не повезло!</b>" 
        
    cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_ZBX_coins, coins_win, coins_loss))
    conn.commit()

    await asyncio.sleep(1.5)
    await message.answer(
        f"{emoji}\n\n<b>💸 Ставка:</b> –{bet} 🪙 ZBX\n"
        f"<b>👀 Выпало:</b> <i>{', '.join(combo)}...</i>\n"
        f"🔎 <b>Выигрышь:</b> +{bet * multiplier:.2f} 🪙 ZBX ({multiplier:.2f}X)\n\n"
        f"💰 <b>Ваш новый баланс:</b> {new_ZBX_coins} 🪙 ZBX"
    , parse_mode='html')


    
    
@dp.message_handler(commands=['dice'])
async def roll_dice(message: types.Message):
    try:
        args = message.text.split()
        target_number = int(args[1])
        bet = int(args[2])
    except (IndexError, ValueError):
        await message.answer("<b>⚠️ Используйте формат:</b>\n\n/dice «число, на которое ставишь» «ставка»", parse_mode='html')
        return

    if target_number < 1 or target_number > 6:
        await message.answer("⚠️ Число, на которое ставите, должно быть от 1 до 6")
        return

    if bet < 25 or bet > 100000:
        await message.answer("⚠️ Ставка должна быть от 25 🪙 до 100000 🪙 ZBX")
        return

    user_id = message.from_user.id
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    ZBX_coins, coins_win, coins_loss = result if result else (0, 0, 0)

    if bet > ZBX_coins:
        await message.answer("🚫 У вас недостаточно 🪙 ZBX для этой ставки")
        return

    data = await bot.send_dice(message.chat.id, emoji='🎲')
    rolled_number = data.dice.value

    if rolled_number == target_number:
        winnings = int(bet * 4)
        new_ZBX_coins = ZBX_coins + winnings
        coins_win += int(winnings / 4) 
        cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_ZBX_coins, coins_win, coins_loss))
        await asyncio.sleep(2)
        await message.answer(f"<b>👌 Победа!</b>\n\n<b>🟢 Выпало число:</b> {rolled_number}\n<b>✅ Ставка (x4):</b> <code>+{winnings} 🪙 ZBX</code>\n\n<b>💰 Ваш новый баланс:</b> {new_ZBX_coins} 🪙 ZBX", parse_mode='html')
    else:
        new_ZBX_coins = ZBX_coins - bet
        coins_loss += bet  
        cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_ZBX_coins, coins_win, coins_loss))
        await asyncio.sleep(2)
        await message.answer(f"<b>👎 Проигрыш!</b>\n\n<b>🔴 Выпало число:</b> {rolled_number}\n<b>❎ Ставка:</b> <code>–{bet} 🪙 ZBX</code>\n\n<b>💰 Ваш новый баланс:</b> {new_ZBX_coins} 🪙 ZBX", parse_mode='html')

    conn.commit()


@dp.message_handler(commands=['bask'])
async def roll_basketball(message: types.Message):
    
    args = message.get_args().split()
    
    if len(args) != 1 or not args[0].isdigit():
        await message.answer("⚠️ Пожалуйста, укажите ставку от 50 до 100000. \n\nПример: /bask 100")
        return
    
    stake = int(args[0])

    if stake < 50 or stake > 100000:
        await message.answer("⚠️ Ставка должна быть от 50 до 100000.")
        return

    user_id = message.from_user.id

    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] < stake:
        await message.answer("⚠️ У вас недостаточно 🪙 ZBX для ставки.")
        return

    data = await bot.send_dice(message.chat.id, emoji='🏀')
    basketball_value = data.dice.value

    if basketball_value == 1:
        payout = 0
        new_loss = result[2] + stake
        new_win = result[1]
        message_result = "🤕 Не попал! (0X)"
    elif basketball_value == 2:
        payout = int(stake * 0.2)
        new_loss = stake - payout + result[2]
        new_win = result[1]
        message_result = "😔 Мимо! (0.2X)"
    elif basketball_value == 3:
        payout = int(stake * 0.35)
        new_loss = stake - payout + result[2]
        new_win = result[1]
        message_result = "👍 Ещё попытку! (0.35X)"
    elif basketball_value == 4:
        payout = int(stake * 1.75)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🫠 Не плохо! (1.75X)"
    elif basketball_value == 5:
        payout = int(stake * 2.25)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🤘 Шикарно! (2.25X)"

    new_ZBX_coins = result[0] - stake + payout
    cursor.execute('UPDATE users SET ZBX_coins = ?, coins_win = ?, coins_loss = ? WHERE user_id = ?', (new_ZBX_coins, new_win, new_loss, user_id))
    conn.commit()

    
    await asyncio.sleep(1.5)
    await message.answer(f'<b>{message_result}</b>\n\n<b>💸 Ставка:</b> –{stake} 🪙 ZBX\n<b>👌 Выигрышь:</b> +{payout} 🪙 ZBX\n\n<b>💰 Ваш новый баланс:</b> {new_ZBX_coins} 🪙', parse_mode='html')


@dp.message_handler(commands=['foot'])
async def roll_basketball(message: types.Message):
    
    args = message.get_args().split()
    
    if len(args) != 1 or not args[0].isdigit():
        await message.answer("⚠️ Пожалуйста, укажите ставку от 50 до 100000. \n\nПример: /bask 100")
        return
    
    stake = int(args[0])

    if stake < 50 or stake > 100000:
        await message.answer("⚠️ Ставка должна быть от 50 до 100000.")
        return

    user_id = message.from_user.id

    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] < stake:
        await message.answer("⚠️ У вас недостаточно 🪙 ZBX для ставки.")
        return

    data = await bot.send_dice(message.chat.id, emoji='⚽')
    basketball_value = data.dice.value

    if basketball_value == 1:
        payout = 0
        new_loss = result[2] + stake
        new_win = result[1]
        message_result = "🤕 Не попал! (0X)"
    elif basketball_value == 2:
        payout = 0
        new_loss = result[2] + stake
        new_win = result[1]
        message_result = "😔 Мимо! (0X)"
    elif basketball_value == 3:
        payout = int(stake * 1.25)
        new_loss = stake - payout + result[2]
        new_win = result[1]
        message_result = "👍 Пойдёт (1.25X)"
    elif basketball_value == 4:
        payout = int(stake * 1.45)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🫠 Не плохо! (1.45X)"
    elif basketball_value == 5:
        payout = int(stake * 2)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🤘 Шикарно! (2X)"

    new_ZBX_coins = result[0] - stake + payout
    cursor.execute('UPDATE users SET ZBX_coins = ?, coins_win = ?, coins_loss = ? WHERE user_id = ?', (new_ZBX_coins, new_win, new_loss, user_id))
    conn.commit()

    
    await asyncio.sleep(1.5)
    await message.answer(f'<b>{message_result}</b>\n\n<b>💸 Ставка:</b> –{stake} 🪙 ZBX\n<b>👌 Выигрышь:</b> +{payout} 🪙 ZBX\n\n<b>💰 Ваш новый баланс:</b> {new_ZBX_coins} 🪙', parse_mode='html')


@dp.message_handler(commands=['dart'])
async def roll_dice(message: types.Message):
    args = message.get_args().split()
    
    if len(args) != 1 or not args[0].isdigit():
        await message.answer("⚠️ Пожалуйста, укажите ставку от 50 до 100000. \n\nПример: /dart 100")
        return
    
    stake = int(args[0])

    if stake < 50 or stake > 100000:
        await message.answer("⚠️ Ставка должна быть от 50 до 100000.")
        return

    user_id = message.from_user.id

    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] < stake:
        await message.answer("⚠️ У вас недостаточно 🪙 ZBX для ставки.")
        return

    data = await bot.send_dice(message.chat.id, emoji='🎯')
    dart_value = data.dice.value

    current_win = result[1]
    current_loss = result[2]

    if dart_value == 1:
        payout = 0
        message_result = "🤕 Не повезло! (0X)"
    elif dart_value == 2:
        payout = int(stake * 0.2)
        message_result = "😔 Не повезло! (0.2X)"
    elif dart_value == 3:
        payout = int(stake * 0.35)
        message_result = "🙁 Не повезло! (0.35X)"
    elif dart_value == 4:
        payout = int(stake * 0.7)
        message_result = "🫠 Почти в точку! (0.7X)"
    elif dart_value == 5:
        payout = int(stake * 0.85)
        message_result = "🫡 Почти в точку! (0.85X)"
    elif dart_value == 6:
        payout = int(stake * 2.5)
        message_result = "🤘 Отлично! Прям в точку! (2.5X)"

    if payout > stake:
        new_win = current_win + (payout - stake)
        new_loss = current_loss
    else:
        new_win = current_win
        new_loss = current_loss + (stake - payout)

    new_balance = result[0] - stake + payout
    cursor.execute('UPDATE users SET ZBX_coins = ?, coins_win = ?, coins_loss = ? WHERE user_id = ?', (new_balance, new_win, new_loss, user_id))
    conn.commit()

    await asyncio.sleep(1.5)
    await message.answer(f'<b>{message_result}</b>\n\n<b>💸 Ставка:</b> –{stake} 🪙 ZBX\n<b>👌 Выплата:</b> +{payout} 🪙 ZBX\n\n<b>💰 Ваш новый баланс:</b> {new_balance} 🪙', parse_mode='html')

@dp.message_handler(commands=['work'])
async def work_command(message: types.Message):
    user_id = message.from_user.id
    current_time = int(datetime.now().timestamp())

    cursor.execute('SELECT ZBX_coins, kd_work FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        ZBX_coins = random.randint(5000, 10000)
        cursor.execute('UPDATE users SET ZBX_coins = ?, kd_work = ? WHERE user_id = ?', (ZBX_coins, current_time, user_id))
        conn.commit()
        await message.answer(f"💰 Вы получили {ZBX_coins} коинов!")
        return

    ZBX_coins, last_work_time = result

    last_work_time = int(last_work_time)

    if current_time < last_work_time + 8 * 750:
        remaining_time = (last_work_time + 8 * 750 - current_time)
        await message.answer(f"⏳ Вы можете работать снова через {remaining_time // 3600}ч. {(remaining_time % 3600) // 60}м.")
        return

    coins = random.randint(5000, 10000)
    ZBX_coins += coins
    cursor.execute('UPDATE users SET ZBX_coins = ?, kd_work = ? WHERE user_id = ?', (ZBX_coins, current_time, user_id))
    conn.commit()
    await message.answer(f"💰 Вы получили {coins} коинов! Теперь у вас {ZBX_coins} коинов.")


@dp.message_handler(commands=['give'])
async def give_money(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("❗ Ответьте на сообщение того, кому хотите перевести.")

    args = message.get_args()
    if not args or not args.isdigit():
        return await message.reply("❗ Используйте: /give [сумма]")

    amount = int(args)
    from_id = message.from_user.id
    to_id = message.reply_to_message.from_user.id

    if from_id == to_id:
        return await message.reply("❗ Нельзя переводить самому себе.")

    if message.reply_to_message.from_user.is_bot:
        return await message.reply("❗ Нельзя переводить ботам.")

    if amount <= 100:
        return await message.reply("❗ Сумма должна быть больше 100.")

    cursor = conn.cursor()

    cursor.execute('SELECT ZBX_coins FROM users WHERE user_id = ?', (from_id,))
    row_from = cursor.fetchone()

    cursor.execute('SELECT ZBX_coins FROM users WHERE user_id = ?', (to_id,))
    row_to = cursor.fetchone()

    if not row_from:
        return await message.reply("❗ Вы отсутствуете в базе данных.")

    if not row_to:
        return await message.reply("❗ Получатель отсутствует в базе данных.")

    if row_from[0] < amount:
        return await message.reply("❗ Недостаточно средств.")

    cursor.execute('UPDATE users SET ZBX_coins = ZBX_coins - ? WHERE user_id = ?', (amount, from_id))
    cursor.execute('UPDATE users SET ZBX_coins = ZBX_coins + ? WHERE user_id = ?', (amount, to_id))

    conn.commit()

    from_link = f"<b><a href='tg://user?id={from_id}'>{message.from_user.first_name}</a></b>"
    to_link = f"<b><a href='tg://user?id={to_id}'>{message.reply_to_message.from_user.first_name}</a></b>"

    await message.answer(f"💳 | {from_link} отправил(а) +{amount} 🪙 ZBX {to_link}", parse_mode="HTML")


def create_user_mention_html(user: types.User) -> str:
    display_name = user.full_name if user.full_name else user.first_name
    return f'<b><a href="tg://user?id={user.id}">{display_name}</a></b>'


RP_COMMANDS = {
    "погладить": "😌🫳 | {initiator} погладил(а) {target}",
    "обнять": "🤗 | {initiator} крепко обнял(а) {target}",
    "ущипнуть": "🤏 | {initiator} слегка ущипнул(а) {target}",
    "поцеловать": "💋😏 | {initiator} нежно поцеловал(а) {target}",
    "ударить": "😵👊 | {initiator} со всей силы ударил(а) {target}",
    "пнуть": "😵‍💫👞 | {initiator} дал(а) пинка под зад {target}",
    "выебать": "🥵 | {initiator} жёстко надругался(ась) над {target}",
    "похлопать": "👏 | {initiator} похлопал(а) {target}",
    "трахнуть": "👌👈 | {initiator} трахнул(а) {target}",
    "иди нахуй": "🫡👎 | {initiator} послал(а) нахуй {target}",
    "застрелить": "🔫😵 | {initiator} застрелил(а) {target}",
    "убить": "🤡🔪 | {initiator} убил(а) {target}",
    "удачи": "🤞🍀 | {initiator} пожелал(а) удачи {target}",
    "спасибо": "🫂 | {initiator} поблагодарил(а) {target}",
    "дать голды": "🤲🟡 | {initiator} дал(а) голды, как бомжу {target}",
    "уебать": "👊😵‍💫 | {initiator} уебал(а) со всей дури {target}",
    "изнасиловать": "🔞 | {initiator} изнасиловал(а) {target}",
    "облизать": "👅 | {initiator} облизал(а) у {target}",
    "задушить": "💀 | {initiator} задушил(а) {target}",
    "засосать": "💋🔥 | {initiator} засосал(а) {target}",
    "облизать ноги": "👅🦶 | {initiator} облизал(а) {target} ноги",
    "облизать руки": "👅✋ | {initiator} облизал(а) {target} руки",
    "полизать ухо": "👅👂 | {initiator} полизал(а) {target} ухо",
    "отсосать": "🍆💦 | {initiator} отсосал(а) хуй у {target}",
}


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_all_text(message: types.Message):
    # 1. СТАТИСТИКА (срабатывает на любое текстовое сообщение в группах)
    if message.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
        user_id = message.from_user.id
        
        # Если отправитель бот — не считаем статистику
        if not message.from_user.is_bot:
            cursor = conn.cursor()
            
            # Добавляем пользователя, если его нет (с дефолтными нулями)
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, sms_day, sms_week, sms_main) 
                VALUES (?, 0, 0, 0)
            ''', (user_id,))
            
            # Обновляем счетчики
            cursor.execute('''
                UPDATE users 
                SET sms_day = sms_day + 1, 
                    sms_week = sms_week + 1, 
                    sms_main = sms_main + 1 
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()

    # 2. РП-КОМАНДЫ (срабатывают, если это ответ на сообщение)
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        initiator_user = message.from_user

        # Игнорируем команды от ботов
        if initiator_user.is_bot:
            return

        command = message.text.lower().strip()

        if command in RP_COMMANDS:
            response_template = RP_COMMANDS[command]
            response_text = response_template.format(
                initiator=create_user_mention_html(initiator_user),
                target=create_user_mention_html(target_user)
            )
            await message.reply(response_text, parse_mode=ParseMode.HTML)
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)