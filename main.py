from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from datetime import datetime, timedelta
import config  # Import your configuration

# Initialize bot and updater
bot = Bot(token=config.TOKEN)
updater = Updater(token=config.TOKEN, use_context=True)
job_queue = updater.job_queue

# Store file IDs and their post times
file_queue = []
posted_files = set()  # To track posted file IDs to avoid duplicates

# Schedule interval in seconds (hard-coded to 30 minutes)
SCHEDULE_INTERVAL = 30 * 60  # 30 minutes

def start(update: Update, context: CallbackContext):
    if update.effective_user.id == config.OWNER_ID:
        welcome_message = (
            "Welcome to the Automated Posting Bot!\n\n"
            "Here’s what you can do:\n"
            "/addfile <file_id> - Add a file ID to the queue for posting.\n"
            "/broadcast <message> - Send a message to the target channel.\n\n"
            "Usage:\n"
            "1. Use /addfile command to add file IDs that you want to post. Ensure the file ID is from the storage channel.\n"
            "2. The bot will automatically post each file to the target channel every 30 minutes.\n"
            "3. Use /broadcast to send a message to the target channel.\n"
            "4. Only the owner can use these commands.\n\n"
            "The bot will handle posting files and broadcasting messages as scheduled."
        )
        update.message.reply_text(welcome_message)
    else:
        update.message.reply_text("You are not authorized to use this bot.")

def add_file(update: Update, context: CallbackContext):
    if update.effective_user.id == config.OWNER_ID:
        if context.args:
            file_id = ' '.join(context.args)
            if file_id not in posted_files:
                file_queue.append(file_id)
                update.message.reply_text("File added to the queue.")
            else:
                update.message.reply_text("This file has already been posted.")
        else:
            update.message.reply_text("Please provide a file ID.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id == config.OWNER_ID:
        if context.args:
            message = ' '.join(context.args)
            context.bot.send_message(chat_id=config.TARGET_CHANNEL, text=message)
            update.message.reply_text("Message sent to the target channel.")
        else:
            update.message.reply_text("Please provide a message to broadcast.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def post_files(context: CallbackContext):
    global file_queue, posted_files
    if file_queue:
        file_id = file_queue.pop(0)
        if file_id not in posted_files:
            context.bot.forward_message(chat_id=config.TARGET_CHANNEL, from_chat_id=config.STORAGE_CHANNEL, message_id=file_id)
            posted_files.add(file_id)
        else:
            context.bot.send_message(chat_id=config.TARGET_CHANNEL, text="No files to post.")
    else:
        context.bot.send_message(chat_id=config.TARGET_CHANNEL, text="No files to post.")

def schedule_jobs():
    # Post files based on the hard-coded schedule interval
    job_queue.run_repeating(post_files, interval=SCHEDULE_INTERVAL, first=datetime.now() + timedelta(seconds=30))

# Add handlers
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('addfile', add_file))
updater.dispatcher.add_handler(CommandHandler('broadcast', broadcast))

# Start the bot
if __name__ == '__main__':
    schedule_jobs()
    updater.start_polling()
    updater.idle()
