"""Webhook verification over raw bytes. Deduplicate event ids in your application."""
import hashlib
import hmac
import math
import re
import time

def verify_webhook(raw_body: bytes | str, header: str | None, secret: str, *, tolerance_seconds: float = 300,
                   now: float | None = None) -> bool:
    """Verify the Classive-Signature header before decoding JSON; default replay window is five minutes."""
    if not header or not secret or len(header) > 100: return False
    match = re.fullmatch(r"t=(\d+),v1=([0-9a-f]{64})", header.strip())
    if not match: return False
    timestamp = int(match[1])
    current = time.time() if now is None else now
    if not math.isfinite(current) or not math.isfinite(tolerance_seconds) or tolerance_seconds < 0 or abs(current - timestamp) > tolerance_seconds:
        return False
    data = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
    signed = str(timestamp).encode("ascii") + b"." + data
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, match[2])
