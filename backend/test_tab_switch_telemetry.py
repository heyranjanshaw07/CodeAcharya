import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from main import app
from database import get_db, format_timestamp_ist, parse_utc_timestamp, IST_TZ
import performance_service
import pdf_generator

client = TestClient(app)

def create_test_user(name: str = "Telemetry Test Student") -> tuple[str, str, dict]:
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    resp = client.post("/api/auth/register", json={
        "full_name": name,
        "email": email,
        "password": pwd
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    user_id = data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, token, headers


# 1. Page hidden for 15s records ~15s (using controlled/mocked clocks)
def test_page_hidden_15s_records_15s():
    uid, token, headers = create_test_user("Hidden 15s User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t0 = datetime(2026, 10, 27, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=15)

    ev_id = f"ts_{uuid.uuid4().hex[:8]}"

    # Page hidden
    resp_hide = client.post("/api/tab-switch/record", headers=headers, json={
        "id": ev_id,
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t0.isoformat(),
        "event_status": "away"
    })
    assert resp_hide.status_code == 200
    assert resp_hide.json()["event_status"] in ("away", "incomplete")

    # Page returned after 15s
    resp_ret = client.post("/api/tab-switch/record", headers=headers, json={
        "id": ev_id,
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t0.isoformat(),
        "return_timestamp": t1.isoformat(),
        "time_away_seconds": 15,
        "event_status": "returned"
    })
    assert resp_ret.status_code == 200
    ret_data = resp_ret.json()
    assert ret_data["event_status"] == "returned"
    assert ret_data["time_away_seconds"] == 15

    perf = performance_service.get_student_performance_data(uid, "all")
    events = perf["tab_switch_events"]
    assert len(events) == 1
    assert events[0]["duration_away_seconds"] == 15
    assert events[0]["status"] == "returned"
    assert "15s" in events[0]["duration_away_formatted"]


# 2. Page hidden for 60s records ~60s (using controlled/mocked clocks)
def test_page_hidden_60s_records_60s():
    uid, token, headers = create_test_user("Hidden 60s User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t0 = datetime(2026, 10, 27, 11, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=60)

    ev_id = f"ts_{uuid.uuid4().hex[:8]}"

    # Page hidden
    client.post("/api/tab-switch/record", headers=headers, json={
        "id": ev_id,
        "attempt_id": attempt_id,
        "question_id": "factorial-recursion",
        "event_timestamp": t0.isoformat(),
        "event_status": "away"
    })

    # Page returned after 60s
    resp_ret = client.post("/api/tab-switch/record", headers=headers, json={
        "id": ev_id,
        "attempt_id": attempt_id,
        "question_id": "factorial-recursion",
        "event_timestamp": t0.isoformat(),
        "return_timestamp": t1.isoformat(),
        "time_away_seconds": 60,
        "event_status": "returned"
    })
    assert resp_ret.status_code == 200
    assert resp_ret.json()["time_away_seconds"] == 60

    perf = performance_service.get_student_performance_data(uid, "all")
    events = perf["tab_switch_events"]
    assert len(events) == 1
    assert events[0]["duration_away_seconds"] == 60
    assert events[0]["status"] == "returned"
    assert "1m" in events[0]["duration_away_formatted"] or "60s" in events[0]["duration_away_formatted"]


# 3. Multiple hide/return cycles produce separate, correctly paired events
def test_multiple_hide_return_cycles_separate_paired():
    uid, token, headers = create_test_user("Multi Cycles Paired User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    base_t = datetime(2026, 10, 27, 12, 0, 0, tzinfo=timezone.utc)

    cycle_durations = [12, 28, 45]
    for idx, dur in enumerate(cycle_durations):
        t_hide = base_t + timedelta(minutes=idx * 2)
        t_ret = t_hide + timedelta(seconds=dur)
        ev_id = f"ts_{idx}_{uuid.uuid4().hex[:6]}"

        client.post("/api/tab-switch/record", headers=headers, json={
            "id": ev_id,
            "attempt_id": attempt_id,
            "question_id": "two-sum",
            "event_timestamp": t_hide.isoformat(),
            "event_status": "away"
        })
        client.post("/api/tab-switch/record", headers=headers, json={
            "id": ev_id,
            "attempt_id": attempt_id,
            "question_id": "two-sum",
            "event_timestamp": t_hide.isoformat(),
            "return_timestamp": t_ret.isoformat(),
            "time_away_seconds": dur,
            "event_status": "returned"
        })

    perf = performance_service.get_student_performance_data(uid, "all")
    events = perf["tab_switch_events"]
    assert len(events) == 3

    # tab_switch_events is returned in reverse-chronological order (most recent first)
    assert events[0]["switch_number"] == 3
    assert events[1]["switch_number"] == 2
    assert events[2]["switch_number"] == 1

    durations_recorded = {e["switch_number"]: e["duration_away_seconds"] for e in events}
    assert durations_recorded[1] == 12
    assert durations_recorded[2] == 28
    assert durations_recorded[3] == 45

    assert perf["summary"]["total_tab_switches"] == 3
    assert perf["summary"]["total_time_away_seconds"] == sum(cycle_durations)


# 4. Duplicate visibility events do not create duplicate records
def test_duplicate_visibility_events_deduplicated():
    uid, token, headers = create_test_user("Deduplication Test User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t_away = datetime(2026, 10, 27, 13, 0, 0, tzinfo=timezone.utc).isoformat()

    # Browser triggers visibilitychange and blur simultaneously
    for _ in range(4):
        r = client.post("/api/tab-switch/record", headers=headers, json={
            "attempt_id": attempt_id,
            "question_id": "two-sum",
            "event_timestamp": t_away,
            "event_status": "away"
        })
        assert r.status_code == 200

    perf = performance_service.get_student_performance_data(uid, "all")
    # Only 1 open event should exist
    assert len(perf["tab_switch_events"]) == 1


# 5. Missing return event is marked incomplete (Awaiting return / Incomplete, never falsely returned)
def test_missing_return_event_marked_incomplete():
    uid, token, headers = create_test_user("Incomplete Telemetry User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t_away = datetime(2026, 10, 27, 14, 0, 0, tzinfo=timezone.utc).isoformat()

    # User left tab and never returned (e.g. browser tab closed or process terminated)
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t_away,
        "event_status": "away"
    })

    perf = performance_service.get_student_performance_data(uid, "all")
    assert len(perf["tab_switch_events"]) == 1
    ev = perf["tab_switch_events"][0]

    assert ev["status"] in ("away", "incomplete")
    assert ev["status"] != "returned"
    assert ev["return_time_ist"] in ("Awaiting return", "Active / Pending Return")
    assert ev["duration_away_formatted"] in ("Incomplete", "Pending")
    assert ev["duration_away_seconds"] == 0


# 6. Timestamps display correctly in Indian Standard Time (Asia/Kolkata)
def test_timestamps_display_correctly_in_ist():
    uid, token, headers = create_test_user("IST Display User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    # 2026-10-27 05:00:00 UTC == 2026-10-27 10:30:00 IST (+5:30)
    t0_utc = datetime(2026, 10, 27, 5, 0, 0, tzinfo=timezone.utc)
    t1_utc = t0_utc + timedelta(seconds=45) # 10:30:45 IST

    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t0_utc.isoformat(),
        "return_timestamp": t1_utc.isoformat(),
        "time_away_seconds": 45,
        "event_status": "returned"
    })

    perf = performance_service.get_student_performance_data(uid, "all")
    ev = perf["tab_switch_events"][0]

    assert "10:30:00" in ev["hidden_time_ist"]
    assert "IST" in ev["hidden_time_ist"]
    assert "10:30:45" in ev["return_time_ist"]
    assert "IST" in ev["return_time_ist"]


# 7. Refreshing/navigating does not create false zero-duration events
def test_refresh_navigating_does_not_create_false_zero_events():
    uid, token, headers = create_test_user("Refresh Navigation User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t_start = datetime(2026, 10, 27, 15, 0, 0, tzinfo=timezone.utc).isoformat()

    # User starts session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 10,
        "start_time": t_start,
        "session_status": "running"
    })

    # User reloads page (sends session heartbeat/reload) without switching away
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 20,
        "start_time": t_start,
        "session_status": "running"
    })

    perf = performance_service.get_student_performance_data(uid, "all")
    # Must NOT have created any tab switch events
    assert len(perf["tab_switch_events"]) == 0
    assert perf["summary"]["total_tab_switches"] == 0


# 8. PDF report reflects persisted telemetry data
def test_pdf_report_reflects_persisted_telemetry_data():
    uid, token, headers = create_test_user("PDF Telemetry User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    t0 = datetime(2026, 10, 27, 16, 0, 0, tzinfo=timezone.utc)

    # Record 2 tab-switches: 18s and 42s
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t0.isoformat(),
        "return_timestamp": (t0 + timedelta(seconds=18)).isoformat(),
        "time_away_seconds": 18,
        "event_status": "returned"
    })
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": (t0 + timedelta(minutes=2)).isoformat(),
        "return_timestamp": (t0 + timedelta(minutes=2, seconds=42)).isoformat(),
        "time_away_seconds": 42,
        "event_status": "returned"
    })

    # Record completed session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 300,
        "status": "completed",
        "passed_count": 2,
        "total_count": 2,
        "overall_score": 90.0
    })

    # Generate PDF
    pdf_resp = client.get("/api/reports/pdf?date_filter=all", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000
    assert pdf_resp.content.startswith(b"%PDF")


# 9. Historical records with missing or identical timestamps do not crash report generation and display Legacy / Unrecorded / N/A
def test_historical_unrecorded_records_do_not_crash_and_display_legacy_na():
    uid, token, headers = create_test_user("Historical Records User")
    legacy_ts = "2026-10-23T05:02:26Z"

    # Insert historical/legacy 0s record with identical hidden and return timestamps directly into database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tab_switch_events (
                id, user_id, attempt_id, question_id,
                event_timestamp, return_timestamp, time_away_seconds, event_status, created_at
            ) VALUES (?, ?, NULL, 'two-sum', ?, ?, 0, 'returned', ?)
        """, (f"ts_leg_{uuid.uuid4().hex[:6]}", uid, legacy_ts, legacy_ts, legacy_ts))
        conn.commit()

    perf = performance_service.get_student_performance_data(uid, "all")
    events = perf["tab_switch_events"]
    assert len(events) == 1
    ev = events[0]

    # Verify graceful display without crashing
    assert ev["is_unrecorded"] is True
    assert ev["status"] == "historical_unrecorded"
    assert ev["duration_away_formatted"] == "N/A"
    assert ev["duration_away_seconds"] == 0

    # Verify PDF generation does not crash on historical unrecorded records
    pdf_bytes = pdf_generator.generate_student_performance_pdf(
        data=perf,
        include_tab_switches=True,
        include_viva=False
    )
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


# 10. Identical/fractional timestamps duration consistency and rounding regression test
def test_identical_timestamps_duration_consistency_and_rounding():
    uid, token, headers = create_test_user("Rounding Consistency User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"

    # Pair A: 6.987s and 7.283s (both format to 22:31:36 IST -> 22:31:43 IST)
    # Must BOTH calculate to 7s using consistent nearest-second rounding (never 6s vs 7s)
    a1_hide = "2026-10-24T17:01:36.296000+00:00"
    a1_ret = "2026-10-24T17:01:43.283000+00:00"
    a2_hide = "2026-10-24T17:01:36+00:00"
    a2_ret = "2026-10-24T17:01:43.283000+00:00"

    # Pair B: 1.602s and 2.151s (both format to 22:29:49 IST -> 22:29:51 IST)
    # Must BOTH calculate to 2s using consistent nearest-second rounding (never 1s vs 2s)
    b1_hide = "2026-10-24T16:59:49.549000+00:00"
    b1_ret = "2026-10-24T16:59:51.151000+00:00"
    b2_hide = "2026-10-24T16:59:49+00:00"
    b2_ret = "2026-10-24T16:59:51.151000+00:00"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO coding_attempts (
                id, user_id, question_id, language, attempt_status,
                start_time, end_time, elapsed_coding_time_seconds,
                is_completed, passed_count, total_count, created_at, last_activity_at
            ) VALUES (?, ?, 'edit-distance-dp', 'python', 'abandoned', ?, NULL, 120, 0, 0, 3, ?, ?)
        """, (attempt_id, uid, b2_hide, b2_hide, b2_hide))

        for ev_id, h, r in [
            (f"ts_a1_{uuid.uuid4().hex[:6]}", a1_hide, a1_ret),
            (f"ts_a2_{uuid.uuid4().hex[:6]}", a2_hide, a2_ret),
            (f"ts_b1_{uuid.uuid4().hex[:6]}", b1_hide, b1_ret),
            (f"ts_b2_{uuid.uuid4().hex[:6]}", b2_hide, b2_ret)
        ]:
            cursor.execute("""
                INSERT INTO tab_switch_events (
                    id, user_id, attempt_id, question_id,
                    event_timestamp, return_timestamp, time_away_seconds, event_status, created_at
                ) VALUES (?, ?, ?, 'edit-distance-dp', ?, ?, 0, 'returned', ?)
            """, (ev_id, uid, attempt_id, h, r, h))
        conn.commit()

    perf = performance_service.get_student_performance_data(uid, "all")
    events = perf["tab_switch_events"]
    assert len(events) == 4

    # Tab switch events are in reverse chronological order
    # Pair A events:
    pair_a = [e for e in events if "22:31:36" in e["hidden_time_ist"]]
    assert len(pair_a) == 2
    for ev in pair_a:
        assert ev["hidden_time_ist"] == "2026-10-24 22:31:36 IST"
        assert ev["return_time_ist"] == "2026-10-24 22:31:43 IST"
        assert ev["duration_away_seconds"] == 7
        assert ev["duration_away_formatted"] == "7s"
        assert ev["status"] == "returned"

    # Pair B events:
    pair_b = [e for e in events if "22:29:49" in e["hidden_time_ist"]]
    assert len(pair_b) == 2
    for ev in pair_b:
        assert ev["hidden_time_ist"] == "2026-10-24 22:29:49 IST"
        assert ev["return_time_ist"] == "2026-10-24 22:29:51 IST"
        assert ev["duration_away_seconds"] == 2
        assert ev["duration_away_formatted"] == "2s"
        assert ev["status"] == "returned"

    # Summary matches sum of events exactly (7 + 7 + 2 + 2 = 18s)
    assert perf["summary"]["total_tab_switches"] == 4
    assert perf["summary"]["total_time_away_seconds"] == 18

    # PDF generation reflects these exact consistent values
    pdf_bytes = pdf_generator.generate_student_performance_pdf(
        data=perf,
        include_tab_switches=True,
        include_viva=False
    )
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000

