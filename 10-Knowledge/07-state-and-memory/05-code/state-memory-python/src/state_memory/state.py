class VersionConflict(RuntimeError):
    """The caller read an older version. Reload and explicitly decide a merge."""


class MemoryConflict(VersionConflict):
    pass
