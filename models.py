import uuid, os, yaml
from dataclasses import dataclass, field

BASE_DIR = os.path.dirname(__file__)
LOCAL_VAULT = os.path.join(BASE_DIR, "sessions.yaml")
IDENTITY_FILE = os.path.join(BASE_DIR, "identities.yaml")

@dataclass
class SessionConfig:
    name: str
    host: str
    port: int = 22
    folder: str = "Root"
    profile: str = "DEV"
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

def get_credentials(profile_name):
    default = {"user": "admin", "pass": "admin"}
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            return data.get(profile_name, default)
    return default

def get_all_profiles():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            if data:
                return [(name, name) for name in data.keys()]
    return [("DEV", "DEV"), ("PROD", "PROD")]
