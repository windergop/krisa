import logging
import random
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
from telegram.ext import MessageHandler, filters

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранение данных о пользователях (в памяти)
users_data = {}

# Инициализация данных пользователя, если его ещё нет
def initialize_user(user_id, username):
    if user_id not in users_data:
        users_data[user_id] = {
            'username': username,
            'balance': 0,
            'last_tapnut': None
        }
def initialize_user(user_id, username):
    if user_id not in users_data:
        users_data[user_id] = {
            'username': username,
            'balance': 0,
            'last_tapnut': None,
            'bonuski': 0  # Добавляем поле для хранения бонусок
        }
        

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/me - инфо про тебя\n"
        "/tapnut - собрать ежедневный бонус\n"
        "/vivod - вывести деньги\n"
        "/help - поможет с чем угодно\n"
        "/leaderboard - лидерборд\n"
        "/casino - испытайте удачу\n"
        "/casino_1to10 - угадай число от 1 до 10 и забери 100Х\n"
        "/casinoWIN - рулетка за 30 $KRISA или за бонуску. забери 10Х \n"
        "Forbes bot rating: ⭐️⭐️⭐️⭐️⭐️ (5/5)"
    )

# Команда /me
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    balance = users_data[user_id]['balance']
    bonuski = users_data[user_id]['bonuski']  # Добавляем количество бонусок

    await update.message.reply_text(
        f"@{username}, у тебя {balance} $KRISA и {bonuski} бонусок.\n\n"
        "Сыграй в /casino или в /casinoWIN!\n\n"
        "Сегодня удача на твоей стороне!" 
        
        "Все команды: /start"
    )

# Команда /tapnut
async def tapnut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    now = datetime.now()
    last_tapnut = users_data[user_id]['last_tapnut']

    if last_tapnut is None or now - last_tapnut > timedelta(hours=24):
        reward = random.randint(1, 30)
        users_data[user_id]['balance'] += reward
        users_data[user_id]['last_tapnut'] = now
        await update.message.reply_text(f"@{username}, ты получаешь {reward} $KRISA! Поздравляем!💵" "❗️Все команды: /start" )
    else:
        await update.message.reply_text("Попробуй позже..." "❗️Все команды: /start")

# Команда /vivod
async def vivod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("скоро...")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вопросы? спроси у @fleo431")

# Команда /leaderboard
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaderboard_text = "Лидерборд:\n"
    sorted_users = sorted(users_data.items(), key=lambda x: x[1]['balance'], reverse=True)
    
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        leaderboard_text += f"{i}. @{user_data['username']} — {user_data['balance']} $KRISA\n"
    
    await update.message.reply_text(leaderboard_text)

