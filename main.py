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

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def hashtags(words):
    special_characters = set("-_*[]()~`>#+=|{}.!")
    escaped_words = []
    
    for char in words:
        if char in special_characters:
            escaped_words.append(f"\\{char}")
        else:
            escaped_words.append(char)
    "".join(escaped_words)        
    return " ".join([f"\#{word}" for word in escaped_words])

async def repost(update: Update, context: CallbackContext):
    original_message = update.message.reply_to_message
    if original_message is not None:
        # I was unable to get the Group ID from the context for some reason so I passed group.id directly
        link = f"https://t.me/{group_id}/{original_message.message_id}"
        target_chat_id = channel_id
        hashtag_words = context.args
        hashtag_text = await hashtags(hashtag_words)

        await context.bot.send_message(chat_id=target_chat_id, text=f"[Перейти к сообщению]({link})\n{hashtag_text}", disable_web_page_preview=True, parse_mode="MarkdownV2")
        await context.bot.forward_message(chat_id=target_chat_id,
                                            from_chat_id=original_message.chat.id,
                                            message_id=original_message.message_id)
    else:
        await update.effective_message.reply_text("Ответьте на сообщение в чате командой /repost.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Я бот, который пересылает сообщения. Меня можно добавить в чат, чтобы я пересылал сообщения в канал или в другой чат. Свяжитесь с моим создателем по ссылке в описании, если вам это интересно.")

def main():
    print("I'm working")
    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("repost", repost))
    application.run_polling()

if __name__ == "__main__":
    main()

# ps ax | grep main.py
# kill PID
