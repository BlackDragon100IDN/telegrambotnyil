#!/bin/bash

set -e

echo "======================================"
echo " Telegram Remote Bot - Auto Installer "
echo "======================================"

REPO_URL="https://github.com/BlackDragon100IDN/telegrambotnyil.git"
BOT_DIR="/root/telegrambotnyil"
VENV_DIR="/root/tgbot"
BOT_FILE="bot.py"
SERVICE_NAME="telegram-remote"

# ===== INPUT TOKEN =====
read -p "Masukkan TOKEN Bot Telegram: " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
  echo "❌ Token tidak boleh kosong!"
  exit 1
fi
echo "✅ Token diterima"

# ===== INSTALL SYSTEM PACKAGE =====
apt update -y
apt install -y git python3 python3-full python3-venv sudo curl

# ===== CLONE REPO =====
if [ -d "$BOT_DIR" ]; then
  echo "📁 Repo sudah ada, skip clone"
else
  git clone $REPO_URL $BOT_DIR
fi

# ===== CREATE VENV =====
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# ===== INSTALL PY LIB =====
pip install --upgrade pip
pip install python-telegram-bot==13.15

# ===== SET TOKEN =====
sed -i "s|^TOKEN = .*|TOKEN = \"$BOT_TOKEN\"|g" $BOT_DIR/$BOT_FILE

# ===== SUDO NOPASSWD =====
USERNAME=$(whoami)
if ! grep -q "$USERNAME ALL=(ALL) NOPASSWD: /sbin/shutdown" /etc/sudoers; then
  echo "$USERNAME ALL=(ALL) NOPASSWD: /sbin/shutdown" >> /etc/sudoers
fi

# ===== SYSTEMD SERVICE =====
cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=Telegram Linux Remote
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
ExecStart=${VENV_DIR}/bin/python ${BOT_DIR}/${BOT_FILE}
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo "======================================"
echo " INSTALL SELESAI"
echo " Bot aktif & autorun boot"
echo "======================================"
