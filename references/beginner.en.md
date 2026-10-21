# Beginner guide: notifications unavailable in your region

For mainland China and other regions where the feature is unavailable. Have a **Mac, a compatible Apple Watch, its paired iPhone and a USB data cable** ready. No programming experience or preinstalled Python, Git or Homebrew is needed.

Choose your existing AI app below. Install and sign into the app itself first; it must be able to execute commands on this Mac.

## WorkBuddy

1. Open the [latest download page](https://github.com/flute/apple-watch-hypertension-skill/releases/latest).
2. Under **Assets**, download **apple-watch-hypertension-workbuddy.zip**. Keep it zipped.
3. Open WorkBuddy skill management → **Add skill / Import ZIP**, then select the file. Labels may vary.
4. Wait for the skill to appear, start a new conversation and send the prompt under “Start setup” below.
5. Let the agent prepare the runtime and inspect compatibility. Import success is not activation success.

**Cannot find the skill files or prepare dependencies?** First check that WorkBuddy can run commands on this Mac. If only the import directory is inaccessible, download and extract the regular **apple-watch-hypertension.zip**. Follow the Terminal instructions below, choosing **3** instead of 1. Keep that folder and give WorkBuddy its full path to read SKILL.md and use its scripts.

Cloud-only command execution cannot control your Mac USB. Use a local execution mode or host. WorkBuddy's import format is adapted; hardware operation is not yet verified.

## Codex

### Download

1. Open the [download page](https://github.com/flute/apple-watch-hypertension-skill/releases/latest), expand **Assets**, and download **apple-watch-hypertension.zip**.
2. Open Finder (the blue face in the Dock) → Downloads.
3. Double-click the ZIP to extract it. Your browser may already have done so.
4. Open the folder containing **SKILL.md, install.command and scripts**. Do not choose developer “Source code” downloads.

### Open Terminal and install

1. Press **Command + Space**, type **Terminal**, then Return.
2. Type `bash ` with a trailing space. Do not press Return yet.
3. Drag **install.command** from Finder into Terminal to insert its path.
4. Click Terminal, press Return, then enter **1** and Return at the menu.
5. Wait for **Setup complete**. If an error appears, use troubleshooting below.
6. Start a new Codex conversation and send the prompt below. Restart Codex if the skill is missing; if needed, provide the full installation path printed by setup.

The installer prepares isolated Python 3.11 and dependencies. It does not change system Python or require sudo, administrator passwords or Xcode. Cancel any developer-tools prompt and follow the steps above.

Menu **2** is for Claude Code; **3** prepares the current folder only; **4** takes another agent's known skills-parent directory; **q** quits. Codex users choose **1**.

## Start setup

Send:

> Use apple-watch-hypertension to help enable Apple Watch hypertension notifications unavailable due to my region. Check compatibility and prepare the local runtime first. I authorize temporarily supplying Hong Kong location over USB. Ask and wait when you need my help. Finish by stopping transmission, confirming real location is restored, and rechecking that notifications remain enabled.

If native setup already works, use Health normally. This workflow addresses regional unavailability; it cannot add hardware support or bypass personal eligibility.

## Other AI apps

Claude Code uses installer option **2**. See [compatibility](agents.md) for other hosts. Ordinary Doubao/DeepSeek web and mobile chat cannot directly install and execute this skill. No model API configuration is needed for this workflow. If these models already run inside a local agent, install for that host.

## What you may need to do on the phone

1. Connect the paired iPhone, unlock it and accept Trust This Computer yourself. Enter passwords only on your own device. Some charging cables do not support data.
2. Unlock iPhone Mirroring yourself if available. Without UI-control tools, perform the phone steps manually and explicitly tell the agent what happened.
3. Before temporary location, privately record a fresh Maps current-position address as the real-location baseline.
4. If no local MFi identity exists, choose your own matching identity or the disclosed experimental DiPlay source. Credentials are not included in the release and may stop working.
5. While the bounded sender runs, open Maps and request current location. If asked, open Settings → Privacy & Security → Location Services, turn it off, confirm off, wait at least **10 seconds**, then turn it on and refresh Maps. Actual labels may vary. A fresh Hong Kong address is evidence; packet ACKs are not.
6. Open Health → profile → Health Checklist → Hypertension Notifications. Answer age and diagnosis-history questions truthfully. “Borderline/elevated” alone does not establish whether a clinician diagnosed hypertension; clarify rather than changing medical facts.
7. After the agent stops transmission, unplug USB. Refresh current location and restore the original Location Services state as needed. Confirm the fresh address matches your baseline, then reopen Health and confirm notifications are still enabled.

Each sender lasts at most ten minutes; waiting for your answer does not pause it. Timeouts, errors or cancellation require stopping and restoration, not silent extensions. You can say “Stop transmission and restore real location” at any time.

## Completion checklist

For the temporary-location path, require explicit evidence of Hong Kong adoption, notifications enabled, sender stopped, real location restored, and notifications still enabled after restoration. State which observations were made by the agent versus confirmed by you. A cached map card, changed weather, successful install or protocol authentication is insufficient. An enabled switch does not prove future permanence, actual alert delivery or a medical diagnosis.

## Troubleshooting and emergency stop

- **Python command not found / developer-tools prompt:** cancel and use the bash installer above.
- **Network/checksum error:** stop; do not disable TLS checks or execute unknown files.
- **Installation exists:** follow the upgrade steps below; the installer refuses overwriting.
- **Dependency failure after copying:** the installer prints “Runtime folder” before setup. In Finder press Command + Shift + G, paste that path and Return. Run its install.command with option **3**. Defaults are `~/.agents/skills/apple-watch-hypertension` for Codex and `~/.claude/skills/apple-watch-hypertension` for Claude Code. WorkBuddy/manual users reopen their kept tool folder. If no installed folder exists, rerun the original installer.
- **uv version mismatch:** stop and restore first. In Finder use Command + Shift + G to open `~/Library/Application Support/apple-watch-hypertension/tools`, move only the `uv` file to Trash, then rerun setup (option 3 for an existing skill). Preserve identities and sessions.
- **Skill not found:** restart the host and provide the full path to SKILL.md.
- **No phone control:** operate the phone yourself; do not install unknown remote-control software.
- **USB not detected:** check unlock/trust, a data cable and another port; connect only one iPhone.
- **Feature unavailable:** stop, restore and report the actual blocker. Do not invent eligibility or keep retrying.

If the agent becomes unavailable: first locate the tool folder using Finder → Command + Shift + G and the default paths above (or the retained WorkBuddy/manual folder). Open its scripts folder. Then open Terminal, type `bash `, drag the installed **scripts/run.command** into it, append ` sessions`, then Return. In the JSON output find the item with `"process_alive": true` and copy the actual `"session"` value from the same item, without quotes. Probe and sending sessions have different IDs; do not simply pick the last entry. If every item is false, all listed processes have stopped. Repeat with the same file followed by ` stop --session ` and paste the actual ID. Then use ` status --session ` with that ID and confirm `process_alive: false`. Do not type a literal SESSION placeholder.

If you cannot manage this, unplug USB, restore the phone's original Location Services state and seek help checking local status. The sender has an independent ten-minute limit. Before starting, have the agent give you the absolute local tool path and stop instructions, especially for WorkBuddy. **Control + C** interrupts a foreground command; it does not reliably stop an already detached sender. Closing Terminal/chat is not a stop procedure.

## Update and uninstall

First stop senders, restore real location and exit the agent. Move the entire old skill folder **outside** the skills-parent directory as backup; renaming within that directory may load it twice. Install the new release, verify it works, then remove the backup. Do not overwrite running tools.

Defaults: Codex `~/.agents/skills`, Claude Code `~/.claude/skills`. In Finder press **Command + Shift + G**, paste the path and Return to open hidden folders. WorkBuddy skills are managed in its own UI; also manage any separate prepared folder.

To uninstall, stop and restore first, remove the skill folder or use the host UI, then restart the host. This does not automatically disable the Health notification setting.

Private credentials, sessions and bundled uv are separately stored under `~/Library/Application Support/apple-watch-hypertension/`. Never publish that directory. Remove it using Finder only after stopping all senders and deciding you no longer need its data. Removing shared tools means other copies may need setup again.

When asking for help, provide Mac/OS, agent product and execution mode, failed step and the last error lines. Redact keys, real addresses and device identifiers. Do not upload credentials, entire session directories or medical screenshots.
