"""Author-defined lager presentation, preserving catalogue mechanics."""
from copy import deepcopy

NAME = "Triton Lager"
DESCRIPTION = ("A blue, non-alcoholic Triton Lager, served chilled: refreshing and exhilarating. "
               "Infused with a particular psychedelic Neptunian microvita. "
               "Excessive drinking carries a high risk of falling through a wormhole.")
SERVING = ("The chilled blue lager is refreshing and exhilarating. "
           "Its Neptunian microvita is psychedelic; it contains no alcohol.")

def describe_lager(item_id, definition):
    if item_id != NAME:
        return definition
    updated = deepcopy(definition)
    updated["description"] = DESCRIPTION
    return updated
