# Future Sky – OPERATIONS v1.0

## Last Updated
2026-07-01

---

# Purpose

This document is the operational runbook for Future Sky.

It answers one question:

> "What do I do to keep the world alive?"

Unlike DEV_ENVIRONMENT_SETUP, this document focuses on day-to-day operation rather than architecture.

---

# Operational Node

Canonical Runtime Node:

**Neptune Lounge**

Role:

- Public website
- Discord bot
- PostgreSQL
- Redis
- Lavalink
- Future Sky runtime

---

# Daily Health Check

Run:

```bash
systemctl --failed
```

Expected:

```text
0 loaded units listed.
```

Verify core services:

```bash
systemctl status nginx --no-pager
systemctl status futuresky-bot --no-pager
systemctl status fail2ban --no-pager
systemctl status postgresql --no-pager
systemctl status lavalink --no-pager
```

---

# Public Verification

Verify externally:

- https://future-sky.net
- Discord bot responds
- SSH on port 777

---

# Deployment Checklist

1. Edit locally on Windows.
2. Validate JSON.
3. Commit to Git (recommended).
4. Deploy changed files.
5. Restart affected service.
6. Verify runtime.
7. Confirm website or bot behaviour.

---

# Website Deployment

Upload:

```powershell
scp -P 777 filename.html karun777@future-sky.net:~
```

Install:

```bash
sudo mv ~/filename.html /var/www/html/
sudo systemctl reload nginx
```

Validate:

```bash
curl -I https://localhost -k
```

---

# Bot Operations

Status:

```bash
systemctl status futuresky-bot
```

Restart:

```bash
sudo systemctl restart futuresky-bot
```

Logs:

```bash
journalctl -u futuresky-bot -n 100 --no-pager
```

---

# Security

Current posture:

- SSH keys only
- Password authentication disabled
- SSH on TCP 777
- UFW enabled
- Fail2Ban enabled

Never expose additional services without documenting the change.

---

# Backups (Target State)

Maintain backups of:

- Source repository
- Runtime JSON
- Website assets
- nginx configuration
- systemd service files
- PostgreSQL dumps
- SSL configuration

---

# Recovery Priorities

1. Restore server connectivity.
2. Restore SSH access.
3. Restore nginx.
4. Restore Future Sky bot.
5. Restore gameplay JSON.
6. Restore database services.
7. Validate public website.
8. Validate Discord.

---

# Infrastructure Change Log

Record changes whenever any of the following occur:

- DNS changes
- Router changes
- Firewall changes
- SSL renewal issues
- Service additions
- Port changes
- Operating system upgrades

---

# Operational Philosophy

Neptune Lounge is no longer simply a development machine.

It is the canonical operational Future Sky node.

Every infrastructure change should be:

- documented,
- repeatable,
- recoverable,
- validated after reboot.

The goal is not merely uptime.

The goal is confidence that the world can always be restored.
