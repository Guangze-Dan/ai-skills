---
name: lightpanda
description: Lightweight headless browser for AI agents (Lightpanda 1.0.0), running inside WSL2 on this machine and reachable from Windows via CDP at http://127.0.0.1:9222. Use when you need to read, render, crawl or screenshot web pages cheaply — about 10x lighter and much faster to start than Chrome — without needing the full browser-use plugin. Covers starting/stopping the server, health checks, CDP connections (Playwright/Puppeteer/raw WebSocket), and troubleshooting the WSL setup. Not for JS-heavy SPA interaction that requires full Chrome fidelity — use the browser-use plugin instead.
metadata:
  version: 1.0.0
  binary: D:\AgentSkills\sources\lightpanda\lightpanda-1.0.0-x86_64-linux
  distro: Ubuntu-24.04
  cdp: http://127.0.0.1:9222
---

# Lightpanda — lightweight headless browser (CDP on 127.0.0.1:9222)

Lightpanda is a headless browser built for AI agents: fast startup, ~1/10 the
memory of Chrome, speaks the Chrome DevTools Protocol (CDP). On this Windows
machine it has no native build, so it runs inside WSL2 (distro `Ubuntu-24.04`,
binary at `/usr/local/lightpanda/lightpanda`); WSL2 localhost forwarding makes
it reachable from Windows at `http://127.0.0.1:9222`.

## Quick check — is it up?

```cmd
curl http://127.0.0.1:9222/json/version
```

A JSON response with `"Browser": "Lightpanda/..."` means it is ready. If it
refuses to connect, start it (next section).

## Start / stop

```cmd
D:\AgentSkills\skills\lightpanda\scripts\lightpanda-start.cmd
D:\AgentSkills\skills\lightpanda\scripts\lightpanda-stop.cmd
```

`lightpanda-start.cmd` is idempotent: it exits 0 immediately if CDP already
answers on 9222, otherwise it launches the server detached inside WSL and
waits until `/json/version` responds (up to ~15 s). Server log lives at
`/var/log/lightpanda.log` inside the distro
(`wsl -d Ubuntu-24.04 -u root -- cat /var/log/lightpanda.log`).

## Using it (CDP)

Anything that speaks CDP works. Easiest from Node with playwright-core:

```js
import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = await browser.newPage();
await page.goto('https://example.com');
console.log(await page.title(), (await page.content()).length);
await browser.close();
```

Raw HTTP surface (no client lib needed): `GET /json/version`, `GET /json/list`
(list targets), plus the WebSocket endpoint per target for
`Page.navigate` / `Runtime.evaluate` / `DOM.getDocument` etc.

Typical agent recipe for a cheap read:
1. `lightpanda-start.cmd` (skip if `/json/version` already answers)
2. connect over CDP, navigate, pull `page.content()` or a screenshot
3. disconnect (the server stays up for the next request)

## First-time setup (normally already done)

If `wsl -d Ubuntu-24.04 --exec true` fails:

1. `scripts\admin-setup-wsl.cmd` — run **elevated** (one UAC click): enables
   the `VirtualMachinePlatform` / `Microsoft-Windows-Subsystem-Linux` Windows
   features and installs the WSL 3.0.1 MSI from
   `D:\AgentSkills\sources\wsl\`. Logs to `D:\AgentSkills\logs\admin-setup-wsl.log`.
   If the features were not enabled before, a **reboot is required** once.
2. After the reboot: `scripts\setup-distro.cmd` — run it normally first; if
   Windows reports elevation is required, rerun it as administrator (whether
   a distro install needs elevation depends on the WSL version). It registers
   Ubuntu-24.04 (`wsl --install Ubuntu-24.04 --web-download --no-launch`),
   copies the lightpanda binary from `D:\AgentSkills\sources\lightpanda\`
   into the distro, installs any missing shared libraries, and self-tests
   CDP from Windows. Logs to `D:\AgentSkills\logs\setup-distro.log`.

## Notes and limits

- Lightpanda aims for "good enough to read the web", not pixel-perfect Chrome:
  some heavy-JS sites render incompletely. For those, fall back to the
  browser-use plugin or Jina Reader (`curl https://r.jina.ai/<url>`).
- The WSL VM shuts down when the last process inside it exits (default idle
  timeout ~60 s), which also stops the server — just run the start script
  again; it reconnects in about a second.
- Upgrade path: replace the binary in `D:\AgentSkills\sources\lightpanda\`
  and rerun `scripts\setup-distro.cmd`.
