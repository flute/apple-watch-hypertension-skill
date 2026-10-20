# Apple Watch Hypertension Notifications Skill

[简体中文](README.md)

**Let an AI agent check, set up, and verify Apple Watch hypertension notifications.**

For Codex, Claude Code, WorkBuddy, and other local agents on a Mac. The agent handles available automation, asks you to connect/unlock or answer health questions when needed, and waits. It finishes by stopping the sender, verifying your real location, and checking that notifications remain on.

> This enables notifications, not blood-pressure measurement. Compatible hardware, software, and eligibility are required. Regional approval or device changes may prevent setup; success is not guaranteed for every Apple Watch.

## Install

Clone the repository and choose one:

```sh
git clone https://github.com/flute/apple-watch-hypertension-skill.git
cd apple-watch-hypertension-skill

# Codex
python3 scripts/install.py --agent codex

# Claude Code
python3 scripts/install.py --agent claude
```

**WorkBuddy:** download `apple-watch-hypertension-workbuddy.zip` from [Releases](https://github.com/flute/apple-watch-hypertension-skill/releases) and import it on the Skills page.

For another `SKILL.md` host, use `python3 scripts/install.py --target /your/skills/directory`. Reload skills or start a new conversation. Installing a skill does not grant an agent USB access or phone UI tools it does not already have.

## Use

Send your agent:

> Use apple-watch-hypertension to check and set up Apple Watch hypertension notifications. If needed, I authorize temporary Hong Kong location over local USB CarKit. Ask and wait when you need my help. Finish by confirming my real location has returned and notifications remain enabled.

Have a **Mac, the iPhone paired with your Watch, a USB data cable, and [uv](https://docs.astral.sh/uv/getting-started/installation/)** ready. The agent checks the remaining requirements and installs pinned dependencies. Without phone UI tools, you perform and confirm the phone steps.

## What happens

1. Check compatibility and current settings. Skip changes if already enabled; use normal setup when available.
2. Only if needed and authorized, authenticate locally with MFi-v3 and send Hong Kong NMEA through USB CarKit. **No AnyGo cloud dependency.**
3. Verify the actual position in Maps, then complete Health setup using your truthful eligibility answers.
4. Stop, unplug USB, verify your real location, and recheck notifications. Missing evidence is reported as incomplete.

The repository **does not contain certificates or private keys**. Use your own matching identity, or ask the agent to extract the experimental identity locally from the specified DiPlay APK. Credentials stay on your Mac; the experimental identity can stop working. IP networking is denied for the sender; each session lasts at most ten minutes.

## Verification and limits

The workflow succeeded in one S12 device session, including restoration checks. The packaged scripts pass offline tests. Claude / WorkBuddy installation formats are adapted but have not each been tested against a live device. See the [retrospective](references/retrospective.md) and [runbook](references/operations.md).

Developer checks (source checkout only): `uv sync --frozen && uv run pytest -q && uv run ruff check scripts tests`

[Apple instructions](https://support.apple.com/en-us/117296) · [Region/model availability](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications) · [Code provenance and licenses](THIRD_PARTY_NOTICES.md)

GPL-3.0-only. Independent project; not affiliated with Apple.
