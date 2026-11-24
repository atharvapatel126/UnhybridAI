"""Browser checks for missing credentials, empty stores, and missing selection."""
from pathlib import Path
from browser_client import Browser
from browser_scenarios import ask, select_student

directory = Path(__file__).resolve().parents[1] / "artifacts"
browser = Browser()
try:
    browser.call("Page.navigate", url="http://127.0.0.1:8502")
    browser.wait("location.port==='8502' && document.body.innerText.includes('Gemini key not configured') && document.body.innerText.includes('Evidence only') && Boolean(document.querySelector('textarea[data-testid=stChatInputTextArea]'))", 30)
    assert "Evidence only" in browser.evaluate("document.body.innerText")
    select_student(browser, "S-012")
    body = ask(browser, "What is my GPA?", 1)
    assert "8.4" in body and "Showing original evidence" in body
    directory.joinpath("phase06-no-key.txt").write_text(body, encoding="utf-8")
    browser.screenshot(directory / "phase06-no-key.png")
    print("No-key browser: banner, default local mode, and real GPA query passed.", flush=True)

    browser.call("Page.navigate", url="http://127.0.0.1:8503")
    browser.wait("location.port==='8503' && document.body.innerText.includes('Student database unavailable') && Boolean(document.querySelector('textarea[data-testid=stChatInputTextArea]'))", 30)
    body = ask(browser, "What is the minimum attendance?", 1)
    assert "No documents are available" in body and "No supporting evidence" in body
    directory.joinpath("phase06-empty-state.txt").write_text(body, encoding="utf-8")
    browser.screenshot(directory / "phase06-empty-state.png")
    print("Empty database/vector browser: readable warnings; no guessed answer.", flush=True)

    browser.call("Page.navigate", url="http://127.0.0.1:8501")
    browser.wait("location.port==='8501' && Boolean(document.querySelector('textarea[data-testid=stChatInputTextArea]'))", 30)
    if not browser.evaluate("document.querySelector('input[type=checkbox]').checked"):
        browser.click("document.querySelector('input[type=checkbox]')")
        browser.wait("document.body.innerText.includes('Evidence only')", 10)
    body = ask(browser, "What is my GPA?", 1)
    assert "Select a synthetic student" in body and "No supporting evidence" in body
    directory.joinpath("phase06-no-student.txt").write_text(body, encoding="utf-8")
    print("No selected student: explicit selection warning and no guessed GPA.", flush=True)
finally:
    browser.close()
