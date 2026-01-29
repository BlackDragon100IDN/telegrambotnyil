#!/bin/bash

echo "=============================="
echo " TELEGRAM BOT FULL REMOVER "
echo "=============================="

systemctl stop telegram-remote 2>/dev/null
systemctl disable telegram-remote 2>/dev/null

rm -f /etc/systemd/system/telegram-remote.service
rm -f /etc/systemd/system/telegram_remote.service
systemctl daemon-reload
systemctl reset-failed

rm -f /root/telegram_remote.py
rm -rf /root/telegrambotnyil
rm -rf /root/tgbot

rm -rf /root/.cache/pip
rm -rf /root/.local/share/virtualenv
rm -rf /root/.config/pip
rm -rf /root/.virtualenvs

find /root -iname "*telegram*" -exec rm -rf {} \; 2>/dev/null
find /etc -iname "*telegram*" -exec rm -rf {} \; 2>/dev/null

systemctl daemon-reexec

echo "=============================="
echo " ✅ BOT TELEGRAM TERHAPUS TOTAL"
echo "=============================="
echo " SYSTEM CLEAN MODE READY"
echo "=============================="
