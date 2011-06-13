"""Some constants used with table rows
NEW:
    New object not yet present in the database.
UNCHANGED:
    Object wasn't changed after being loaded from database.
MODIFIED:
    Object was modified and has uncommitted changes which can cause conflicts.
UPDATED:
    Object has relative modifications that will not cause conflicts.
"""

NEW = 'NEW'
UNCHANGED = 'UNCHANGED'
MODIFIED = 'MODIFIED'
UPDATED = 'UPDATED'