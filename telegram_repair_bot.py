import uuid
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Етапи розмови
TYPE, ISSUE, NAME, PHONE, CHECK_STATUS = range(5)
clients = {}  # Зберігання даних замовлень


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот сервісу ремонту техніки. Обери тип пристрою:",
        reply_markup=ReplyKeyboardMarkup([["Смартфон", "Ноутбук"], ["ПК", "Інше"]], one_time_keyboard=True)
    )
    return TYPE

async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text
    await update.message.reply_text("Яка проблема з пристроєм?")
    return ISSUE

async def get_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["issue"] = update.message.text
    await update.message.reply_text("Введіть ваше ім’я:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Номер телефону:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    order_id = f"ORD{str(uuid.uuid4())[:8].upper()}"
    clients[order_id] = context.user_data.copy()
    await update.message.reply_text(f"Дякуємо, {context.user_data['name']}! Ваш код замовлення: {order_id}")
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть код замовлення (наприклад, ORD1234AB):")
    return CHECK_STATUS

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    data = clients.get(code)
    if data:
        await update.message.reply_text(f"Статус: В роботі\nТип: {data['type']}\nПроблема: {data['issue']}")
    else:
        await update.message.reply_text("Замовлення не знайдено.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

app = ApplicationBuilder().token("7765881253:AAGeSg759wEnbkrqIINg3gK6xfyCeco3SPw").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type)],
        ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_issue)],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        CHECK_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_status)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler("status", status))

app.run_polling()