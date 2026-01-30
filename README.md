# 🤖 telegrambotnyil  
**Telegram Remote Control Bot**

Bot Telegram untuk **remote server / VPS / Linux device**  
Dilengkapi sistem **akses admin**, **approval user**, **auto-install**, dan **auto-service**.  
Dirancang untuk kebutuhan **DevOps, IoT device, mini PC, VPS, dan server production**.

---

## 🚀 Fitur Utama

- 🔐 **Sistem Admin & Approval User**
- 👥 **Manajemen User Akses**
- 📡 **Monitoring Server**
- ⏱ **Uptime System**
- 🌐 **Status Koneksi Internet (nmcli)**
- 📡 **Status Port**
- ♻ **Restart Service**
- 🧹 **Clear Cache System**
- 🚀 **Test Bandwidth / Speedtest**
- 🛠 **Remote Solve Device**
- 🔁 **Auto Restart Service**
- 🔄 **Auto Run Saat Boot**
- 📄 **Logging System**
- 🛡 **Aman & Production Ready**

---

## 🧠 Konsep Sistem

- Telegram sebagai **Remote Control Panel**
- Sistem akses:
  - Admin
  - User approval
- Berjalan sebagai **Linux service (systemd)**
- Auto-start saat boot
- Auto-restart saat crash
- Logging semua aktivitas
- Modular & scalable
- Production architecture

---

## 🗑 Hapus Bot Lama (WAJIB jika sudah pernah install)

### Mode Normal
```bash
wget https://raw.githubusercontent.com/BlackDragon100IDN/telegrambotnyil/main/remove-telegram-bot.sh
chmod +x remove-telegram-bot.sh
./remove-telegram-bot.sh
```

### Mode Sekali Jalan (One-Line Command)
```bash
wget -q https://raw.githubusercontent.com/BlackDragon100IDN/telegrambotnyil/main/remove-telegram-bot.sh && chmod +x remove-telegram-bot.sh && ./remove-telegram-bot.sh
```

---


## ⚡ Instalasi Otomatis (1 Command Install)

Copy & paste ke terminal:

```bash
wget https://raw.githubusercontent.com/BlackDragon100IDN/telegrambotnyil/main/auto-install.sh
chmod +x auto-install.sh
sudo ./auto-install.sh
```

****
---

## 📁 Struktur Project

```bash
telegrambotnyil/
├── auto-install.sh
├── remove-telegram-bot.sh
├── bot.py
├── config.env
├── service/
│   └── telegrambot.service
├── modules/
│   ├── monitoring.py
│   ├── network.py
│   ├── system.py
│   ├── security.py
│   └── utils.py
├── logs/
│   └── bot.log
└── README.md
```

---

## ⚙ System Requirements

**OS:**
- Debian
- Ubuntu
- Linux Server
- VPS Linux
- Mini PC Linux

**Software:**
- Python `>= 3.8`
- systemd
- network-manager (nmcli)

**Package:**
- python3
- python3-pip
- curl
- wget
- git
- speedtest-cli

---

## 🔄 Service Management

```bash
systemctl status telegrambot
systemctl restart telegrambot
systemctl stop telegrambot
systemctl start telegrambot
systemctl enable telegrambot
```

---

## 📄 Logging System

```bash
tail -f /var/log/telegrambot.log
journalctl -u telegrambot -f
```

---

## 🛡 Sistem Keamanan

- Validasi Admin ID
- Sistem approval user
- Whitelist user
- Permission command control
- Isolasi service systemd
- Auto recovery service
- Logging semua aktivitas
- Proteksi akses tidak sah
- Security hardening

---

## 📡 Contoh Command Bot

- `/status` → status server  
- `/uptime` → uptime system  
- `/net` → status jaringan  
- `/ports` → cek port aktif  
- `/restart` → restart service  
- `/clear` → clear cache  
- `/speedtest` → test bandwidth  
- `/reboot` → reboot server  
- `/shutdown` → shutdown server  
- `/logs` → lihat log  
- `/approve` → approve user  
- `/ban` → block user  

---

## 📌 Roadmap

- 🌍 Web dashboard
- 📊 Resource monitoring graph
- 🤖 AI anomaly detection
- 🔐 Role-based access control
- 📱 Multi-device support
- 📦 Plugin system
- 🔑 Encrypted config
- 🧩 Modular API
- 🛡 Security hardening
- 📡 Cloud integration

---

## 👨‍💻 Author

**BlackDragon100IDN**  
Telegram Bot Engineer  
Linux Automation • VPS Security • IoT Integration • DevOps System

---

## ⭐ Support Project

Jika project ini membantu kamu:

- ⭐ Star repository  
- 🍴 Fork project  
- 🤝 Contribute pull request  
- 💬 Share ke komunitas Linux / DevOps / IoT  
- 🧠 Gunakan untuk production system  

---

> 🤖 **telegrambotnyil**  
> *Control your server from Telegram — secure, automated, and production ready.*
