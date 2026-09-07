# Ready Timer

A backwards-planned routine timer for ADHD time blindness. Single-file web app — no build, no dependencies, no account. Works in Safari on iPhone/iPad and Chrome/Safari/Edge on Mac. Can be installed to the Home Screen / Dock like a native app.

## The idea

You set a **goal time** (e.g. 8:30 — out the door) and list the activities that get you there with how long each takes. The app calculates **backwards** from the goal and shows exactly when each activity should start and end. While running, it pulls you back from distraction with:

- a **sound + flash + full-screen alert** at the start of each activity and at **25% / 50% / 75%** through it
- a **spoken voice alert** (Siri-style voice) saying what's happening and how long is left
- **huge text** on screen: current activity, % through it, time remaining, and time to goal

## Run screen

```
GOAL 8:30 AM                    42:18 to goal
this pace: 8:34 AM (4:12 late)          ← updates live

WAKE UP & OUT OF BED            ← current activity, huge
0:42                            ← remaining, huge (amber < 1 min, red when over)
37% through "Wake up…"

[✓ DONE] [⏸ PAUSE] [+5 min on goal]
[↶ Redo activity] [■ End routine]

Activity        Start     End       State
Wake up…        7:27 AM   7:37 AM   ▶ NOW
Shower          7:37 AM   7:52 AM   …
```

## Key behaviours

- **Pause** freezes everything; on resume the *whole schedule slides later* by the pause duration. The **original goal time stays on screen** as the target, with a live banner: "⚠ 4:12 behind original goal — finish an activity early to catch up."
- **Finishing an activity early** pulls every later activity (and the goal) earlier again — that's how you catch up after pausing or dawdling. The banner flips to "✓ ahead of original goal."
- **Finishing is always explicit.** When an activity's time runs out the app does **not** move on: the activity stays current, the countdown goes into red overtime (`+2 mins & 10 secs`), a full-screen "WRAP UP" alert fires (then a reminder every 30 s) until she taps ✓ DONE. All later activities and the finish time slide in real time — "this pace: 8:41 AM (11:12 late)" — so the cost of dawdling is always visible.
- **+5 min on goal** deliberately moves the goal for a morning that's just not happening.
- **Redo activity** restarts the current one with a full duration and clears its fired alerts.
- Screen-title shows the current activity's end time, so it's visible at a glance in tabOverview/switcher.
- The run **survives a page reload** (all scheduling is absolute wall-clock time).
- Keep-screen-on: the app holds a **Screen Wake Lock** and additionally plays a hidden 1-px silent looping video — the video is the reliable path on iOS, where the Wake Lock API is flaky (silently ignored in Low Power Mode). Both start on Start and stop when the routine ends. Still not bulletproof: locking the phone manually or force-quitting always wins, and a locked phone can't play the alerts (web apps get no background audio on iOS).
- Everything persists in `localStorage`.

## Alerts & voice on iOS

- Sound plays at **media volume** (turn it up with the volume buttons while the app is open) — the ringer switch does not mute web apps.
- Voice uses the on-device Safari speech engine. The app **auto-picks the best installed voice** (Premium > Enhanced > everything else) and there's a **Voice picker + ▶ preview** in settings. The robotic default = Apple's "compact" voices; the fix is free: **Settings → Accessibility → Spoken Content → Voices → English**, download an **Enhanced** or **Premium** voice (e.g. Karen Enhanced for en-AU), then reopen the app and pick it. Per device — do it on the phone and the Mac separately.
- Alerts also flash the whole screen and vibrate (where supported).
- Install it: Safari → Share → **Add to Home Screen**. It then runs full-screen like an app.

### Troubleshooting: the home-screen icon is just a bookmark

A Home-Screen icon that opens the server URL instead of the app means the service
worker never registered — **offline install requires a secure context**
(`https://…` or `http://localhost`). Plain `http://192.168.1.136:…` silently
degrades to a bookmark. The app now detects this and shows a ⚠ note on the plan
screen. Fix: serve over HTTPS (GitHub Pages, Let's Encrypt on the host, or a
self-signed cert + trust profile), or on the host machine use
`http://localhost:8123`. Then open the page, confirm the note says
"✓ Offline ready", and redo Add to Home Screen.

## DEMO mode

Removed (was a 20×-speed test button). For testing, temporarily shrink the activity durations instead.

## Run it

```bash
cd ~/projects/ready-timer
python3 -m http.server 8123
# open http://<this-machine's-LAN-IP>:8123 on the iPhone/Mac
```

Any static server works. **The server is only the install/update doorway** — once a device has the app (Home Screen install, or a downloaded `index.html`), the timer runs fully offline with no server. Start the server again whenever you want to install on a new device or push app updates.

Files:

- `index.html` — the entire app (HTML+CSS+JS)
- `manifest.json`, `sw.js`, `icons/` — installability (offline cache, icon)
- `qa/cdp.py` + `qa/shots/` — CDP test driver and QA screenshots

## QA log (verified by automated browser tests, Sep 2026)

- Plan view: backwards schedule preview correct (08:30 goal − 60 min → 7:30 start), >2h-away goal guard works
- Alerts: 25/50/75% overlays fired at exactly the right times in a timed 60× demo run
- Auto-advance when an activity runs over (incl. multi-activity catch-up after sleep)
- Pause → resume: goal slid by exactly the pause duration (45.6 s), original goal kept visible
- Early finish: goal pulled earlier, banner flipped ahead/behind correctly
- Redo activity: restarts at 0%, clears fired alerts
- Late start: anchors to now, announces the late pace
- Reload mid-run: restores the exact same schedule and progress
- Zero JS errors across all runs