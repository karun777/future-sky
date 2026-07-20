# ============================================================
# FILE META — fsbot/presence.py
# Canonical name: Presence (runtime presence query authority)
#
# Version: v0.2.0
# Last edited: 2026-07-17
#
# Authority:
# - AUTHORITATIVE query interface for runtime character presence
# - Answers canonical questions about which character records exist
#   and which characters currently occupy a room
#
# Purpose:
# - Centralise presence queries that were previously distributed across:
#   • GameState.get_players_in_room()
#   • direct iteration over storage.characters
# - Provide a single read boundary for Navigation, Ambient, HUD, Combat,
#   scenarios, NPC systems, and future emergent systems
#
# Source of truth:
# - Storage remains authoritative for character records
# - Character current_room remains the persisted location fact
# - GameState remains authoritative for room resolution / void rescue
# - Presence does not maintain a second mutable copy of world state
#
# Writes:
# - None
#
# Must NOT own:
# - Movement decisions or current_room mutation
# - Character persistence
# - Room persistence
# - Void rescue
# - Event publication
# - Idle timing, ambient pacing, combat, narrative, or routing
# - Presence caches until a demonstrated runtime need exists
#
# Depends on:
# - Storage
# - GameState
#
# Used by:
# - run_bot.py (runtime wiring)
# - Navigation
# - Ambient
# - HUD
# - Future combat, scenario, NPC, and social systems
#
# Design law:
# - Presence is a canonical query interface over existing truth.
# - It must not become another mutable copy of world state.
# ============================================================

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Tuple


class Presence:
    """Canonical read interface for runtime character presence.

    Presence deliberately remains thin. Character records live in Storage,
    while valid room resolution and void rescue remain GameState concerns.
    """

    def __init__(self, storage, state):
        self.storage = storage
        self.state = state

    # ---------------------------
    # Character access
    # ---------------------------

    def iter_character_records(
        self,
    ) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """Yield valid ``(user_id, character_record)`` pairs.

        Invalid or non-dict entries are ignored. This method does not call
        ``ensure_player_records`` because broad iteration must remain
        non-mutating.
        """
        characters = getattr(self.storage, "characters", {})

        if not isinstance(characters, dict):
            return

        for user_id, character in characters.items():
            if not isinstance(character, dict):
                continue
            yield str(user_id), character

    def iter_players(self) -> Iterator[Dict[str, Any]]:
        """Yield valid character records without their user IDs."""
        for _, character in self.iter_character_records():
            yield character

    def get_character(
        self,
        user_id: str,
        *,
        ensure: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Return a character record for ``user_id``.

        When ``ensure`` is true, GameState may apply its existing minimal
        character shape guarantees before the record is returned.
        """
        uid = str(user_id)

        if ensure:
            self.state.ensure_player_records(uid)

        characters = getattr(self.storage, "characters", {})
        if not isinstance(characters, dict):
            return None

        character = characters.get(uid)
        if not isinstance(character, dict):
            return None

        return character

    # ---------------------------
    # Room resolution
    # ---------------------------

    def resolve_room_for_user(self, user_id: str) -> str:
        """Return the user's canonical valid room.

        Delegates to GameState so void-rescue behaviour and persistence remain
        unchanged and retain a single authority.
        """
        return self.state.resolve_room_for_user(str(user_id))

    def get_room_id_for_character(
        self,
        user_id: str,
        character: Optional[Dict[str, Any]] = None,
        *,
        resolve: bool = False,
    ) -> Optional[str]:
        """Return a character's room ID.

        ``resolve=False`` performs a non-mutating read of ``current_room``.
        ``resolve=True`` delegates to GameState and may trigger its existing
        void-rescue repair behaviour.
        """
        uid = str(user_id)

        if resolve:
            return self.resolve_room_for_user(uid)

        record = character if isinstance(character, dict) else self.get_character(uid)
        if not isinstance(record, dict):
            return None

        room_id = record.get("current_room")
        if not isinstance(room_id, str) or not room_id:
            return None

        return room_id

    # ---------------------------
    # Presence queries
    # ---------------------------

    def get_players_in_room(
        self,
        room_id: str,
        exclude_user_id: Optional[str] = None,
        *,
        resolve: bool = False,
    ) -> List[Dict[str, Any]]:
        """Return character records currently assigned to ``room_id``.

        ``resolve=False`` compares persisted ``current_room`` values without
        mutation. ``resolve=True`` delegates each lookup to GameState and may
        perform its existing void-rescue repair behaviour.
        """
        present: List[Dict[str, Any]] = []
        excluded = str(exclude_user_id) if exclude_user_id is not None else None

        for user_id, character in self.iter_character_records():
            member_room = (
                self.resolve_room_for_user(user_id)
                if resolve
                else character.get("current_room")
            )
            if member_room != room_id:
                continue
            if excluded is not None and user_id == excluded:
                continue
            present.append(character)

        return present

    def get_room_members(
        self,
        room_id: str,
        exclude_user_id: Optional[str] = None,
        *,
        resolve: bool = False,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Return ``(user_id, character_record)`` pairs in ``room_id``.

        Set ``resolve=True`` when callers require canonical room resolution
        rather than a non-mutating persisted-room comparison.
        """
        members: List[Tuple[str, Dict[str, Any]]] = []
        excluded = str(exclude_user_id) if exclude_user_id is not None else None

        for user_id, character in self.iter_character_records():
            member_room = (
                self.resolve_room_for_user(user_id)
                if resolve
                else character.get("current_room")
            )
            if member_room != room_id:
                continue
            if excluded is not None and user_id == excluded:
                continue
            members.append((user_id, character))

        return members

    def get_user_ids_in_room(
        self,
        room_id: str,
        exclude_user_id: Optional[str] = None,
        *,
        resolve: bool = False,
    ) -> List[str]:
        """Return user IDs for characters currently assigned to ``room_id``."""
        return [
            user_id
            for user_id, _ in self.get_room_members(
                room_id,
                exclude_user_id=exclude_user_id,
                resolve=resolve,
            )
        ]

    def is_user_in_room(self, user_id: str, room_id: str) -> bool:
        """Return whether the user's persisted current_room equals ``room_id``."""
        character = self.get_character(str(user_id))
        if not isinstance(character, dict):
            return False
        return character.get("current_room") == room_id

    def count_players_in_room(
        self,
        room_id: str,
        exclude_user_id: Optional[str] = None,
        *,
        resolve: bool = False,
    ) -> int:
        """Return the number of characters currently assigned to ``room_id``."""
        return len(
            self.get_room_members(
                room_id,
                exclude_user_id=exclude_user_id,
                resolve=resolve,
            )
        )
