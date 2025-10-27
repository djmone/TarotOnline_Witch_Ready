
import os, hashlib
def make_seed(): return os.urandom(16).hex()
def commit_seed(seed: str, user_id: int, preset_slug: str, created_at_iso: str) -> str:
    data = f"{seed}|{user_id}|{preset_slug}|{created_at_iso}".encode()
    return hashlib.sha256(data).hexdigest()
