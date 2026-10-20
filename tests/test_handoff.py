from bpkit.session import atomic_json
from watchbp import handoff, status


def make_session(tmp_path):
    atomic_json(
        tmp_path / "process.json", {"pid": 99999999, "fingerprint": "none", "token": "none"}
    )
    atomic_json(tmp_path / "config.json", {"duration": 60, "started_at": 0})
    return tmp_path


def test_private_handoff_survives_agent_change_and_report_hides_baseline(tmp_path):
    folder = make_session(tmp_path)
    note = "private original landmark test"
    saved = handoff(folder, "on", note, "eligibility")
    assert saved["baseline_note"] == note
    assert handoff(folder)["waiting_for"] == "eligibility"
    report = status(folder)
    assert note not in str(report)
    assert report["handoff"]["baseline_recorded"]
    assert report["handoff"]["original_location_services"] == "on"
