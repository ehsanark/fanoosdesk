import base64
import ipaddress
import json
from pathlib import Path


def render_defaults(template):
    settings = json.loads(Path(__file__).with_name("server-defaults.json").read_text())
    address = str(ipaddress.IPv4Address(settings["server"]))
    key = settings["public_key"]
    if len(base64.b64decode(key, validate=True)) != 32:
        raise ValueError("Expected a base64-encoded 32-byte server public key")
    return template.replace("__FANOOS_IP__", address).replace("__FANOOS_KEY__", key)
