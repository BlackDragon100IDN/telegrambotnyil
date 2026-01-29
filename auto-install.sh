#!/bin/bash
set -e

echo "=== TELEGRAMBOTNYIL AUTO INSTALLER ==="

apt update
apt install -y python3 python3-venv python3-pip git curl sudo

mkdir -p /root/tgbot
python3 -m venv /root/tgbot

source /root/tgbot/bin/activate
pip install --upgrade pip
pip install python-telegram-bot==13.15

cd /root
git clone https://github.com/BlackDragon100IDN/telegrambotnyil.git
cd telegrambotnyil

echo '["8599557076"]' > admins.json

chmod +x bot.py

cp telegrambotnyil.service /etc/systemd/system/telegram-remote.service

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable telegram-remote
systemctl restart telegram-remote

echo "======================================"
echo " INSTALL SELESAI "
echo " Bot aktif dan auto-run saat boot "
echo "======================================"
