#!/usr/bin/env python3
import configparser
import logging
import re
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ContextTypes, ApplicationBuilder, MessageHandler, filters
from tinydb import TinyDB, Query

config = configparser.ConfigParser()
config.read("config.ini")

bot_token = config.get("secrets", "TELEGRAM_ACCESS_TOKEN")
channel_id = config.get("secrets", "SECRET_CHANNEL_ID")
group_id = config.get("secrets", "GROUP_ID")
pinned_message_id = config.get("secrets", "PINNED_MESSAGE_ID")

db = TinyDB('db.json')

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def get_pinned_message(context: CallbackContext, target_chat_id):
    chat = await context.bot.get_chat(target_chat_id)
    return chat.pinned_message 

async def update_pinned_message(context: CallbackContext, channel_id, pinned_message_id, hashtag_counts):
    # Fetch the current pinned message
    pinned_message = await get_pinned_message(context, channel_id)
    
    # Extract the existing text
    existing_text = pinned_message.text.split('Hashtags in this channel:')[0]

    # Append the new hashtag counts
    hashtag_string = "\n".join(f"{tag}: {count}" for tag, count in hashtag_counts.items())
    message_text = f"{existing_text}Hashtags in this channel:\n\n{hashtag_string}"

    await context.bot.edit_message_text(
        chat_id=channel_id, message_id=pinned_message_id, text=message_text
    )


async def handle_new_message(update: Update, context: CallbackContext):

    message_text = update.effective_message.text
    if update.effective_message.caption: # Check if there's a caption (reposts or media)
        message_text += " " + update.effective_message.caption

    hashtag_set = re.findall(r"#\w+", message_text)

    if hashtag_set:
        update_pinned = False
        for hashtag in hashtag_set:
            hashtag_query = Query()
            hashtag_entry = db.get(hashtag_query.hashtag == hashtag)
            if hashtag_entry:
                updated_count = hashtag_entry['count'] + 1
                db.update({'count': updated_count}, hashtag_query.hashtag == hashtag)
                update_pinned = True
            else:
                db.insert({'hashtag': hashtag, 'count': 1})
                update_pinned = True

        if update_pinned:
            hashtag_counts = {entry['hashtag']: entry['count'] for entry in db.all()}
            await update_pinned_message(context, channel_id, pinned_message_id, hashtag_counts)


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

        await context.bot.send_message(chat_id=target_chat_id, text=f"[Go to message]({link})\n{hashtag_text}", disable_web_page_preview=True, parse_mode="MarkdownV2")
        await context.bot.forward_message(chat_id=target_chat_id,
                                          from_chat_id=original_message.chat.id,
                                          message_id=original_message.message_id)

        # Extract hashtags from hashtag_text
        hashtag_set = re.findall(r"#\w+", hashtag_text)

        if hashtag_set:
            update_pinned = False
            for hashtag in hashtag_set:
                hashtag_query = Query()
                hashtag_entry = db.get(hashtag_query.hashtag == hashtag)
                if hashtag_entry:
                    updated_count = hashtag_entry['count'] + 1
                    db.update({'count': updated_count}, hashtag_query.hashtag == hashtag)
                    update_pinned = True
                else:
                    db.insert({'hashtag': hashtag, 'count': 1})
                    update_pinned = True

            if update_pinned:
                hashtag_counts = {entry['hashtag']: entry['count'] for entry in db.all()}
                await update_pinned_message(context, channel_id, pinned_message_id, hashtag_counts)

            # Here should be logic for handling and processing the forwarded message to extract hashtags
            # However, I didn't manage to implement it. Good enough for MVP.
    else:
        await update.effective_message.reply_text("Reply to a message with /repost.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I am a bot to forward messages.")

def main():
    print("I'm working")
    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("repost", repost))
    application.add_handler(MessageHandler(filters.TEXT & filters.UpdateType.CHANNEL_POSTS, handle_new_message))
    application.run_polling()

if __name__ == "__main__":
    main()
