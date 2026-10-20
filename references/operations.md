# Runbook

For beginners use [the detailed guide](beginner.zh-CN.md) ([English](beginner.en.md)); check [host capabilities](agents.md). From the skill root, `bash install.command --prepare` prepares dependencies without preinstalled Python/Git. The installer stores uv at `$HOME/Library/Application Support/apple-watch-hypertension/tools/uv`; when following the commands below, use that absolute path in place of `uv` if uv is not on PATH. The prepared `bash scripts/run.command doctor` wrapper runs the same tool without uv on PATH; other watchbp subcommands work the same way. Identity import can use `.venv/bin/python scripts/import_diplay_identity.py` after setup.

These commands run from the skill root. `uv` must already be installed from its [official instructions](https://docs.astral.sh/uv/getting-started/installation/). Never pipe an unreviewed install command into a shell. Python 3.11+ is required; `uv` can select an existing interpreter. If dependencies or USB are unavailable, explain the missing capability and ask for the necessary local action.

## Setup (network access)

```sh
uv sync --frozen --no-dev
uv run --frozen --no-sync python scripts/watchbp.py doctor
uv run --frozen --no-sync python scripts/watchbp.py doctor --device
```

The phone must be unlocked and already trust the Mac. Device inspection prints model/OS, not UDID or device name. Never auto-pair an unexpected phone. Remote/cloud agents without a Mac-side executor cannot access the user's USB phone.

Default local data: `~/Library/Application Support/apple-watch-hypertension/`. Identities and sessions remain outside the skill. Session logs record protocol milestones, not health answers, private keys, challenges, or real addresses. Do not upload the data directory.

### Identity

Explain provenance before import: the optional shared experimental identity was recovered from public Carlinkit firmware and bundled in DiPlay. It is not issued to this project and can be revoked. It is not covered by this repository's software license. Do not redistribute it. See [DiPlay's notice](https://github.com/shihabal3amri/DiPlay/blob/main/docs/THIRD_PARTY_NOTICES.md#experimental-authentication-data).

If the user's request already specifies this source, no repeated source approval is needed. Otherwise offer their own matching identity or this documented experimental source and wait for a choice.

```sh
uv run --frozen --no-sync python scripts/import_diplay_identity.py --download \
  --output-dir "$HOME/Library/Application Support/apple-watch-hypertension/identity"
uv run --frozen --no-sync python scripts/watchbp.py check-identity
```

`--apk /absolute/path/DiPlay-0.2.7.apk` supports an existing APK. The importer pins the APK SHA-256, reads only `assets/offline-mfi/certificate.p7b` and `identity.pk8`, validates P-256 consistency, and creates a new directory (0700) with files (0600). It never installs/runs the APK and never overwrites an existing identity. If the identity exists, validate/reuse it; do not delete it to make import pass. Custom identities use `--identity-dir /absolute/directory` on check/start. The sender loads certificate/key in-process and signs the **already hashed 32 bytes** with prehashed ECDSA P-256, returning 64-byte raw `r||s`.

## Probe, send, wait

```sh
uv run --frozen --no-sync python scripts/watchbp.py start --probe --hong-kong --duration 45
```

Save the returned `session`. Replace `SESSION` below with that exact ID:

```sh
uv run --frozen --no-sync python scripts/watchbp.py status --session SESSION
uv run --frozen --no-sync python scripts/watchbp.py stop --session SESSION
```

Probe does not send NMEA. Open Maps if there is no subscription. Expect `MFi_v3_authenticated`, `identification_accepted`, and `location_subscribed`. A probe may end without a subscription; report the missing milestone, not success. Once the probe stops:

```sh
uv run --frozen --no-sync python scripts/watchbp.py start --hong-kong --duration 600
```

Keep the **new** session ID. Both workers use macOS `sandbox-exec` to deny IP networking; USB uses a local Unix socket. Dependencies/import use network only during setup. The clock is read from the iPhone for NMEA timestamps; device/system time is never changed. GGA/RMC are separately encoded in repeated parameter 0, each with CRLF and NUL termination; only subscribed sentences are sent. Link ACKs demonstrate delivery, not adoption.

For agent/context changes, save a local handoff immediately after start (use the real original state and a concise private baseline):

```sh
uv run --frozen --no-sync python scripts/watchbp.py handoff --session SESSION \
  --original-location-services on --baseline-note 'Private baseline observed before sending' \
  --waiting-for eligibility
uv run --frozen --no-sync python scripts/watchbp.py sessions
uv run --frozen --no-sync python scripts/watchbp.py handoff --session SESSION
```

Replace the example baseline with the actual privately observed place/card information. Do not store health answers or passwords. `handoff` without update flags reads the private resume record; `status`/`report` omit its baseline text. `sessions` finds lost IDs and lists approximate remaining budgets. Carry the same baseline/original-state record into the sending session after a probe; do not mistake a probe ID for the active sender. A resumed agent must re-observe the phone and sender state; a pending request never counts as an answer.

The independent worker survives an agent turn ending, but always expires within its configured budget plus bounded cleanup. Treat this as a backstop, **not** permission to abandon cleanup. `stop` is idempotent and verifies process start time/token before signalling its process group. Multiple simultaneous senders are refused. Status/reports never connect to the phone.

Ask the user for one concrete action at a time: connect/trust, unlock mirroring, answer an eligibility question, or unplug. Use a host-specific question tool if present; otherwise ask in chat and wait. At most 30–60 seconds per bounded observation wait; send progress only for a meaningful change. Before waiting for a long/unbounded response, stop and restore; resume only with the user, within a newly disclosed bounded session. Never infer medical facts, permission, or completion from silence.

## Observe and record

Use native/UI tools if available. In iPhone Mirroring, use the app's Home/App Switcher/Spotlight controls, read a fresh screenshot after transitions, and focus search before typing. It may have no meaningful accessibility tree. Scroll using the host's scroll tool. Do not use screen coordinates from another Mac or a previous screen. If a screen does not react, re-observe before retrying; human interference can invalidate pending input.

For Maps, close an old “My Location” card, tap recenter, open the **new blue dot**, and wait for address reverse-geocoding. Basemap tiles and old cards may be cached. If Hong Kong is not adopted, perform **one** 10-second Location Services cycle while sending, then request a fresh fix. Check clock-alignment and subscription status. A second cycle is allowed only after a concrete protocol/clock correction; otherwise stop/restore and report the blocker. Do not start an open-ended retry loop.

The initial case resolved only after GGA and RMC were encoded as separate parameters. The included sender already implements this; do not replace it with a combined text parameter or a cloud location service.

After actually observing each milestone:

```sh
uv run --frozen --no-sync python scripts/watchbp.py verify --session SESSION \
  --event location_adopted --source agent-observed
uv run --frozen --no-sync python scripts/watchbp.py verify --session SESSION \
  --event notification_enabled --source agent-observed
```

Use `--source user-confirmed` only when the human explicitly confirms that specific milestone. This ledger records assertions from observation; it cannot read phone settings itself. Never mark events merely to satisfy the completion checker.

Health path: Health → profile → Health Checklist → Hypertension Notifications → eligibility → informational screens → Done. Localized labels, OS versions and ordering vary. Ask for missing answers without collecting the user's whole medical report. “Never explicitly diagnosed; only elevated readings” supports “No previous diagnosis” as the user's report; “borderline” alone does not. A prior diagnosis, age below the current minimum, or an unknown answer must not be bypassed. If eligibility prevents setup, stop/restore and report the actual outcome. Do not alter birth date, diagnoses or pregnancy records.

## Stop and verify restoration

```sh
uv run --frozen --no-sync python scripts/watchbp.py stop --session SESSION
uv run --frozen --no-sync python scripts/watchbp.py status --session SESSION
```

Require `process_alive: false`. A closed service can leave the last accessory fix cached. Ask the user to **unplug USB** and wait; mirroring can remain connected wirelessly. Refresh Location Services if necessary, preserving its original state. Compare a fresh current-position card with the baseline; allow reverse-geocoding time. On the initial case, the weather changed before the address finished updating: weather alone was not accepted as proof.

```sh
uv run --frozen --no-sync python scripts/watchbp.py verify --session SESSION \
  --event real_location_restored --source agent-observed
# Reopen Health after the above observation; inspect the actual “notifications on” state.
uv run --frozen --no-sync python scripts/watchbp.py verify --session SESSION \
  --event notification_rechecked_after_restore --source agent-observed
uv run --frozen --no-sync python scripts/watchbp.py report --session SESSION
```

If the user must leave or hardware access is lost, stop first, request unplugging/restoration, and report restoration as unverified until confirmed. Do not end with an unmentioned active worker or silently mark a missing check complete. No notification trigger is fabricated to test delivery.