# Команда /casino
async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    balance = users_data[user_id]['balance']
    
    if balance > 0:
        chance = random.random()
        if chance <= 0.5:  # 50% шанс удвоить баланс
            users_data[user_id]['balance'] *= 2
            await update.message.reply_text(f"@{username}, удача !💰 Твой баланс удвоен:  {users_data[user_id]['balance']} $KRISA!")
        else:  # 60% шанс разделить баланс пополам
            users_data[user_id]['balance'] = max(users_data[user_id]['balance'] // 2, 0)
            await update.message.reply_text(f"@{username}, проебаал...❌ Твой баланс: {users_data[user_id]['balance']} $KRISA.")
    else:
        await update.message.reply_text(f"@{username}, у тебя нет $KRISA для игры в казино!")
# Команда /giveaway - Раздача $KRISA на 5 человек
async def giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    creator_id = 727265381  # Замени на свой Telegram ID
    
    # Проверяем, что команду выполняет создатель бота
    if user_id == creator_id:
        if len(context.args) >= 1:
            try:
                amount = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Укажи корректное количество $KRISA.")
                return
            
            # Выбираем 5 случайных пользователей
            if len(users_data) >= 5:
                selected_users = random.sample(list(users_data.keys()), 5)
                usernames = [f"@{users_data[uid]['username']}" for uid in selected_users]

                for uid in selected_users:
                    users_data[uid]['balance'] += amount
                
                await update.message.reply_text(f"{' '.join(usernames)}\nвы получили по {amount} $KRISA!")
            else:
                await update.message.reply_text("Недостаточно пользователей для раздачи.")
        else:
            await update.message.reply_text("Использование: /giveaway <amount>")
    else:
        await update.message.reply_text("Эта команда доступна только создателю бота.")

async def bonuska(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    creator_id = 727265381  # Замени на свой Telegram ID

    # Проверяем, что команду выполняет создатель бота
    if user_id == creator_id:
        if len(context.args) > 0:  # Если указан конкретный username
            target_username = context.args[0].lstrip('@')  # Убираем '@' если есть
            target_user_id = next((uid for uid, data in users_data.items() if data['username'] == target_username), None)

            if target_user_id:
                bonuski_amount = random.randint(1, 3)
                users_data[target_user_id]['bonuski'] += bonuski_amount
                await update.message.reply_text(f"@{target_username} получил {bonuski_amount} бонусок!")
            else:
                await update.message.reply_text(f"Пользователь @{target_username} не найден.")
        else:  # Рандомное распределение бонусок
            if len(users_data) >= 1:
                target_user_id = random.choice(list(users_data.keys()))
                bonuski_amount = random.randint(1, 3)
                users_data[target_user_id]['bonuski'] += bonuski_amount
                target_username = users_data[target_user_id]['username']
                await update.message.reply_text(f"@{target_username} получил {bonuski_amount} бонусок!")
            else:
                await update.message.reply_text("Недостаточно пользователей для выдачи бонусок.")
    else:
        await update.message.reply_text("Эта команда доступна только создателю бота.")

# Команда /casino_1to10 - угадай число от 1 до 10
async def casino_1to10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    # Бот загадывает число от 1 до 10
    users_data[user_id]['casino_number'] = random.randint(1, 10)
    await update.message.reply_text(f"@{username}, я загадал число от 1 до 10. Угадаешь — Х100 к балансу, не угадаешь — обнуление. Угадывай...")

# Обработка угадывания числа
async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    if 'casino_number' in users_data[user_id]:
        try:
            user_guess = int(update.message.text)
        except ValueError:
            await update.message.reply_text("ОТ ОДНОГО ДО ДЕСЯТИ!")
            return

        if 1 <= user_guess <= 10:
            correct_number = users_data[user_id]['casino_number']
            balance = users_data[user_id]['balance']

            if user_guess == correct_number:
                users_data[user_id]['balance'] *= 100
                await update.message.reply_text(f"@{username}, ЧОООО угадал! Лови Х10 🎰✅\nТеперь твой баланс: {users_data[user_id]['balance']} $KRISA!")
            else:
                users_data[user_id]['balance'] = 0
                await update.message.reply_text(f"@{username}, близко, но не повезло... 🚫\nТеперь твой баланс: {users_data[user_id]['balance']} $KRISA.")
            
            # Удаляем загаданное число после попытки
            del users_data[user_id]['casino_number']
        else:
            await update.message.reply_text("ОТ ОДНОГО ДО ДЕСЯТИ!")

# Команда /casinoWIN - ставка 30 $KRISA и кручение
async def casinoWIN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    initialize_user(user_id, username)

    balance = users_data[user_id]['balance']
    bonuski = users_data[user_id]['bonuski']

    if bonuski > 0:  # Если есть бонуски
        users_data[user_id]['bonuski'] -= 1
        await update.message.reply_text(f"@{username}, списал 1 бонуску, начинаю крутить...")
    elif balance >= 30:  # Если нет бонусок, снимаем $KRISA
        users_data[user_id]['balance'] -= 30
        await update.message.reply_text(f"@{username}, списал 30 $KRISA, начинаю крутить...")
    else:
        # Если не хватает $KRISA и бонусок
        await update.message.reply_text(
            "Не хватает $KRISA или бонусок.\n"
            "Проверь баланс /me\n"
            "Забери ежедневную награду /tapnut"
        )
        return

    # Задержка в 1 секунды
    await asyncio.sleep(1)

    # Список возможных вариантов
    outcomes = [
        "||🚫🍌🍌||",
        "||🍌🚫🚫||",
        "||🚫🚫🍌||",
        "||🚫🍌🚫||",
        "||🍌🍌🚫||",
        "||🍌🍌🍌||",  # выигрышный вариант
        "||🚫🚫🚫||",
        "||🍌🚫🍌||"
    ]

    # Случайный выбор варианта
    result = random.choice(outcomes)
    await update.message.reply_text(result)

    # Если выпал вариант 6 (||🍌🍌🍌||), добавляем 300 $KRISA
    if result == "||🍌🍌🍌||":
        users_data[user_id]['balance'] += 300
        await update.message.reply_text("Поздравляем!!!💰🤙🏻🤙🏻")


# Основная функция для запуска бота
def main():
    bot_token = '7543069560:AAEEAVa3sd5gHOeGmMdEB31s9bg0VRQD2QM'  # Замени на свой токен

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("me", me))
    application.add_handler(CommandHandler("tapnut", tapnut))
    application.add_handler(CommandHandler("vivod", vivod))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("casino", casino))
    application.add_handler(CommandHandler("giveaway", giveaway))
    application.add_handler(CommandHandler("casino_1to10", casino_1to10))  # Команда с угадыванием числа
    application.add_handler(CommandHandler("casinoWIN", casinoWIN))  # Команда казино с бонусками
    application.add_handler(CommandHandler("bonuska", bonuska))  # Команда для выдачи бонусок
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))  # Обработка угадывания числа

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
