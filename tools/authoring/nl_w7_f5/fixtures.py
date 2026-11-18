"""Synthetic host-owned fixture. No live records or authentication are loaded."""
import json
import time

from engine.participation.desk import Binding, Desk
from engine.participation.undertakings import UndertakingStore, schema

PROFILES = {
    "maker": ("Mira Vale", "Project coordinator"),
    "reader": ("Ivo Reed", "Review steward"),
    "successor": ("Lark Fen", "Nominated successor"),
    "convenor": ("Orin Ash", "Convenor"),
    "visitor": ("Nell Moss", "Visitor"),
}


def create(path, realm, *, title="Review the lantern workshop plan",
           brief="Invite a second reader to review the plan and acknowledge its scoped copy.",
           content="The fictional workshop has three lantern stations and a shared tool table."):
    ends = int(time.time()) + 30 * 86400

    def seed(db):
        schema(db)
        db.execute("INSERT INTO collective VALUES ('circle')")
        db.executemany("INSERT INTO portal VALUES (?,'circle')", [("desk",), ("source",)])
        for actor in PROFILES:
            db.execute("INSERT INTO person VALUES (?)", (actor,))
            db.execute("INSERT INTO held_key VALUES (?,?,0,?)", (realm+"."+actor, actor, ends))
            db.execute("INSERT INTO capacity VALUES (?,'circle',?,?)", (actor, actor, ends))
        for portal, fields in [("desk", {"undertaking": title, "brief": brief}),
                               ("source", {"title": title, "observation": content})]:
            db.execute("INSERT INTO record VALUES (?,'case',?,'SYNTHETIC WITHHELD NOTE','open','')",
                       (portal, json.dumps(fields)))
        db.execute("""INSERT INTO undertaking
            (portal,target,source_portal,source_target,office,holder,nominee)
            VALUES ('desk','case','source','case','successor','reader','successor')""")
        grants = {
            "maker": ("assigned", ["read", "request", "offer"]),
            "reader": ("office-holder", ["read", "accept", "decline", "receive_copy", "receipt"]),
            "successor": ("office-holder", ["read", "accept", "decline", "receive_copy", "receipt"]),
            "convenor": ("delegated", ["read", "succeed"]),
        }
        for actor, (kind, actions) in grants.items():
            db.execute("INSERT INTO involvement VALUES (?,'desk','case',?,?)",
                       (actor, "designated" if actor == "successor" else kind, ends))
            for action in actions:
                projection = ["undertaking", "brief"] if action == "read" else []
                db.execute("INSERT INTO recognition VALUES (?,'desk','case',?,?,?,?,0,?)",
                           (realm+"."+actor, actor, kind, action, json.dumps(projection), ends))
        db.execute("INSERT INTO involvement VALUES ('maker','source','case','author',?)", (ends,))
        for action in ("read", "release_copy"):
            db.execute("INSERT INTO recognition VALUES (?,'source','case','maker','author',?,?,0,?)",
                       (realm+".maker", action, '["title","observation"]', ends))

    return UndertakingStore.create(path, realm, seed)


def desk(store):
    return Desk(store, {actor: Binding(actor, store.realm+"."+actor, "circle", actor, "desk", "case")
                        for actor in PROFILES})
