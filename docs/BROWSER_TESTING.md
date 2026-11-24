# Reproducing browser checks on Windows

These checks interact with the actual Docker app using an isolated headless Chrome
profile and a loopback-only DevTools port. They do not use the user's normal browser
profile. Application unit checks additionally use Streamlit AppTest.

Start the app with `docker compose up -d app`. Start an isolated browser:

```powershell
$browserArgs = @('--headless=new','--disable-gpu','--no-first-run',
  '--no-default-browser-check','--window-size=1440,1100',
  '--remote-debugging-address=127.0.0.1','--remote-debugging-port=9461',
  '--remote-allow-origins=http://127.0.0.1:9461',
  '--user-data-dir=D:\Projects\DellProject\artifacts\browser-profile',
  'http://127.0.0.1:8501')
Start-Process -FilePath 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  -ArgumentList $browserArgs -WindowStyle Hidden
```

Adapt executable/workspace paths if needed. Do not use a real personal profile.
Do not expose the debug port remotely. The test dependency `websocket-client` is
pinned in development requirements; Chrome is a host-only test prerequisite.

```powershell
.\.venv\Scripts\python.exe -u tests/browser_scenarios.py chat
.\.venv\Scripts\python.exe -u tests/browser_scenarios.py uploads
```

Chat checks exercise three routes, source panels, actual facts, history clearing,
and local-evidence mode. Upload checks temporarily add `Browser_Test_Guide.txt` and
`Browser_Test_Rules.pdf`, test corrupt/empty/oversized files, and save observations
and screenshots to ignored `artifacts/`. Remove only those two indexed test names
after verification; preserve the four included policies and unrelated user uploads.

`tests/browser_states.py` additionally expects explicitly created scratch runtime
containers on ports 8502 (blank key, demo data) and 8503 (blank key, empty stores).
They are not normal application services. The Phase 06 run created and removed
these scratch containers, leaving the main app on port 8501. Repeat that setup
before running the state-check script; never remove the app's named data volumes.

Helpers set a desktop viewport, require visible click targets, and wait for both
the expected response count and the absence of Streamlit's generation spinner.
This avoids mistaking transient stale elements during reruns for new responses.
Screenshots and DOM observations are agent browser evidence, not a human
faithfulness evaluation.
