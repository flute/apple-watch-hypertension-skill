---
name: apple-watch-hypertension
description: Use when a user wants to set up or verify Apple Watch hypertension notifications, including a locally authorized macOS USB CarKit/iAP2 location workflow. Also applies to 高血压通知开通、地区不可用、停止定位后核验. Does not apply to measuring blood pressure or diagnosing hypertension.
license: GPL-3.0-only
metadata:
  compatibility: Live device operations require a local macOS host, Python 3.11+, uv, a trusted USB iPhone paired with a compatible Apple Watch, and either phone UI control or human assistance.
  version: "0.2.0"
  author: flute
---

# Apple Watch hypertension notifications

Help the user reach a verified setting, then leave the phone at its real location. Speak the user's language. Use the scripts shipped with this skill; resolve paths from this directory, regardless of the chat's working directory. Do not depend on Codex-specific tools.

## Installation and host capabilities

For a first-time user, read [the beginner guide](references/beginner.zh-CN.md) ([English](references/beginner.en.md)) and [agent compatibility](references/agents.md). Never assume Python/Git/Homebrew exists. The bundled bash installer prepares pinned uv, managed Python 3.11 and locked dependencies without sudo. Explain how to open Terminal and drag the installer if the user needs it. Install into the local execution host, not a model-brand directory. Ordinary Doubao/DeepSeek chat is guidance-only unless a local Mac executor is actually established. A successful Skill import does not prove local execution or phone access. After setup, use the absolute bundled uv path from operations, or the prepared scripts/run.command wrapper. Do not repeat setup while a sender is active.

## Before device changes

1. Read [references/operations.md](references/operations.md). Check Apple's current [requirements](https://support.apple.com/en-us/117296) and [region/model availability](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications). This feature sends notifications; it does not measure blood pressure. Unsupported hardware cannot be enabled by this workflow.
2. Establish model/OS compatibility, pairing, wrist detection, the user's requested scope, and available local shell/UI tools. Start with `doctor` and read-only UI inspection. If already enabled, report that and avoid a sender. If supported native setup works, use it without location substitution.
3. For the experimental location path, explain that it temporarily supplies Hong Kong coordinates over USB and requires local MFi credentials. Obtain authorization for that target if the request did not already specify it. Never silently change Apple ID region, system time, VPN, profiles, developer mode, account, or unrelated settings.
4. Record a private baseline of the phone's real map position and original Location Services state. Prefer a readable current-position card; a blank basemap does not invalidate the address. Do not publish addresses/screenshots/identifiers.

## Execute the authorized local path

- Set up pinned dependencies and import/validate credentials as described in operations. Use the exact pinned DiPlay v0.2.7 assets or the user's matching MFi-v3 identity. Keep credentials outside the skill and out of Git. A local key test is not iPhone trust.
- Have the user connect/unlock/trust the USB iPhone and unlock iPhone Mirroring themselves. Never request passwords. `doctor --device` requires exactly one USB phone. If UI automation is unavailable, give the same phone steps to the user and wait for confirmation.
- Run a bounded `start --probe`, inspect authentication/identification/subscription events, and stop it before a sending session. Start `--hong-kong` for at most 600 seconds. Save its returned session ID, absolute local tool path and stop command; give the human the stop instructions before sending. Write the original Location Services state, private baseline and pending human action with `handoff` so another agent can resume. Do not silently restart or extend an expired session.
- Open Maps and request current position. If ignored, turn Location Services off, confirm off, wait at least 10 seconds, and turn it back on **while the sender is running**. Confirm the actual current-position address is in Hong Kong before recording `location_adopted`. Packet ACKs alone are insufficient. Use the bounded retry limit in operations.
- Open Health → profile → Health Checklist → Hypertension Notifications. For eligibility, use only facts the user provides, or let them answer on the phone. “Borderline/elevated” is not evidence of a prior diagnosis. Ask whether a clinician/report explicitly diagnosed hypertension; if unknown, wait or stop and restore. Never choose a convenient answer to pass setup.
- Proceed through the actual screens, including their limitations, and confirm “set up”/“notifications on.” Record `notification_enabled`. Follow current UI, not fixed coordinates or assumed button order.

## Human assistance and cleanup

Ask a concrete question/action and wait using the host's input/wait mechanism. A timeout is not an answer. Continue only independent work; the sender's deadline still applies. If the user is unavailable, the budget expires, an error occurs, or the task is cancelled, stop transmission and perform cleanup. Do not leave a sender running after ending the turn.

If a session was started, on **every** exit run `stop`, confirm `process_alive: false`, and ask the user to unplug USB. Restore the original Location Services state; if it was originally on and a cached fix persists, cycle off for 10 seconds and back on. Request a fresh map position and compare it with the baseline, allowing reverse-geocoding time. Record `real_location_restored` only after observation or explicit user confirmation. Reopen Health after restoration and record `notification_rechecked_after_restore` only when it still says on.

For a temporary-location session, `report` must show all four external observations plus a stopped sender before reporting completion. For native setup or an already-enabled setting, no location sender/session or Hong Kong observation is required: verify the actual Health setting and report that no temporary-location workflow was used. Identify whether evidence was agent-observed or user-confirmed. If any check is unresolved, report exactly what succeeded and what remains unverified. Never claim future permanence, a hypertension diagnosis, blood-pressure readings, or actual notification delivery from an enabled switch.
