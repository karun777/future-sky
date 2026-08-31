# NEPTUNE_LOUNGE_V2_COMMISSIONING.md

**Status:** Draft v0.1\
**Purpose:** Commission a clean 64-bit Neptune Lounge while preserving
every meaningful part of Future Sky.

------------------------------------------------------------------------

# Mission

This is **not** an upgrade.

It is a controlled commissioning of **Neptune Lounge v2**.

The objective is:

-   preserve everything meaningful
-   remove accidental complexity
-   establish a reproducible server
-   validate every restored service
-   retain the existing server until the new one is proven

------------------------------------------------------------------------

# Governing Principles

1.  Never destroy before a verified backup exists.
2.  Archive before deleting.
3.  Every service must justify its existence.
4.  Prefer rebuilding over repairing.
5.  Secrets are restored separately from documentation.
6.  Every completed step is checked off before continuing.

------------------------------------------------------------------------

# Phase 0 --- Discovery ✅

-   [x] OS identified
-   [x] 32-bit Debian confirmed
-   [x] Hardware confirmed 64-bit capable
-   [x] Core services inventoried
-   [x] Data footprint measured
-   [x] Future Sky project structure reviewed
-   [x] Migration strategy agreed

------------------------------------------------------------------------

# Phase 1 --- Capture

## Inventory

-   [ ] Package inventory
-   [ ] Enabled services
-   [ ] Custom systemd services
-   [ ] Network configuration
-   [ ] Firewall rules
-   [ ] SSH configuration
-   [ ] nginx configuration
-   [ ] PostgreSQL inventory
-   [ ] Redis inventory
-   [ ] Directory inventory
-   [ ] Installed Python environments

## Backup

-   [ ] Future Sky source
-   [ ] Future Sky data
-   [ ] Assets
-   [ ] Website
-   [ ] Documentation
-   [ ] nginx
-   [ ] systemd
-   [ ] SSH
-   [ ] UFW
-   [ ] Fail2Ban
-   [ ] PostgreSQL dump
-   [ ] Redis archive (if required)
-   [ ] Secrets exported to secure location

## Verification

-   [ ] Backup readable
-   [ ] Checksums created
-   [ ] Backup copied off-server
-   [ ] Selective restore tested

------------------------------------------------------------------------

# Phase 2 --- Redundancy Audit

  Component                 Decision                   Notes
  ------------------------- -------------------------- -------------------------
  Future Sky Bot            Keep                       Runtime authority
  nginx                     Keep                       Public web
  SSH                       Keep                       Administration
  PostgreSQL                Archive                    Redesign later
  Redis                     Archive unless justified   No current authority
  Lavalink                  Review                     Confirm dependency
  Codex Worker              Archive                    Revisit as world daemon
  Legacy systemd services   Archive                    Historical reference

------------------------------------------------------------------------

# Phase 3 --- Fresh Build

## Base

-   [ ] Debian amd64
-   [ ] Updates
-   [ ] SSH
-   [ ] Firewall
-   [ ] Fail2Ban
-   [ ] Time sync

## Runtime

-   [ ] Python
-   [ ] Virtual environment
-   [ ] Future Sky
-   [ ] nginx
-   [ ] HTTPS
-   [ ] Discord bot

## Optional

-   [ ] PostgreSQL
-   [ ] Lavalink
-   [ ] Redis
-   [ ] MBBSEmu

------------------------------------------------------------------------

# Phase 4 --- Validation

## Infrastructure

-   [ ] SSH
-   [ ] HTTPS
-   [ ] DNS
-   [ ] Automatic boot

## Future Sky

-   [ ] Bot starts
-   [ ] Character loads
-   [ ] Navigation works
-   [ ] Thread nodes trigger
-   [ ] Presence updates
-   [ ] World clock advances
-   [ ] Assets resolve

## Recovery

-   [ ] Backup runs
-   [ ] Restore procedure validated

## MajorMUD

-   [ ] MBBSEmu installed
-   [ ] MajorMUD loads
-   [ ] Telnet connection successful

------------------------------------------------------------------------

# Commissioning Complete

Neptune Lounge v2 is commissioned only when:

-   the new server has passed every validation item,
-   backups are verified,
-   documentation matches reality,
-   and the original server is no longer required as the recovery
    position.

------------------------------------------------------------------------

# Notes

The discovery that Neptune Lounge was installed as a 32-bit Debian
system was not a setback.

It revealed the right moment to establish a durable operational
foundation before Future Sky accumulates years of infrastructure.

The goal is not merely a new server.

The goal is a server that can always be rebuilt with confidence.
