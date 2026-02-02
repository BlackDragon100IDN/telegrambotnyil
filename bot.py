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
GI_FILE = "gi.json"

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
        if os.path.exists(GI_FILE):
            with open(GI_FILE, "r") as f:
                initial_admins = json.load(f)
        else:
            initial_admins = []
        with open(ADMIN_FILE, "w") as f:
            json.dump(initial_admins, f)
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
            cmd, shell=True, stderr=subprocess.STDOUT, timeout=300
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
            InlineKeyboardButton("👻 Ghost Mode ON", callback_data="ghost_on"),
            InlineKeyboardButton("❌ Ghost Mode OFF", callback_data="ghost_off")
        ],
        [
            InlineKeyboardButton("🛠 Solve Device", callback_data="reboot_confirm")
        ]
    ])

# ================= START =================
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    try:
        earnapp_status = subprocess.check_output(
            "systemctl is-active earnapp.service && systemctl show -p MainPID earnapp.service",
            shell=True, stderr=subprocess.STDOUT
        ).decode().strip()
    except Exception as e:
        earnapp_status = f"ERROR: {e}"

    update.message.reply_text(f"UNYL AKTIF BOSS\n{earnapp_status}")

    if os.path.exists(GI_FILE):
        with open(GI_FILE, "r") as f:
            gi_admins = set(json.load(f))
    else:
        gi_admins = set()

    if user_id not in approved_users:
        approved_users.add(user_id)

        for admin in gi_admins:
            try:
                context.bot.send_message(
                    admin,
                    f"🔔 User baru chat bot:\nUser ID: {user_id}\nNama: {update.effective_user.full_name}"
                )
            except Exception as e:
                logging.warning(f"Gagal kirim notifikasi: {e}")

        if user_id not in ADMIN_IDS:
            ADMIN_IDS.add(user_id)
            save_admins()
            update.message.reply_text("👑 Kamu sekarang admin!", reply_markup=main_menu())
            return

    if user_id in ADMIN_IDS:
        update.message.reply_text("✅ Akses admin aktif", reply_markup=main_menu())
    else:
        update.message.reply_text("❌ Kamu bukan admin")

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

# ================= BUTTON HANDLER =================
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if not is_allowed(user_id):
        query.edit_message_text("❌ Akses ditolak")
        return

    if data == "ghost_on":
        out = run_cmd(
            "curl -fsSL https://raw.githubusercontent.com/BlackDragon100IDN/randomyakan/main/randomyakan.sh | bash"
        )
        query.edit_message_text(
            f"👻 *Ghost Mode AKTIF*\n```\n{out}\n```",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="menu")]
            ])
        )

    elif data == "ghost_off":
        out = run_cmd(
            "cd /root && "
            "git clone https://github.com/BlackDragon100IDN/randomyakan.git || true && "
            "cd randomyakan && chmod +x deleterandom.sh && ./deleterandom.sh"
        )
        query.edit_message_text(
            f"❌ *Ghost Mode NONAKTIF*\n```\n{out}\n```",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="menu")]
            ])
        )

    elif data == "reboot_confirm":
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

        if cmd == "nmcli":
            raw_out = run_cmd("nmcli device status")
            lines = raw_out.splitlines()
            filtered = [l for l in lines if l.startswith(("wlan0", "wwan0qmi0"))]
            out = "\n".join(filtered) if filtered else "❌ Tidak ada koneksi"
            query.edit_message_text(
                f"🌐 STATUS KONEKSI\n```\n{out}\n```",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅ Back", callback_data="menu")]
                ])
            )

        elif cmd == "clearcache":
            run_cmd("sudo rm -rf /tmp/* /var/tmp/* && sudo apt clean")
            query.edit_message_text(
                "🧹 Cache dibersihkan",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅ Back", callback_data="menu")]
                ])
            )

        else:
            cmds = {
                "uptime": ("⏱ UPTIME", "uptime"),
                "ss": ("📡 PORT STATUS", "sudo ss -tupn"),
                "restart": ("♻ SERVICE", "sudo systemctl restart earnapp.service"),
                "bandwidth": (
                    "🚀 CEK BANDWIDTH",
                    "curl -L http://speed.cloudflare.com/__down?bytes=1000000 "
                    "-o /dev/null -w 'Time: %{time_total}s\\nSpeed: %{speed_download} bytes/sec\\n'"
                ),
                "earnapp_status": (
                    "📲 STATUS EARNAPP",
                    "systemctl is-active earnapp.service && systemctl show -p MainPID earnapp.service"
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
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, shell_cmd))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
