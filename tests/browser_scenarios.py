"""Real host Chrome interaction checks against the Docker UI; run explicitly."""
import argparse
import json
from pathlib import Path
import time
from browser_client import Browser

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"


def select_student(browser, student):
    if browser.evaluate("Boolean(document.querySelector('button[aria-label=\"Expand sidebar\"]'))"):
        browser.click("document.querySelector('button[aria-label=\"Expand sidebar\"]')")
    browser.wait("document.querySelector('[data-testid=stSidebar]').getBoundingClientRect().x>=0", 10)
    browser.press("Escape", "Escape", 27)
    browser.click("document.querySelector('input[role=combobox]')")
    browser.evaluate("document.querySelector('input[role=combobox]').select()")
    browser.call("Input.insertText", text=student)
    target = "Array.from(document.querySelectorAll('[role=option]')).find(e=>e.textContent.includes(" + json.dumps(student) + "))"
    browser.wait(f"Boolean({target})", 10)
    browser.click(target)
    time.sleep(.5)


def ask(browser, question, expected_count):
    browser.click("document.querySelector('textarea[data-testid=stChatInputTextArea]')")
    browser.call("Input.insertText", text=question)
    browser.press("Enter", "Enter", 13)
    complete = "document.querySelectorAll('[data-testid=stSpinner]').length===0 && (document.body.innerText.match(/Response time:/g)||[]).length===" + str(expected_count)
    browser.wait(complete)
    time.sleep(.5)
    browser.wait(complete)
    browser.evaluate("document.querySelectorAll('details:not([open]) > summary').forEach(e=>e.click())")
    return browser.evaluate("document.body.innerText")


def chats(browser):
    select_student(browser, "S-012")
    browser.click("Array.from(document.querySelectorAll('button')).find(e=>e.innerText==='Clear conversation')")
    browser.wait("document.querySelectorAll('[data-testid=stChatMessage]').length===0", 15)
    cases = [("structured", "What is my GPA and fee status?", "STRUCTURED", "8.4"),
             ("attendance", "What is the minimum attendance?", "UNSTRUCTURED", "75"),
             ("hybrid", "Am I eligible for a merit scholarship and what is the deadline?", "HYBRID", "Scholarship_Policy.pdf")]
    for count, (name, question, route, fact) in enumerate(cases, 1):
        body = ask(browser, question, count)
        assert route in body and fact in body
        ARTIFACTS.joinpath(f"phase06-browser-{name}.txt").write_text(body, encoding="utf-8")
        browser.evaluate("Array.from(document.querySelectorAll('[data-testid=stChatMessage]')).at(-1).scrollIntoView({block:'start'})")
        browser.screenshot(ARTIFACTS / f"phase06-browser-{name}.png")
        print(json.dumps({"case": name, "route_observed": route, "fact_observed": fact,
                          "fallback_notice_present": "Showing original evidence" in body}), flush=True)
    select_student(browser, "S-001")
    browser.wait("document.querySelectorAll('[data-testid=stChatMessage]').length===0", 10)
    browser.click("document.querySelector('input[type=checkbox]')")
    browser.wait("document.body.innerText.includes('Evidence only')", 10)
    body = ask(browser, "What is my GPA?", 1)
    assert "8.0" in body and "Showing original evidence" in body
    print("Student change cleared history; local-evidence mode returned GPA 8.0.", flush=True)


def uploads(browser):
    if browser.evaluate("Boolean(document.querySelector('button[aria-label=\"Expand sidebar\"]'))"):
        browser.click("document.querySelector('button[aria-label=\"Expand sidebar\"]')")
    browser.wait("document.querySelector('[data-testid=stSidebar]').getBoundingClientRect().x>=0", 10)
    fixture_dir = ARTIFACTS / "browser-uploads"
    fixture_dir.mkdir(exist_ok=True)
    files = {"Browser_Test_Guide.txt": b"SYNTHETIC - DEMO ONLY. The test library lends four books for seven days.",
             "Browser_Test_Rules.pdf": (ARTIFACTS.parent / "data/raw_docs/Academic_Regulations.pdf").read_bytes(),
             "Corrupt_Example.pdf": b"not a valid PDF file", "Empty_Example.txt": b""}
    for name, content in files.items():
        path = fixture_dir / name
        path.write_bytes(content)
        browser.upload(path)
        time.sleep(1)
        button = "Array.from(document.querySelectorAll('button')).find(e=>e.innerText==='Index document')"
        browser.wait(f"({button}) && !({button}).disabled", 10)
        browser.click(button)
        needle = f"Indexed {name}" if name.startswith("Browser") else "Cannot read document" if name.endswith(".pdf") else "Upload a nonempty document"
        browser.wait("document.body.innerText.includes(" + json.dumps(needle) + ")", 60)
        body = browser.evaluate("document.body.innerText")
        ARTIFACTS.joinpath(f"phase06-upload-{name}.txt").write_text(body, encoding="utf-8")
        print(name, "observed:", needle, flush=True)
    oversized = fixture_dir / "Oversized_Example.txt"
    with oversized.open("wb") as file:
        file.truncate(20 * 1024 * 1024 + 1)
    browser.upload(oversized)
    time.sleep(1)
    body = browser.evaluate("document.body.innerText")
    assert "File must be 20.0MB or smaller" in body
    ARTIFACTS.joinpath("phase06-upload-oversized.txt").write_text(body, encoding="utf-8")
    print("Oversized file rejected by the 20 MB widget limit.", flush=True)
    browser.screenshot(ARTIFACTS / "phase06-upload-errors.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=["chat", "uploads"])
    args = parser.parse_args()
    browser = Browser()
    try:
        chats(browser) if args.scenario == "chat" else uploads(browser)
    finally:
        browser.close()
