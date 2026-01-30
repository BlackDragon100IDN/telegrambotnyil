#!/bin/bash
set -e

echo "=== TELEGRAMBOTNYIL AUTO INSTALLER ==="

# Update sistem dan install dependencies
apt update
apt install -y python3 python3-venv python3-pip git curl sudo

# Buat virtual environment
mkdir -p /root/tgbot
python3 -m venv /root/tgbot

# Aktifkan virtualenv dan install library
source /root/tgbot/bin/activate
pip install --upgrade pip
pip install python-telegram-bot==13.15

# Clone repository bot
cd /root
git clone https://github.com/BlackDragon100IDN/telegrambotnyil.git
cd telegrambotnyil

# Minta token Telegram dari user
read -p "Masukkan TOKEN Telegram Bot: " TELEGRAM_TOKEN

# Simpan token ke file token.txt (bot.py akan membacanya)
echo "$TELEGRAM_TOKEN" > token.txt

# Buat file admins.json default
if [ ! -f admins.json ]; then
    echo '["8599557076"]' > admins.json
fi

# Beri hak eksekusi bot.py
chmod +x bot.py

# Pasang service systemd
cp telegrambotnyil.service /etc/systemd/system/telegram-remote.service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable telegram-remote
systemctl restart telegram-remote

echo "======================================"
echo " INSTALL SELESAI "
echo " Bot aktif dan auto-run saat boot "
echo "======================================"
