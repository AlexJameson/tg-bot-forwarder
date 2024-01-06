#!/usr/bin/env python3
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ContextTypes, ApplicationBuilder
import configparser
import logging

config = configparser.ConfigParser()
config.read("config.ini")

bot_token = config.get("secrets", "TELEGRAM_ACCESS_TOKEN")
channel_id = config.get("secrets", "SECRET_CHANNEL_ID")
group_id = config.get("secrets", "GROUP_ID")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def repost(update: Update, context: CallbackContext):
    original_message = update.message.reply_to_message
    if original_message is not None:
        link = f"https://t.me/{group_id}/{original_message.message_id}"

        target_chat_id = channel_id 
        await context.bot.send_message(chat_id=channel_id, text=f"[Перейти к сообщению]({link})", disable_web_page_preview = True, parse_mode="MarkdownV2")
        await context.bot.forward_message(chat_id=target_chat_id,
                                            from_chat_id=original_message.chat.id,
                                            message_id=original_message.message_id)
    else:
        await update.effective_message.reply_text("Ответьте на сообщение командой /repost чтобы переслать его.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Я бот, который пересылает сообщения. Меня можно добавить в чат, чтобы я пересылал сообщения в канал или в другой чат. Свяжитесь с моим создателем, если вам это интересно.")

def main():
    print("I'm working")
    application = ApplicationBuilder().token(bot_token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CommandHandler("repost", repost))
    application.run_polling()

if __name__ == "__main__":
    main()

# ps ax | grep main.py
# kill PID
