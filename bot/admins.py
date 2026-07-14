import os


DEFAULT_ADMIN_IDS = (1824227638,)


def get_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_USER_IDS", "")
    ids = {
        int(uid.strip())
        for uid in raw.split(",")
        if uid.strip().isdigit()
    }
    if not ids:
        ids = set(DEFAULT_ADMIN_IDS)
    return ids
