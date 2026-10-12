#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT RƯƠNG LIVE TIKTOK
=====================

Cài:
  pip install python-telegram-bot==21.6

Cách dùng:
  1. Telegram → @BotFather → /newbot → copy token
  2. Dán token vào BOT_TOKEN bên dưới
  3. python bot_ruong.py
  4. Vào bot gửi /start rồi /lives
"""

import os
import json
import random
import logging
from pathlib import Path
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============ CẤU HÌNH ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8866106077:AAEByEp1VpgqEnILtNDQi0sOHqDTT3sTbyI")
DATA_FILE = Path("user_data.json")
REFRESH_SECONDS = 60

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
log = logging.getLogger("bot")

# ============ DỮ LIỆU USER ============
def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

db = load_data()

def user(uid):
    key = str(uid)
    if key not in db:
        db[key] = {"xu": 0, "opened": []}
        save_data(db)
    return db[key]

# ============ SCRAPER MẪU ============
def scrape_lives():
    names = [
        "@idol_vietnam", "@live_hot_girl", "@tiktok_star",
        "@game_live_vn", "@beauty_queen", "@music_live", "@dance_live"
    ]
    result = []
    for i, name in enumerate(names, 1):
        has = random.random() > 0.3
        result.append({
            "id": i,
            "user": name,
            "viewers": f"{random.randint(2, 40)}.{random.randint(0,9)}K",
            "chest": has,
            "time": random.randint(10, 180) if has else 0,
        })
    return result

lives_list = scrape_lives()

async def job_refresh(context: ContextTypes.DEFAULT_TYPE):
    global lives_list
    lives_list = scrape_lives()
    log.info(f"Refresh live: {len(lives_list)} phòng")

# ============ LỆNH ============
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = user(update.effective_user.id)
    await update.message.reply_text(
        f"Chào {update.effective_user.first_name}!\n\n"
        f"Bot Rương Live TikTok\n"
        f"Xu: <b>{u['xu']}</b>\n\n"
        f"/lives - Xem live + mở rương\n"
        f"/xu - Xem xu\n"
        f"/help - Hướng dẫn",
        parse_mode="HTML"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hướng dẫn:\n"
        "/lives - Danh sách live có rương\n"
        "/xu - Số xu hiện tại\n\n"
        "Bot tự làm mới danh sách mỗi 60 giây.\n"
        "Dữ liệu hiện là mẫu."
    )

async def cmd_xu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = user(update.effective_user.id)
    await update.message.reply_text(f"Bạn có <b>{u['xu']}</b> Xu", parse_mode="HTML")

async def cmd_lives(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"<b>Live TikTok</b>\n<i>{datetime.now().strftime('%H:%M:%S')}</i>\n\n"
    buttons = []
    for item in lives_list:
        st = "🎁 Có rương" if item["chest"] else "Không có"
        text += f"{item['user']} | {item['viewers']} | {st}\n"
        if item["chest"]:
            buttons.append([InlineKeyboardButton(
                f"Mở rương {item['user']}",
                callback_data=f"open_{item['id']}"
            )])
    if not buttons:
        text += "\nKhông có rương."
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=markup)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = user(q.from_user.id)

    if not q.data.startswith("open_"):
        return

    lid = int(q.data.split("_")[1])
    item = next((x for x in lives_list if x["id"] == lid), None)

    if not item or not item["chest"]:
        await q.edit_message_text("Rương đã hết.")
        return
    if lid in u["opened"]:
        await q.edit_message_text("Bạn đã mở rương này rồi!")
        return

    amount = random.randint(3, 50)
    u["xu"] += amount
    u["opened"].append(lid)
    save_data(db)

    await q.edit_message_text(
        f"Mở thành công!\n"
        f"Phòng: {item['user']}\n"
        f"+{amount} Xu\n"
        f"Tổng: <b>{u['xu']}</b> Xu",
        parse_mode="HTML"
    )

# ============ CHẠY ============
def main():
    if not BOT_TOKEN or BOT_TOKEN == "THAY_TOKEN_VAO_DAY":
        print("Chưa có token!")
        print("1. Telegram → @BotFather → /newbot")
        print("2. Copy token dán vào BOT_TOKEN trong file này")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("lives", cmd_lives))
    app.add_handler(CommandHandler("xu", cmd_xu))
    app.add_handler(CallbackQueryHandler(on_button))

    if app.job_queue:
        app.job_queue.run_repeating(job_refresh, interval=REFRESH_SECONDS, first=10)

    print("Bot đang chạy... Ctrl+C để dừng")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
