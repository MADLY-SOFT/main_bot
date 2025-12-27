import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import asyncio
import random
from datetime import datetime, timedelta


admin_id = 1621495791


conn = sqlite3.connect('base_main.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        ZBX_coins INT DEFAULT 500,
        kd_work TEXT DEFAULT '0',
        coins_win INT DEFAULT 0,
        coins_loss INT DEFAULT 0
)
""")
conn.commit()


API_TOKEN = '7912798466:AAGYMfVx-SFjKL9SMA1HxzJXPfvpu_2PwQY'


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
        "📋 <b>Главное меню:</b>\n\n"
        "/profile – Профиль\n"
        "/slot – Игра в слоты\n"
        "/dice – Игра в кости\n"
        "/dart – Игра в дартс\n"
        "/bask – Игра в баскетбол\n\n"
        "/top_wins – Топ по выигрышам\n"
        "/top_coins – Топ богачей\n\n"
        "/work – Работа (+коины)\n"
    )
    
    await message.answer(menu_message, parse_mode='html')
    
@dp.message_handler(commands=['slot_info'])
async def menu(message: types.Message):
    menu_message = (
        "🎰 Слоты: информация...\n\n\n7️⃣7️⃣7️⃣ = 3Х\n\n🍋🍋🍋 = 2.5X\n\nBAR|BAR|BAR = 3.25X\n\n🍇🍇🍇 = 3Х\n\n7️⃣7️⃣ = 1.15Х\n\n🍋🍋 = 0.75X\n\nBAR|BAR = 0.70X\n\n🍇🍇 = 0.65Х"
    )
    
    await message.answer(menu_message, parse_mode='html')


@dp.message_handler(commands=['top_wins'])
async def top_players(message: types.Message):
    cursor.execute('SELECT user_id, coins_win FROM users ORDER BY coins_win DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("🏆 <b>Топ игроков:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "🏆 <b>Топ 10 игроков по выигранным коинам:</b>\n\n"
    
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name  # Получаем полное имя пользователя
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win} 🪙\n"

    await message.answer(top_message, parse_mode='html')

@dp.message_handler(commands=['top_coins'])
async def top_players(message: types.Message):
    cursor.execute('SELECT user_id, ZBX_coins FROM users ORDER BY ZBX_coins DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("🏆 <b>Топ игроков:</b> Нет данных о выигрышах.", parse_mode='html')
        return

    top_message = "🏆 <b>Топ 10 богачей по коинам:</b>\n\n"
    
    for rank, (user_id, coins_win) in enumerate(top_users, start=1):
        user = await bot.get_chat(user_id)
        full_name = user.full_name  # Получаем полное имя пользователя
        top_message += f"<b>{rank}. <a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a></b> – {coins_win} 🪙\n"

    await message.answer(top_message, parse_mode='html')


@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name  # Получаем полное имя пользователя
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        await message.answer("⚠️ У вас еще нет профиля.")
        return

    balance, coins_win, coins_loss = result

    profile_message = (
        f"👤 <b><a href=\"tg://openmessage?user_id={user_id}\">{full_name}</a>:</b>\n\n"
        f"🔑 <b>ID:</b> <code>{user_id}</code>\n"
        f"💰 <b>Баланс:</b> {balance:.2f} 🪙 ZBX\n\n"
        f"🟢 <b>Выигрышей:</b> {coins_win} 🪙 \n"
        f"🔴 <b>Проигрышей:</b> {coins_loss} 🪙 \n\n"
    )

    await message.answer(profile_message, parse_mode='html')



@dp.message_handler(commands=['pay'])
async def pay_coins(message: types.Message):
    # Проверяем, является ли пользователь администратором
    if message.from_user.id != admin_id:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    try:
        # Извлекаем user_id и количество коинов из сообщения
        _, user_id, amount = message.text.split()
        user_id = int(user_id)  # Преобразуем user_id в целое число
        amount = int(amount)  # Преобразуем количество коинов в целое число

        # Обновляем баланс пользователя
        cursor.execute("UPDATE users SET ZBX_coins = ZBX_coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

        # Уведомляем администратора о пополнении
        await message.reply(f"💸 Баланс пользователя – ID: {user_id} был пополнен на +{amount} 🪙 ZBX...")

        # Уведомляем пользователя о пополнении баланса
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
    # Проверяем, является ли пользователь администратором
    if message.from_user.id != admin_id:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    try:
        # Извлекаем user_id, количество коинов и причину из сообщения
        parts = message.text.split()
        if len(parts) < 4:
            await message.reply("Ошибка: убедитесь, что вы ввели правильный формат команды: /withdraw (user_id) (amount) (reason)")
            return

        user_id = int(parts[1])  # Преобразуем user_id в целое число
        amount = int(parts[2])  # Преобразуем количество коинов в целое число
        reason = ' '.join(parts[3:])  # Объединяем оставшиеся части сообщения в одну строку как причину

        # Проверяем, достаточно ли коинов на балансе
        cursor.execute("SELECT ZBX_coins FROM users WHERE user_id = ?", (user_id,))
        balance = cursor.fetchone()
        
        if balance is None:
            await message.reply(f"Пользователь с ID {user_id} не найден.")
            return

        current_balance = balance[0]
        if current_balance < amount:
            await message.reply(f"Недостаточно коинов на балансе пользователя {user_id}. Текущий баланс: {current_balance} 🪙 ZBX.")
            return

        # Обновляем баланс пользователя
        cursor.execute("UPDATE users SET ZBX_coins = ZBX_coins - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

        # Уведомляем администратора о выводе
        await message.reply(f"💰 Баланс пользователя – ID: {user_id} был уменьшен на –{amount} 🪙 ZBX по причине: {reason}.")

        # Уведомляем пользователя о выводе баланса
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
    balance = result[0] if result else 0
    c_wins = result[1]
    c_loss = result[2]

    if bet > balance:
        await message.answer("У вас недостаточно средств для этой ставки.")
        return

    # Сначала вычитаем ставку из баланса
    new_balance = balance - bet
    cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins) VALUES (?, ?)', (user_id, new_balance))

    data = await bot.send_dice(message.chat.id, emoji='🎰')
    combo = get_combo_text(data.dice.value)
    multiplier = calculate_multiplier(combo)

    if multiplier >= 1:
        winnings = int(bet * multiplier) # Полный выигрыш
        coins_win = winnings - bet + c_wins
        coins_loss = c_loss
        new_balance += winnings
        emoji = "<b>🟢 Повезло!</b>"  # Зеленый эмодзи для выигрыша
    else:
        winnings = int(bet * multiplier)  # Возвращаем часть ставки
        coins_loss = bet - winnings + c_loss
        coins_win = c_wins
        new_balance += winnings
        emoji = "<b>🔴 Не повезло!</b>"  # Красный эмодзи для проигрыша
        
        # Обновляем баланс в базе данных
    cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_balance, coins_win, coins_loss))
    conn.commit()

    # Формируем общее сообщение
    await asyncio.sleep(1.5)
    await message.answer(
        f"{emoji}\n\n<b>💸 Ставка:</b> –{bet} 🪙 ZBX\n"
        f"<b>👀 Выпало:</b> <i>{', '.join(combo)}...</i>\n"
        f"🔎 <b>Выигрышь:</b> +{bet * multiplier:.2f} 🪙 ZBX ({multiplier:.2f}X)\n\n"
        f"💰 <b>Ваш новый баланс:</b> {new_balance} 🪙 ZBX"
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
    balance, coins_win, coins_loss = result if result else (0, 0, 0)

    if bet > balance:
        await message.answer("🚫 У вас недостаточно 🪙 ZBX для этой ставки")
        return

    data = await bot.send_dice(message.chat.id, emoji='🎲')
    rolled_number = data.dice.value

    if rolled_number == target_number:
        winnings = int(bet * 2.25)
        new_balance = balance + winnings
        coins_win += int(winnings / 2.25)  # Увеличиваем сумму выигранных монет
        cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_balance, coins_win, coins_loss))
        await asyncio.sleep(2)
        await message.answer(f"<b>👌 Победа!</b>\n\n<b>🟢 Выпало число:</b> {rolled_number}\n<b>✅ Ставка (x2.25):</b> <code>+{winnings} 🪙 ZBX</code>\n\n<b>💰 Ваш новый баланс:</b> {new_balance} 🪙 ZBX", parse_mode='html')
    else:
        new_balance = balance - bet
        coins_loss += bet  # Увеличиваем сумму проигранных монет
        cursor.execute('INSERT OR REPLACE INTO users (user_id, ZBX_coins, coins_win, coins_loss) VALUES (?, ?, ?, ?)', (user_id, new_balance, coins_win, coins_loss))
        await asyncio.sleep(2)
        await message.answer(f"<b>👎 Проигрыш!</b>\n\n<b>🔴 Выпало число:</b> {rolled_number}\n<b>❎ Ставка:</b> <code>–{bet} 🪙 ZBX</code>\n\n<b>💰 Ваш новый баланс:</b> {new_balance} 🪙 ZBX", parse_mode='html')

    conn.commit()


@dp.message_handler(commands=['bask'])
async def roll_basketball(message: types.Message):
    # Получаем аргументы команды
    args = message.get_args().split()
    
    # Проверяем, что ставка передана и является числом
    if len(args) != 1 or not args[0].isdigit():
        await message.answer("⚠️ Пожалуйста, укажите ставку от 50 до 1000. \n\nПример: /bask 100")
        return
    
    stake = int(args[0])

    # Проверяем, что ставка в пределах допустимого диапазона
    if stake < 50 or stake > 100000:
        await message.answer("⚠️ Ставка должна быть от 50 до 100000.")
        return

    user_id = message.from_user.id

    # Получаем баланс пользователя из базы данных
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] < stake:
        await message.answer("⚠️ У вас недостаточно 🪙 ZBX для ставки.")
        return

    # Отправляем баскетбол и получаем значение
    data = await bot.send_dice(message.chat.id, emoji='🏀')
    basketball_value = data.dice.value

    # Определяем выигрыш в зависимости от значения баскетбольного броска
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

    # Обновляем баланс пользователя в базе данных
    new_balance = result[0] - stake + payout
    cursor.execute('UPDATE users SET ZBX_coins = ?, coins_win = ?, coins_loss = ? WHERE user_id = ?', (new_balance, new_win, new_loss, user_id))
    conn.commit()

    # Отправляем результат пользователю
    await asyncio.sleep(1.5)
    await message.answer(f'<b>{message_result}</b>\n\n<b>💸 Ставка:</b> –{stake} 🪙 ZBX\n<b>👌 Выигрышь:</b> +{payout} 🪙 ZBX\n\n<b>💰 Ваш новый баланс:</b> {new_balance:.2f} 🪙', parse_mode='html')



@dp.message_handler(commands=['dart'])
async def roll_dice(message: types.Message):
    # Получаем аргументы команды
    args = message.get_args().split()
    
    # Проверяем, что ставка передана и является числом
    if len(args) != 1 or not args[0].isdigit():
        await message.answer("⚠️ Пожалуйста, укажите ставку от 50 до 1000. \n\nПример: /dart 100")
        return
    
    stake = int(args[0])

    # Проверяем, что ставка в пределах допустимого диапазона
    if stake < 50 or stake > 100000:
        await message.answer("⚠️ Ставка должна быть от 50 до 100000.")
        return

    user_id = message.from_user.id

    # Получаем баланс пользователя из базы данных
    cursor.execute('SELECT ZBX_coins, coins_win, coins_loss FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] < stake:
        await message.answer("⚠️ У вас недостаточно 🪙 ZBX для ставки.")
        return

    # Отправляем дартс и получаем значение
    data = await bot.send_dice(message.chat.id, emoji='🎯')
    dart_value = data.dice.value

    # Определяем выигрыш в зависимости от значения дартса
    if dart_value == 1:
        payout = 0
        new_loss = result[2] + stake
        new_win = result[1]
        message_result = "🤕 Не повезло! (0X)"
    elif dart_value == 2:
        payout = int(stake * 0.2)
        new_loss = stake - payout + result[2]
        new_win = result[1]
        message_result = "😔 Не повезло! (0.2X)"
    elif dart_value == 3:
        payout = int(stake * 0.35)
        new_loss = stake - payout + result[2]
        new_win = result[1]
        message_result = "🙁 Не повезло! (0.35X)"
    elif dart_value == 4:
        payout = int(stake * 0.7)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🫠 Почти в точку! (0.7X)"
    elif dart_value == 5:
        payout = int(stake * 0.85)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🫡 Почти в точку! (0.85X)"
    elif dart_value == 6:
        payout = int(stake * 2.75)
        new_win = payout - stake + result[1]
        new_loss = result[2]
        message_result = "🤘 Отлично! Прям в точку! (2.75X)"

    # Обновляем баланс пользователя в базе данных
    new_balance = result[0] - stake + payout
    cursor.execute('UPDATE users SET ZBX_coins = ?, coins_win = ?, coins_loss = ? WHERE user_id = ?', (new_balance, new_win, new_loss, user_id))
    conn.commit()

    # Отправляем результат пользователю
    await asyncio.sleep(1.5)
    await message.answer(f'<b>{message_result}</b>\n\n<b>💸 Ставка:</b> –{stake} 🪙 ZBX\n<b>👌 Выигрышь:</b> +{payout} 🪙 ZBX\n\n<b>💰 Ваш новый баланс:</b> {new_balance:.2f} 🪙', parse_mode='html')


@dp.message_handler(commands=['work'])
async def work_command(message: types.Message):
    user_id = message.from_user.id
    current_time = int(datetime.now().timestamp())

    # Получаем информацию о пользователе из базы данных
    cursor.execute('SELECT ZBX_coins, kd_work FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    # Если пользователь не существует, создаем запись
    if result is None:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        ZBX_coins = random.randint(5000, 10000)
        cursor.execute('UPDATE users SET ZBX_coins = ?, kd_work = ? WHERE user_id = ?', (ZBX_coins, current_time, user_id))
        conn.commit()
        await message.answer(f"💰 Вы получили {ZBX_coins} коинов!")
        return

    ZBX_coins, last_work_time = result

    # Преобразуем last_work_time в целое число
    last_work_time = int(last_work_time)

    # Проверяем, прошло ли 8 часов с последней работы
    if current_time < last_work_time + 8 * 1800:
        remaining_time = (last_work_time + 8 * 1800 - current_time)
        await message.answer(f"⏳ Вы можете работать снова через {remaining_time // 3600}ч. {(remaining_time % 3600) // 60}м.")
        return

    # Выдаем случайное количество коинов
    coins = random.randint(5000, 10000)
    ZBX_coins += coins
    cursor.execute('UPDATE users SET ZBX_coins = ?, kd_work = ? WHERE user_id = ?', (ZBX_coins, current_time, user_id))
    conn.commit()
    await message.answer(f"💰 Вы получили {coins} коинов! Теперь у вас {ZBX_coins} коинов.")




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
