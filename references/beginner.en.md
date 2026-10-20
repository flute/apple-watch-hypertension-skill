# First-time setup, without Python or Git

You need a **Mac**, a compatible Apple Watch, its paired iPhone and a USB data cable. This enables hypertension **notifications**, not numerical blood-pressure readings. Hardware, OS and eligibility requirements still apply.

You do not need to preinstall Python, Git, Homebrew or Xcode. Installing a skill does not install an AI product or provide a subscription. Choose a local agent that can run commands on the Mac connected to your phone. Read the [compatibility table](agents.md): a model name is not an execution environment.

## Download

1. Open the [latest release](https://github.com/flute/apple-watch-hypertension-skill/releases/latest) in your Mac browser.
2. Expand **Assets** and download **apple-watch-hypertension.zip**, not “Source code.”
3. Open Finder (the blue face in the Dock), select Downloads and double-click the ZIP. Your browser may already have extracted it.
4. Open the extracted folder. You should see SKILL.md, install.command and scripts. Keep this folder if using manual/WorkBuddy mode.
5. If GitHub is unreachable, fix access or obtain the unchanged release from someone you trust. Do not run random mirror/accelerator scripts. SHA256SUMS is available in the same release.

## Open Terminal and install

1. Press **Command + Space**, type **Terminal**, then Return. Alternatively open Finder → Applications → Utilities → Terminal.
2. In Terminal type `bash ` including the trailing space. Do not press Return yet.
3. Drag **install.command** from Finder into Terminal. This inserts its path, including any necessary escaping.
4. Click Terminal and press Return.
5. Enter **1** for Codex, **2** for Claude Code, **3** to prepare the current folder for WorkBuddy/manual use, or **4** for a known custom skills-parent directory. Press Return. Enter **q** to quit without installing.
6. Option 4 asks for an absolute path starting with `/`; it creates an apple-watch-hypertension folder below it. Do not copy placeholder paths.
7. Wait for **Setup complete** and the installation path. On first run, it downloads pinned uv, managed Python 3.11 and locked dependencies. Progress and speed depend on your network.
8. If an error appears, setup is incomplete. Keep the last few lines for help. No phone action or location transmission starts during installation.

We cannot assume Python is installed or recent enough. This installer prepares an isolated environment without changing system Python or shell startup files. No administrator password, sudo, Homebrew or Xcode is required. Run with bash as above; do not disable Gatekeeper.

## Load the skill

Restart/reload skills in your agent or open a new conversation. If it cannot find the skill, give it the full installation path and ask it to read SKILL.md there.

Send:

> Use apple-watch-hypertension to check and set up Apple Watch hypertension notifications. First confirm you can execute commands locally on this Mac. If needed, I authorize temporary Hong Kong location over local USB CarKit. Ask for one human action at a time and wait. At the end confirm transmission has stopped, real location is restored, and notifications remain enabled. Installation success is not activation success.

The agent should inspect compatibility and existing settings first. If already enabled, no repeated location session is needed. A cloud container cannot access your USB merely because its interface runs on your Mac.

## WorkBuddy

1. Download **apple-watch-hypertension-workbuddy.zip** separately. Keep it zipped.
2. Open WorkBuddy skill management → Add/import skill ZIP (labels vary by version), select it and wait for it to appear.
3. Start a new conversation and ask the agent to check local Mac command access.
4. Importing the skill does not prepare dependencies. If the import directory is accessible, have the agent run `bash install.command --prepare` there.
5. Otherwise prepare the regular extracted ZIP with menu option **3**, keep that folder and provide its full path to the agent so it uses that SKILL.md and its scripts.
6. Cloud-only or script-restricted modes cannot directly automate this workflow. Use human-assisted execution or a local host.

The import format is adapted to official documentation; imports and hardware operations have not been tested across WorkBuddy versions.

## Doubao and DeepSeek

Their normal web/mobile chat should be treated as a guide unless a verified local Mac executor is connected. Uploading Markdown does not grant USB access. A person must run local commands and report sanitized results. This is an expert-assisted mode, not a complete standalone beginner walkthrough for chat-only products.

When DeepSeek is the model inside Claude Code or another local agent, install for that host. DeepSeek officially documents such integrations. Volcengine documents coding-tool integrations for its model services; that does not establish compatibility with the ordinary Doubao app. See [sources and the capability checklist](agents.md). Configure optional model accounts locally; never send API keys to chat. The USB tool itself needs no AI API key.

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
