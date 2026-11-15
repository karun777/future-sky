#!/usr/bin/env python3
"""Check this fictional design fixture; these are not live access-control tests."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parent / "fixtures/pod_console_workspace.v0.1.json"

def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def validate(data: dict) -> None:
    need(data.get("schema_version") == 1, "Unsupported version")
    need(data.get("realm") == "future_sky_fiction", "Wrong realm")
    need(data.get("status") == "authoring_fixture_not_live", "Not an authoring fixture")
    need(data.get("source_kind") == "synthetic_authored_data", "Only authored synthetic data")
    need(data["workspace"]["account_holder"] is None, "Unresolved account holder was invented")
    need(data["workspace"]["previous_user"] is None, "Unresolved previous user was invented")
    console = data["console"]
    need(console["true_owner"] is None, "Ownership is not established")
    need(console["character_belief"]["truth_status"] == "assumption_not_confirmed", "Belief promoted to fact")
    need(console["session"]["credential_value"] is None, "Do not store a credential")
    need(console["ownership_transfer"] is False and console["inventory_grant"] is False, "Discovery cannot transfer title or grant inventory")
    expected_boundaries = {"production_load_allowed", "private_data_import_allowed", "runtime_mutations_allowed", "real_world_credential_present", "automatic_obligation_inheritance", "automatic_currency_credit", "automatic_role_assignment", "new_locations_created"}
    need(set(data["boundaries"]) == expected_boundaries, "Missing boundary declarations")
    need(all(v is False for v in data["boundaries"].values()), "Fixture boundary broadened")
    panels = {p["id"] for p in data["panels"]}
    ids = set()
    for record in data["records"]:
        rid = record["id"]
        need(bool(re.fullmatch(r"FS-DEMO-RECORD-[0-9]{3}", rid)), "Non-demo record ID")
        need(rid not in ids, "Duplicate record")
        ids.add(rid)
        need(record["panel"] in panels, "Unknown panel")
        need(record["accepted_by_character"] is False, "Display cannot accept a commitment")
        if record["kind"] == "historical_balance_claim":
            need(record["spendable"] is False, "Archived claim cannot become funds")
        if record["kind"] == "unconditional_offer":
            need(record["reciprocal_obligation"] is False, "Gift cannot create repayment")
        if record["kind"] == "invitation":
            need(record["authority_granted"] is False, "Invitation cannot appoint a role")
        if record["kind"] == "legacy_note":
            need(record["obligation_assigned"] is False, "Old task cannot assign an obligation")
    need(len(ids) == 7, "Review the seven-record sample explicitly before changing it")

def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    validate(data)
    mutations = [
        lambda d: d.update(realm="real_world"),
        lambda d: d["console"].update(true_owner="Efiishent"),
        lambda d: d["console"]["session"].update(credential_value="TEST-ONLY"),
        lambda d: d["records"][4].update(spendable=True),
        lambda d: d["records"][5].update(reciprocal_obligation=True),
        lambda d: d["records"][1].update(authority_granted=True),
        lambda d: d["records"][2].update(obligation_assigned=True),
        lambda d: d["boundaries"].update(production_load_allowed=True),
        lambda d: d["records"][0].update(accepted_by_character=True),
        lambda d: d["records"][1].update(id=d["records"][0]["id"]),
    ]
    for mutate in mutations:
        candidate = copy.deepcopy(data)
        mutate(candidate)
        try:
            validate(candidate)
        except ValueError:
            continue
        raise AssertionError("Invalid fixture mutation accepted")
    print(f"PASS: seven fictional records; valid fixture plus {len(mutations)} rejected variants")
    print("Scope: fixture consistency only; no runtime privacy, UI, gameplay or authentication test.")

if __name__ == "__main__":
    main()
