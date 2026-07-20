# ============================================================
# FILE META — fsbot/scenarios.py
# Canonical name: ScenarioService (runtime scenario authority)
#
# Version: v0.2.0 — Feather 1.5: Living Scenario State
# Last edited: 2026-07-17 (Australia/Perth)
#
# Authority:
# - AUTHORITATIVE for active runtime scenario instances
# - AUTHORITATIVE for scenario variables, flags, history, notes, and completion
# - NOT authoritative for movement, rooms, combat, rendering, or persistence
#
# Feather 1.5 scope:
# - In-memory only
# - Future Sky world-time timestamps
# - Variables, flags, factual history, and authored notes
# - One hard-coded proof scenario: portal_run
# ============================================================

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


ScenarioInstance = Dict[str, Any]
WorldTimeProvider = Callable[[], int]


class ScenarioService:
    """Runtime authority for active scenario instances.

    The service stores journey state, but does not interpret arbitrary variables
    or flags. Scenario rules and EventBus bridges decide what those values mean.
    """

    PORTAL_RUN_ID = "portal_run"
    PORTAL_RUN_ROUTE = (
        "neptune_lounge",
        "main_square",
        "efiishents_office",
    )

    def __init__(
        self,
        *,
        world_time_provider: WorldTimeProvider,
        logger: logging.Logger | None = None,
    ):
        if not callable(world_time_provider):
            raise TypeError("world_time_provider must be callable")

        self.log = logger or logging.getLogger("futuresky.scenarios")
        self._world_time_provider = world_time_provider
        self._active_by_player: Dict[str, List[ScenarioInstance]] = {}
        self._completed_by_player: Dict[str, List[ScenarioInstance]] = {}

    # --------------------------------------------------
    # Lifecycle API
    # --------------------------------------------------

    def start(
        self,
        player_id: str,
        scenario_id: str,
        *,
        chapter_id: str = "orientation",
        variables: Optional[Dict[str, Any]] = None,
        flags: Optional[List[str]] = None,
        note: Optional[str] = None,
    ) -> ScenarioInstance:
        """Start a scenario for a player, or return the existing active one."""
        uid = str(player_id)
        sid = self._normalise_id(scenario_id, "scenario_id")

        existing = self.get_active(uid, sid)
        if existing is not None:
            return existing

        now = self._world_time()
        instance: ScenarioInstance = {
            "instance_id": f"scn_{uuid4().hex}",
            "scenario_id": sid,
            "chapter_id": str(chapter_id or "orientation"),
            "player_id": uid,
            "status": "active",
            "step_index": 0,
            "step_id": self._initial_step_id(sid),
            "variables": deepcopy(variables) if isinstance(variables, dict) else {},
            # Lists are intentionally used instead of Python sets so the shape is
            # already safe for future JSON persistence.
            "flags": self._normalise_flags(flags or []),
            "history": [],
            "notes": [],
            "started_at_world": now,
            "updated_at_world": now,
            "completed_at_world": None,
        }

        self._active_by_player.setdefault(uid, []).append(instance)
        self._append_history_ref(
            instance,
            event_type="scenario.started",
            details={"step_id": instance["step_id"]},
        )
        if note:
            self._append_note_ref(instance, note)

        self.log.info(
            "[SCENARIO] started player=%s scenario=%s chapter=%s step=%s world_time=%s",
            uid,
            sid,
            instance["chapter_id"],
            instance["step_id"],
            now,
        )
        return deepcopy(instance)

    def advance(
        self,
        player_id: str,
        scenario_id: str,
        *,
        step_id: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        history_event: Optional[str] = None,
        history_details: Optional[Dict[str, Any]] = None,
        note: Optional[str] = None,
    ) -> Optional[ScenarioInstance]:
        """Advance an active scenario by one step or to an explicit step."""
        uid = str(player_id)
        sid = self._normalise_id(scenario_id, "scenario_id")
        instance = self._get_active_ref(uid, sid)
        if instance is None:
            return None

        previous_step = str(instance.get("step_id") or "")
        self._merge_variables_ref(instance, variables)

        if step_id is None:
            instance["step_index"] = int(instance.get("step_index", 0)) + 1
            instance["step_id"] = self._step_id_for_index(
                sid,
                int(instance["step_index"]),
            )
        else:
            explicit = str(step_id).strip()
            if not explicit:
                raise ValueError("step_id must not be empty")
            instance["step_id"] = explicit

        instance["updated_at_world"] = self._world_time()
        self._append_history_ref(
            instance,
            event_type=history_event or "scenario.advanced",
            details={
                "from_step_id": previous_step,
                "to_step_id": instance.get("step_id"),
                **deepcopy(history_details or {}),
            },
        )
        if note:
            self._append_note_ref(instance, note)

        self.log.info(
            "[SCENARIO] advanced player=%s scenario=%s step=%s index=%s world_time=%s",
            uid,
            sid,
            instance.get("step_id"),
            instance.get("step_index"),
            instance.get("updated_at_world"),
        )
        return deepcopy(instance)

    def complete(
        self,
        player_id: str,
        scenario_id: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        history_event: str = "scenario.completed",
        history_details: Optional[Dict[str, Any]] = None,
        note: Optional[str] = None,
    ) -> Optional[ScenarioInstance]:
        """Complete and archive an active scenario instance in memory."""
        uid = str(player_id)
        sid = self._normalise_id(scenario_id, "scenario_id")
        active = self._active_by_player.get(uid, [])

        for index, instance in enumerate(active):
            if instance.get("scenario_id") != sid:
                continue

            self._merge_variables_ref(instance, variables)
            now = self._world_time()
            instance["status"] = "completed"
            instance["step_id"] = "complete"
            instance["updated_at_world"] = now
            instance["completed_at_world"] = now
            self._append_history_ref(
                instance,
                event_type=history_event,
                details=deepcopy(history_details or {}),
            )
            if note:
                self._append_note_ref(instance, note)

            completed = active.pop(index)
            if not active:
                self._active_by_player.pop(uid, None)
            self._completed_by_player.setdefault(uid, []).append(completed)

            self.log.info(
                "[SCENARIO] completed player=%s scenario=%s world_time=%s",
                uid,
                sid,
                now,
            )
            return deepcopy(completed)

        return None

    def get_active(
        self,
        player_id: str,
        scenario_id: Optional[str] = None,
    ) -> Optional[ScenarioInstance] | List[ScenarioInstance]:
        """Return one active instance or all active instances for a player."""
        uid = str(player_id)
        if scenario_id is None:
            return deepcopy(self._active_by_player.get(uid, []))

        sid = self._normalise_id(scenario_id, "scenario_id")
        instance = self._get_active_ref(uid, sid)
        return deepcopy(instance) if instance is not None else None

    def get_completed(self, player_id: str) -> List[ScenarioInstance]:
        return deepcopy(self._completed_by_player.get(str(player_id), []))

    def is_active(self, player_id: str, scenario_id: str) -> bool:
        return self._get_active_ref(str(player_id), str(scenario_id)) is not None

    # --------------------------------------------------
    # Living state API
    # --------------------------------------------------

    def set_variable(
        self,
        player_id: str,
        scenario_id: str,
        key: str,
        value: Any,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        variable_key = self._normalise_key(key, "variable key")
        instance.setdefault("variables", {})[variable_key] = deepcopy(value)
        self._touch_ref(instance)
        return deepcopy(instance)

    def increment_variable(
        self,
        player_id: str,
        scenario_id: str,
        key: str,
        amount: int | float = 1,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        variable_key = self._normalise_key(key, "variable key")
        variables = instance.setdefault("variables", {})
        current = variables.get(variable_key, 0)
        if not isinstance(current, (int, float)) or isinstance(current, bool):
            raise TypeError(f"scenario variable {variable_key!r} is not numeric")
        variables[variable_key] = current + amount
        self._touch_ref(instance)
        return deepcopy(instance)

    def add_flag(
        self,
        player_id: str,
        scenario_id: str,
        flag: str,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        flag_id = self._normalise_key(flag, "flag")
        flags = instance.setdefault("flags", [])
        if flag_id not in flags:
            flags.append(flag_id)
            flags.sort()
            self._touch_ref(instance)
        return deepcopy(instance)

    def remove_flag(
        self,
        player_id: str,
        scenario_id: str,
        flag: str,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        flag_id = self._normalise_key(flag, "flag")
        flags = instance.setdefault("flags", [])
        if flag_id in flags:
            flags.remove(flag_id)
            self._touch_ref(instance)
        return deepcopy(instance)

    def has_flag(self, player_id: str, scenario_id: str, flag: str) -> bool:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return False
        flag_id = self._normalise_key(flag, "flag")
        return flag_id in instance.get("flags", [])

    def add_history(
        self,
        player_id: str,
        scenario_id: str,
        event_type: str,
        *,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        self._append_history_ref(instance, event_type=event_type, details=details)
        return deepcopy(instance)

    def add_note(
        self,
        player_id: str,
        scenario_id: str,
        text: str,
    ) -> Optional[ScenarioInstance]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None:
            return None
        self._append_note_ref(instance, text)
        return deepcopy(instance)

    # --------------------------------------------------
    # Feather proof helpers
    # --------------------------------------------------

    def expected_room(self, player_id: str, scenario_id: str) -> Optional[str]:
        instance = self._get_active_ref(str(player_id), str(scenario_id))
        if instance is None or scenario_id != self.PORTAL_RUN_ID:
            return None

        index = int(instance.get("step_index", 0))
        if 0 <= index < len(self.PORTAL_RUN_ROUTE):
            return self.PORTAL_RUN_ROUTE[index]
        return None

    def reset_player(self, player_id: str) -> None:
        uid = str(player_id)
        self._active_by_player.pop(uid, None)
        self._completed_by_player.pop(uid, None)
        self.log.info("[SCENARIO] reset player=%s", uid)

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _get_active_ref(self, player_id: str, scenario_id: str) -> Optional[ScenarioInstance]:
        for instance in self._active_by_player.get(str(player_id), []):
            if instance.get("scenario_id") == str(scenario_id):
                return instance
        return None

    def _merge_variables_ref(
        self,
        instance: ScenarioInstance,
        variables: Optional[Dict[str, Any]],
    ) -> None:
        if not variables:
            return
        current = instance.setdefault("variables", {})
        current.update(deepcopy(variables))

    def _append_history_ref(
        self,
        instance: ScenarioInstance,
        *,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        event_id = self._normalise_key(event_type, "history event type")
        now = self._world_time()
        instance.setdefault("history", []).append(
            {
                "event_type": event_id,
                "world_time": now,
                "details": deepcopy(details or {}),
            }
        )
        instance["updated_at_world"] = now

    def _append_note_ref(self, instance: ScenarioInstance, text: str) -> None:
        note = str(text or "").strip()
        if not note:
            raise ValueError("note must not be empty")
        now = self._world_time()
        instance.setdefault("notes", []).append(
            {"world_time": now, "text": note}
        )
        instance["updated_at_world"] = now

    def _touch_ref(self, instance: ScenarioInstance) -> None:
        instance["updated_at_world"] = self._world_time()

    def _world_time(self) -> int:
        value = self._world_time_provider()
        if isinstance(value, bool):
            raise TypeError("world_time_provider returned bool")
        return int(value)

    def _initial_step_id(self, scenario_id: str) -> str:
        return self._step_id_for_index(scenario_id, 0)

    def _step_id_for_index(self, scenario_id: str, index: int) -> str:
        if scenario_id == self.PORTAL_RUN_ID:
            if 0 <= index < len(self.PORTAL_RUN_ROUTE):
                return f"enter_{self.PORTAL_RUN_ROUTE[index]}"
            return "complete"
        return f"step_{index}"

    @classmethod
    def _normalise_flags(cls, flags: List[str]) -> List[str]:
        return sorted({cls._normalise_key(flag, "flag") for flag in flags})

    @staticmethod
    def _normalise_id(value: str, field_name: str) -> str:
        normalised = str(value or "").strip().lower()
        if not normalised:
            raise ValueError(f"{field_name} is required")
        return normalised

    @staticmethod
    def _normalise_key(value: str, field_name: str) -> str:
        normalised = str(value or "").strip().lower().replace(" ", "_")
        if not normalised:
            raise ValueError(f"{field_name} is required")
        return normalised
