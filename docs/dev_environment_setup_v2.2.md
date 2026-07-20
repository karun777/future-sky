# dev_environment_setup.md – Version 2.2

# Future Sky Developer Environment Setup

## Server Information
- **Server IP:** `165.228.222.120`
- **SSH User:** `karun777`

---

## Core Directories
- **Bot Directory:**  
`/home/karun777/futuresky/bot`

- **Python Virtual Environment:**  
`/home/karun777/futuresky/discord-bot-env`

- **Bot Script Path:**  
`/home/karun777/futuresky/bot/run_bot.py`  
*(Note: The production bot script is referred to by systemd as `bot.py` but is based on the local `run_bot.py` file from Mac.)*

- **Local Development Path (MacOS):**  
/Users/karun777/Documents/GitHub/FutureSky/future-sky-canon/
├── bot/
│   ├── run_bot.py
│   ├── __init__.py
│   └── ...
├── data/
│   ├── rooms/
│   │   └── rooms.json
│   ├── enemies/
│   │   └── enemies.json
│   ├── characters/
│   │   └── characters.json
│   └── global_ambient.json
├── docs/
│   ├── developer_codex_V1.1.md
│   ├── RedBook_V7.2.md
│   ├── future_sky_bikerack.md
│   ├── chakra_combat_mechanics.md
│   └── dev_environment_setup.md
├── media/
│   └── images/
│       └── ...
└── ...
---

## Systemd Service

- **Service Name:**  
`futuresky-bot.service`

- **Service File Path:**  
`/etc/systemd/system/futuresky-bot.service`

### Sample Service Definition
```ini
[Unit]
Description=Future Sky Discord Bot
After=network.target

[Service]
Type=simple
User=karun777
WorkingDirectory=/home/karun777/futuresky/bot
ExecStart=/home/karun777/futuresky/discord-bot-env/bin/python3 /home/karun777/futuresky/bot/run_bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

---

## Deployment Steps

### 1. **Update the bot code**
From Mac to server:
```bash
scp /Users/karun777/Documents/GitHub/FutureSky/future-sky-canon/bot/run_bot.py karun777@165.228.222.120:/home/karun777/futuresky/bot/run_bot.py
```

### 2. **Reload & Restart Bot Service**
```bash
sudo systemctl daemon-reload
sudo systemctl restart futuresky-bot.service
sudo systemctl status futuresky-bot.service
```

### 3. **View Live Logs**
```bash
sudo journalctl -u futuresky-bot.service -f
```

---

## Logs Management
- View logs since 1 hour ago:
```bash
sudo journalctl -u futuresky-bot.service --since "1 hour ago"
```

- Clear logs older than 2 days:
```bash
sudo journalctl --vacuum-time=2d
```

---

## Version Control
- **Canonical GitHub Repository:**  
https://github.com/karun777/future-sky

*(Ensure local repo stays in sync with server files post-deployment.)*

---

_This document is a living file. Update as needed when directory structures, services, or workflows change._



### 🛰️ Server Deployment Structure (Debian)

**Location:**  
`/home/karun777/futuresky/`

**Directory Layout:**
```
/home/karun777/futuresky/
├── bot
│   ├── run_bot.py
│   └── __pycache__
├── codex-worker
│   ├── codex
│   │   ├── RedBook_V7.2.md
│   │   └── developer_codex_V1.1.md
│   ├── directory_structure.txt
│   ├── generate_section.py
│   ├── logs
│   │   └── session_log.txt
│   ├── output
│   │   └── section_3.md
│   ├── prompts
│   │   └── section_3.txt
│   └── redbook-extract.txt
├── data
│   ├── characters
│   │   └── characters.json
│   ├── enemies
│   │   └── enemies.json
│   ├── global_ambient.json
│   └── rooms
│       └── rooms.json
├── discord-bot-env
│   ├── bin
│   ├── include
│   ├── lib
│   └── pyvenv.cfg
└── docs
    ├── RedBook_V7.2.md
    ├── chakra_combat_mechanics.md
    ├── developer_codex_V1.1.md
    ├── dev_environment_setup_v2.1.md
    └── future_sky_bikerack.md
```


### 📁 Codex Worker Node

**Location:**  
`~/codex-worker/`

**Purpose:**  
Handles autonomous rewrite, analysis, and output of Developer Codex sections using OpenAI API + Red Book v7.2 as reference.

**Directory Structure:**
```
~/codex-worker/
├── generate_section.py           ← Rewrite script (interactive)
├── .env                          ← API key required
├── prompts/                      ← Contains 17 prompt files
├── output/                       ← Stores regenerated Markdown output
├── logs/                         ← Appends session history
└── codex/
    ├── developer_codex_V1.1.md   ← Canonical source input
    └── red_book_v7.2.md          ← Contextual reference file
```

**Manual Usage:**
```bash
cd ~/codex-worker
python3 generate_section.py
```

**Prompt file format:**
Each file should be named `section_X_name.txt` matching the desired output name.

> Future development may include systemd integration for autonomous background operation or webhook triggers.
