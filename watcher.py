import subprocess
import time
import logging
import telebot
import asyncio
import hashlib

# Your API token, admin ID, developer ID, and developer username
API_TOKEN = '7230364476:AAEj4oTyDcrlWBe_X0mR5ZccaV3sg0_va4Y'
ADMIN_ID = '6904449442'
DEVELOPER_ID = '6904449442'
DEVELOPER_USERNAME = '@NINJA666'
MAX_RESTARTS = 500
RESTART_PERIOD = 60  # Seconds

# Your watermark
WATERMARK = 'Bot made and developed by @NINJA666'
COMBINED_HASH = 'a0ff3cb11e39f3c9a18dfe94714f6586'  # Replace with your actual combined hash

def calculate_hash(*args):
    """Calculate the hash of the given text arguments."""
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(arg.encode('utf-8'))
    return hasher.hexdigest()

def verify_combined_hash():
    """Verify the integrity of the watermark, developer ID, and developer username."""
    current_hash = calculate_hash(WATERMARK, DEVELOPER_ID, DEVELOPER_USERNAME)
    if current_hash != COMBINED_HASH:
        raise ValueError("Combined hash integrity check failed. The watermark, developer ID, or developer username has been tampered with.")

def start_bot():
    """Start the bot script as a subprocess."""
    return subprocess.Popen(['python', 'm.py'])

async def notify_admin(message):
    """Send a notification message to the admin via Telegram."""
    try:
        bot = telebot.TeleBot(API_TOKEN)
        bot.send_message(ADMIN_ID, message)
        logging.info("Admin notified: %s", message)
    except Exception as e:
        logging.error("Failed to send message to admin: %s", e)

async def main():
    """Main function to manage bot process lifecycle."""
    verify_combined_hash()  # Verify the combined hash integrity before starting
    
    restart_count = 0
    last_restart_time = time.time()
    
    while True:
        if restart_count >= MAX_RESTARTS:
            current_time = time.time()
            if current_time - last_restart_time < RESTART_PERIOD:
                wait_time = RESTART_PERIOD - (current_time - last_restart_time)
                logging.warning("Maximum restart limit reached. Waiting for %.2f seconds...", wait_time)
                await notify_admin(f"Maximum restart limit reached. Waiting for {int(wait_time)} seconds before retrying.")
                await asyncio.sleep(wait_time)
            restart_count = 0
            last_restart_time = time.time()

        logging.info("Starting the bot...")
        process = start_bot()
        await notify_admin("Bot is starting...")

        while process.poll() is None:
            await asyncio.sleep(5)
        
        logging.warning("Bot process terminated. Restarting in 10 seconds...")
        await notify_admin("The bot has crashed and will be restarted in 10 seconds.")
        restart_count += 1
        await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except ValueError as e:
        logging.error(e)
    except KeyboardInterrupt:
        logging.info("Watcher script terminated by user.")
