# Future Sky – DEV_ENVIRONMENT_SETUP v5.0

## Last Updated
2026-07-01

---

# Purpose

This document defines the canonical operational environment for Future Sky.

It answers three questions:

1. Where does Future Sky live?
2. How is it developed?
3. How is it operated?

This document describes stable architecture and operational practice rather than current priorities.

Related documents:

- DEV_STATE.md — Current operational truth
- CHANGELOG.md — Historical evolution
- TRAJECTORY.md — Strategic direction
- NEPTUNE_LOUNGE_SERVER_STATE.md — Infrastructure snapshot
- FUTURE_SKY_OPERATIONS.md *(planned)* — Operational runbook

---

# Guiding Principles

Future Sky currently optimises for:

- Clarity
- Recoverability
- Iteration speed
- Operational stability
- Single-developer comprehensibility

When uncertain, choose the solution that future-you can understand after months away from the project.

---

# Canonical Environment

## Development Workstation

**Canonical:** Windows 11

Responsibilities:

- Source editing
- Git
- Deployment
- Documentation
- SSH administration

The MacBook Pro is currently unavailable and is **not** part of the canonical operating environment.

## Runtime Node

**Hostname:** Neptune Lounge

Purpose:

- Canonical Future Sky runtime
- Public web node
- Discord bot host
- Database host
- Operational infrastructure

---

# Infrastructure

## Network

- NBN FTTP
- Telstra Smart Modem 4
- Reserved LAN IP: 192.168.0.148

## Public Services

- HTTPS: future-sky.net
- nginx
- Let's Encrypt
- SSH on TCP 777

## Security

- SSH public-key authentication
- Password authentication disabled
- UFW enabled
- Fail2Ban enabled

## Boot Profile

Default target:

    multi-user.target

Console-first operation.

---

# Runtime Architecture

Primary interface:

Discord

Core runtime:

- fsbot/
- bot/run_bot.py

Supporting services:

- PostgreSQL
- Redis
- Lavalink
- nginx

Gameplay persistence authority remains JSON.

---

# Website Architecture

Canonical domain:

https://future-sky.net

Current onboarding spine:

Physical Discovery
↓
Website
↓
Discord
↓
Future Sky

Primary assets:

- index.html
- signal.html
- chamber.html
- love.html
- feed7.html

---

# Deployment Workflow

Windows
↓
Edit
↓
Validate
↓
Deploy
↓
Restart service
↓
Verify
↓
Commit

Typical deployment:

```powershell
scp -P 777 filename.html karun777@future-sky.net:~
```

Then on Neptune Lounge:

```bash
sudo mv ~/filename.html /var/www/html/
sudo systemctl reload nginx
```

---

# Operational Validation

Healthy node checklist:

- SSH reachable on 777
- nginx running
- PostgreSQL running
- Redis running
- Future Sky bot running
- Lavalink running
- Fail2Ban running
- Zero failed systemd units

Useful commands:

```bash
systemctl --failed
systemctl status futuresky-bot
systemctl status nginx
systemctl status fail2ban
```

---

# Data Authority

During runtime:

Memory

On save:

JSON

Future:

PostgreSQL may become authoritative only when gameplay requirements justify migration.

---

# Recovery Order

1. Source repository
2. Runtime JSON
3. Website assets
4. PostgreSQL
5. Documentation

---

# Documentation Philosophy

Every canonical document should answer a single question.

- DEV_STATE — What is true?
- DEV_ENVIRONMENT_SETUP — How does the system operate?
- CHANGELOG — What changed?
- TRAJECTORY — Where are we going?
- SERVER_STATE — What is the infrastructure state?

---

# Closing Observation

Future Sky is no longer simply a software project.

It is an operational platform.

Development now occurs against a stable, documented, Internet-facing node.

The objective is not merely to build new systems.

The objective is to evolve a world that remains understandable, recoverable and operable over time.
