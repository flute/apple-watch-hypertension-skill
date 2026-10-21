# Enable Apple Watch Hypertension Notifications in Unsupported Regions

[简体中文](README.md)

**Your Watch supports the feature, but Health says it is unavailable in your region? Let an AI agent help enable it and restore your real location afterward.**

This skill is for users in **regions where hypertension notifications are not available**. It connects an iPhone to a Mac, temporarily supplies a Hong Kong location, and assists with Health setup. The agent asks and waits when you need to connect, unlock or answer a question.

Supports **Claude Code, Codex, WorkBuddy**, and other local agents on a Mac. If the feature already works in your region, follow [Apple's normal setup steps](https://support.apple.com/en-us/117296).

## What you need

- A **Mac** with **Claude Code, Codex or WorkBuddy** able to execute local commands.
- A compatible **Apple Watch** and its paired **iPhone**.
- A **USB data cable**.

No preinstalled Python, Git or Homebrew is needed. Apple's [hardware, software and eligibility requirements](https://support.apple.com/en-us/117296) still apply. This tool cannot add support to incompatible hardware.

## Install for your agent

### Claude Code

1. Download **apple-watch-hypertension.zip** from the [download page](https://github.com/flute/apple-watch-hypertension-skill/releases/latest) and double-click to unzip.
2. Press **Command + Space**, type **Terminal**, then Return.
3. Type `bash ` with a trailing space. Drag **install.command** from the extracted folder into Terminal, then press Return.
4. Enter **2** and Return. Wait for **Setup complete**, then start a new Claude Code conversation.

The installer prepares Python and dependencies. See the [beginner walkthrough](references/beginner.en.md#claude-code) if you have never used Terminal.

### Codex

1. Download **apple-watch-hypertension.zip** from the [download page](https://github.com/flute/apple-watch-hypertension-skill/releases/latest) and double-click to unzip.
2. Press **Command + Space**, type **Terminal**, then Return.
3. Type `bash ` with a trailing space. Drag **install.command** from the extracted folder into Terminal, then press Return.
4. Enter **1** and Return. Wait for **Setup complete**, then start a new Codex conversation.

The installer prepares Python and dependencies. See the [beginner walkthrough](references/beginner.en.md#codex) if you have never used Terminal.

### WorkBuddy

1. Open the [download page](https://github.com/flute/apple-watch-hypertension-skill/releases/latest) and download **apple-watch-hypertension-workbuddy.zip** under **Assets**.
2. Open WorkBuddy skill management → **Add skill / Import ZIP**. Import the ZIP without extracting it.
3. Start a new conversation and send the prompt below. Let the agent prepare the runtime and check your setup.

Cannot find import or run local commands? See the [WorkBuddy walkthrough](references/beginner.en.md#workbuddy).

**Other agents:** see [compatibility](references/agents.md). Ordinary Doubao and DeepSeek web/mobile chat cannot directly install and execute this skill.

## Send this to your agent

> Use apple-watch-hypertension to help enable Apple Watch hypertension notifications unavailable due to my region. Check compatibility and prepare the local runtime first. I authorize temporarily supplying Hong Kong location over USB. Ask and wait when you need my help. Finish by stopping transmission, confirming real location is restored, and rechecking that notifications remain enabled.

Follow the prompts to connect and unlock your phone and answer Health questions truthfully. You do not need to understand the code or protocol.

## What counts as completion

The agent must confirm:

1. Maps adopted the temporary Hong Kong position.
2. Health shows hypertension notifications enabled.
3. Transmission stopped and you unplugged USB.
4. Maps returned to your real location, and notifications are still enabled after reopening Health.

Missing evidence means incomplete setup. To cancel, say: **“Stop transmission and restore real location.”**

## Before you use it

- These are **hypertension notifications**, not blood-pressure readings or a diagnosis.
- Uses local USB, with **no AnyGo cloud dependency**. Credentials are not bundled; the agent follows instructions to prepare them locally. Experimental credentials may stop working.
- One **S12 + Codex** session completed setup, location restoration and notification rechecks. WorkBuddy's import format is adapted but hardware operation remains untested. Success is not guaranteed across devices, OS versions or regions.
- Regional availability changes; check [Apple's current list](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications).

[Beginner guide and troubleshooting](references/beginner.en.md) · [Agent compatibility](references/agents.md) · [Retrospective](references/retrospective.md) · [Technical runbook](references/operations.md) · [Code provenance](THIRD_PARTY_NOTICES.md)

GPL-3.0-only. Independent project; not affiliated with Apple.
