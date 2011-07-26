"""Some constants used with table rows
NEW:
    New object not yet present in the database.
UNCHANGED:
    Object wasn't changed after being loaded from database.
MODIFIED:
    Object was modified and has uncommitted changes which can cause conflicts.
UPDATED:
    Object has relative modifications that will not cause conflicts.
DELETED:
    Object is unaccessible and will be deleted on from db on flush
ORPHANED:
    Object belongs to a class with dependent relationship with other class, but
    has currently no parent. It will be deleted if flushed now, but if it gets
    a new parent, it will be preserved
"""

NEW = 'NEW'
UNCHANGED = 'UNCHANGED'
MODIFIED = 'MODIFIED'
UPDATED = 'UPDATED'
DELETED = 'DELETED'
ORPHANED = 'ORPHANED'