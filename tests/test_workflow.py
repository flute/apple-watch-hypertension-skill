import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bpkit.workflow import Evidence, completion, evidence_record


def test_delivery_is_not_location_or_notification_success():
    e = Evidence(authenticated=True, identified=True, subscribed=True, packets=80)
    assert completion(e)["result"] == "incomplete"
    assert not completion(e)["location_restored"]


def test_success_requires_stop_restore_and_notification_after_restore():
    e = Evidence(location_adopted=True, notification_enabled=True, sender_stopped=True)
    assert completion(e)["result"] == "incomplete"
    e.real_location_restored = True
    assert completion(e)["result"] == "incomplete"
    e.notification_rechecked_after_restore = True
    assert completion(e)["result"] == "complete"


def test_never_report_success_if_setup_failed_but_cleanup_succeeded():
    e = Evidence(sender_stopped=True, real_location_restored=True)
    assert completion(e)["result"] == "incomplete"


def test_evidence_is_local_summary_not_raw_health_data():
    record = evidence_record("real_location_restored", "agent-observed")
    assert record["source"] == "agent-observed"
    assert "address" not in record
    with pytest.raises(ValueError):
        evidence_record("diagnosis", "guess")
