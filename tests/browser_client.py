"""Host browser inspection via local Chrome DevTools; not part of runtime code.

Connect only to an isolated headless browser started for this project on port 9461.
"""
import argparse
import base64
import json
import time
from pathlib import Path
from urllib.request import urlopen
import websocket


class Browser:
    def __init__(self):
        with urlopen("http://127.0.0.1:9461/json", timeout=3) as response:
            pages = json.load(response)
        page = next(item for item in pages if item["type"] == "page")
        self.connection = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30,
                                                      origin="http://127.0.0.1:9461")
        self.serial = 0
        self.call("Emulation.setDeviceMetricsOverride", width=1440, height=1100, deviceScaleFactor=1, mobile=False)

    def call(self, method, **params):
        self.serial += 1
        serial = self.serial
        self.connection.send(json.dumps({"id": serial, "method": method, "params": params}))
        while True:
            reply = json.loads(self.connection.recv())
            if reply.get("id") == serial:
                if "error" in reply:
                    raise RuntimeError(reply["error"]["message"])
                return reply.get("result", {})

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if result.get("exceptionDetails"):
            raise RuntimeError("Browser JavaScript failed")
        return result.get("result", {}).get("value")

    def screenshot(self, path):
        self.call("Emulation.setDeviceMetricsOverride", width=1440, height=1100, deviceScaleFactor=1, mobile=False)
        reply = self.call("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        Path(path).write_bytes(base64.b64decode(reply["data"]))

    def upload(self, path):
        root = self.call("DOM.getDocument")["root"]["nodeId"]
        node = self.call("DOM.querySelector", nodeId=root, selector='input[type="file"]')["nodeId"]
        self.call("DOM.setFileInputFiles", nodeId=node, files=[str(Path(path).resolve())])

    def click(self, expression):
        box = self.evaluate(f"(()=>{{const e=({expression});e.scrollIntoView({{block:'center'}});const r=e.getBoundingClientRect();return {{x:r.x+r.width/2,y:r.y+r.height/2}};}})()")
        if not 0 <= box["x"] <= 1440 or not 0 <= box["y"] <= 1100:
            raise RuntimeError("Target element is not visible in the browser viewport")
        self.call("Input.dispatchMouseEvent", type="mousePressed", button="left", clickCount=1, **box)
        self.call("Input.dispatchMouseEvent", type="mouseReleased", button="left", clickCount=1, **box)

    def press(self, key, code=None, virtual=0):
        self.call("Input.dispatchKeyEvent", type="keyDown", key=key, code=code or key,
                  windowsVirtualKeyCode=virtual, nativeVirtualKeyCode=virtual)
        self.call("Input.dispatchKeyEvent", type="keyUp", key=key, code=code or key,
                  windowsVirtualKeyCode=virtual, nativeVirtualKeyCode=virtual)

    def wait(self, expression, timeout=120):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.evaluate(expression):
                return
            time.sleep(.25)
        raise TimeoutError("Expected browser state did not appear")

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression", default="document.body.innerText")
    parser.add_argument("--screenshot")
    parser.add_argument("--upload")
    args = parser.parse_args()
    browser = Browser()
    try:
        if args.upload:
            browser.upload(args.upload)
        print(json.dumps(browser.evaluate(args.expression), ensure_ascii=True))
        if args.screenshot:
            browser.screenshot(args.screenshot)
    finally:
        browser.close()
