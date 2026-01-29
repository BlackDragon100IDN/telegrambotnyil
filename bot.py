#!/usr/bin/env python3
import subprocess
import logging
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext
)

# ================= CONFIG =================
TOKEN = "..."
ADMIN_FILE = "admins.json"

logging.basicConfig(level=logging.INFO)

approved_users = set()
pending_users = set()

# ================= ADMIN STORAGE =================
def load_admins():
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "w") as f:
            json.dump(["8599557076"], f)  # admin awal
    with open(ADMIN_FILE, "r") as f:
        return set(json.load(f))

def save_admins():
    with open(ADMIN_FILE, "w") as f:
        json.dump(list(ADMIN_IDS), f)

ADMIN_IDS = load_admins()

# ================= UTILS =================
def is_admin(chat_id):
    return chat_id in ADMIN_IDS

def is_allowed(chat_id):
    return is_admin(chat_id) or chat_id in approved_users

def run_cmd(cmd):
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, timeout=30
        )
        return out.decode(errors="ignore")[:3500]
    except Exception as e:
        return str(e)

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ Uptime", callback_data="cmd:uptime"),
            InlineKeyboardButton("📡 Port Status", callback_data="cmd:ss")
        ],
        [
            InlineKeyboardButton("🌐 Status Koneksi", callback_data="cmd:nmcli"),
            InlineKeyboardButton("♻ Restart EarnApp", callback_data="cmd:restart")
        ],
        [
            InlineKeyboardButton("🧹 Clear Cache", callback_data="cmd:clearcache"),
            InlineKeyboardButton("🚀 Cek Bandwidth", callback_data="cmd:bandwidth")
        ],
        [
            InlineKeyboardButton("🛠 Solve Device", callback_data="reboot_confirm")
        ]
    ])

# ================= START =================
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    if is_admin(user_id):
        approved_users.add(user_id)
        pending_users.discard(user_id)
        update.message.reply_text("👑 Admin access granted", reply_markup=main_menu())
        return

    if user_id in approved_users:
        update.message.reply_text("✅ Akses aktif", reply_markup=main_menu())
        return

    if user_id not in pending_users:
        pending_users.add(user_id)
        for admin in ADMIN_IDS:
            context.bot.send_message(
                admin,
                f"🔐 Request akses\nUser ID: {user_id}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ APPROVE", callback_data=f"approve:{user_id}"),
                    InlineKeyboardButton("❌ REJECT", callback_data=f"reject:{user_id}")
                ]])
            )

    update.message.reply_text("⏳ Menunggu persetujuan admin")

# ================= ADMIN COMMAND =================
def add_admin(update: Update, context: CallbackContext):
    if not is_admin(str(update.effective_user.id)):
        return
    if not context.args:
        update.message.reply_text("❌ Gunakan: /addadmin user_id")
        return
    uid = context.args[0]
    ADMIN_IDS.add(uid)
    save_admins()
    update.message.reply_text(f"✅ Admin ditambahkan: {uid}")

def del_admin(update: Update, context: CallbackContext):
    if not is_admin(str(update.effective_user.id)):
        return
    if not context.args:
        update.message.reply_text("❌ Gunakan: /deladmin user_id")
        return
    uid = context.args[0]
    if uid in ADMIN_IDS:
        ADMIN_IDS.remove(uid)
        save_admins()
        update.message.reply_text(f"🗑 Admin dihapus: {uid}")
    else:
        update.message.reply_text("⚠ User bukan admin")

def list_admin(update: Update, context: CallbackContext):
    if not is_admin(str(update.effective_user.id)):
        return
    update.message.reply_text(
        "👑 LIST ADMIN:\n" + "\n".join(ADMIN_IDS)
    )

# ================= BUTTON HANDLER =================
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    # APPROVAL
    if data.startswith(("approve:", "reject:")):
        if not is_admin(user_id):
            return
        act, uid = data.split(":")
        pending_users.discard(uid)
        if act == "approve":
            approved_users.add(uid)
            context.bot.send_message(uid, "✅ Disetujui, ketik /start")
            query.edit_message_text(f"Approved {uid}")
        else:
            query.edit_message_text(f"Rejected {uid}")
        return

    if not is_allowed(user_id):
        query.edit_message_text("❌ Akses ditolak")
        return

    if data == "reboot_confirm":
        if not is_admin(user_id):
            return
        query.edit_message_text(
            "🛠 *Solve Device*\n\nPerangkat akan di solve secara aman.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ YA", callback_data="reboot_now"),
                    InlineKeyboardButton("❌ BATAL", callback_data="menu")
                ]
            ])
        )

    elif data == "reboot_now":
        if not is_admin(user_id):
            return
        run_cmd("nohup sudo shutdown -r +1 'Solve Device via Telegram Bot' >/dev/null 2>&1 &")
        query.edit_message_text("🔄 Solve dijalankan.\nDevice akan reboot ±1 menit.")

    elif data == "menu":
        query.edit_message_text("📟 Menu", reply_markup=main_menu())

    elif data.startswith("cmd:"):
        cmd = data.split(":")[1]

        cmds = {
            "uptime": ("⏱ UPTIME", "uptime"),
            "ss": ("📡 PORT STATUS", "sudo ss -tupn"),
            "restart": ("♻ EARNAPP", "systemctl restart earnapp"),
            "nmcli": ("🌐 STATUS KONEKSI", "nmcli device status"),
            "clearcache": ("🧹 CLEAR CACHE", "sudo rm -rf /tmp/* /var/tmp/* && sudo apt clean"),
            "bandwidth": (
                "🚀 CEK BANDWIDTH",
                "curl -L http://speed.cloudflare.com/__down?bytes=1000000 "
                "-o /dev/null -w 'Time: %{time_total}s\\nSpeed: %{speed_download} bytes/sec\\n'"
            )
        }

        if cmd in cmds:
            title, shell = cmds[cmd]
            out = run_cmd(shell)
            query.edit_message_text(
                f"{title}\n```\n{out}\n```",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅ Back", callback_data="menu")]
                ])
            )

# ================= SHELL CMD =================
def shell_cmd(update: Update, context: CallbackContext):
    if not is_admin(str(update.effective_user.id)):
        return
    if update.message.text.startswith("!"):
        out = run_cmd(update.message.text[1:])
        update.message.reply_text(f"```\n{out}\n```", parse_mode="Markdown")

# ================= MAIN =================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addadmin", add_admin))
    dp.add_handler(CommandHandler("deladmin", del_admin))
    dp.add_handler(CommandHandler("listadmin", list_admin))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, shell_cmd))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
