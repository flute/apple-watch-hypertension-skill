"""Evidence bookkeeping: transport events never imply a medical feature was enabled."""

from dataclasses import dataclass
from datetime import UTC, datetime

EVENTS = {
    "location_adopted",
    "notification_enabled",
    "real_location_restored",
    "notification_rechecked_after_restore",
}
SOURCES = {"agent-observed", "user-confirmed"}


@dataclass
class Evidence:
    authenticated: bool = False
    identified: bool = False
    subscribed: bool = False
    packets: int = 0
    location_adopted: bool = False
    notification_enabled: bool = False
    sender_stopped: bool = False
    real_location_restored: bool = False
    notification_rechecked_after_restore: bool = False


def completion(evidence):
    restored = evidence.sender_stopped and evidence.real_location_restored
    done = all(
        (
            evidence.location_adopted,
            evidence.notification_enabled,
            restored,
            evidence.notification_rechecked_after_restore,
        )
    )
    return {"result": "complete" if done else "incomplete", "location_restored": restored}


def evidence_record(event, source):
    if event not in EVENTS or source not in SOURCES:
        raise ValueError("Unsupported evidence event or source")
    return {"event": event, "source": source, "at": datetime.now(UTC).isoformat()}
