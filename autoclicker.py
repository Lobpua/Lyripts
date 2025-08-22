import threading
import time
from typing import Optional
from pynput.mouse import Button, Controller as MouseController, Listener


class AutoClicker:
    BUTTON_MAP = {"ЛКМ": Button.left, "ПКМ": Button.right, "СКМ": Button.middle}
    TRIGGER_MAP = {
        "mouse1": Button.left,
        "mouse2": Button.right,
        "mouse3": Button.middle,
        "mouse4": Button.x1,
        "mouse5": Button.x2,
    }

    def __init__(self, settings) -> None:
        self.settings = settings
        self.mouse_controller = MouseController()
        self._clicking = False
        self._stop_evt = threading.Event()
        self.listener: Optional[Listener] = None
        self.thread: Optional[threading.Thread] = None

    def _click_loop(self) -> None:
        btn = self.BUTTON_MAP.get(self.settings.data.get("spam_button"), Button.left)
        interval = self.settings.get_click_interval()
        while not self._stop_evt.is_set():
            if self._clicking:
                self.mouse_controller.click(btn)
            time.sleep(interval)

    def _ensure_thread(self) -> None:
        if not self.thread or not self.thread.is_alive():
            self._stop_evt.clear()
            self.thread = threading.Thread(target=self._click_loop, daemon=True)
            self.thread.start()

    def on_click(self, x, y, button, pressed):
        trigger_btn = self.TRIGGER_MAP.get(
            self.settings.data.get("trigger_button"), Button.x1
        )
        if button == trigger_btn:
            if pressed:
                self._clicking = True
                self._ensure_thread()
            else:
                self._clicking = False

    def toggle(self) -> None:
        if self.listener and self.listener.running:
            self.stop()
        else:
            self.listener = Listener(on_click=self.on_click)
            self.listener.start()
            self._ensure_thread()

    def stop(self) -> None:
        self._clicking = False
        if self.listener and self.listener.running:
            self.listener.stop()
        self.listener = None
        self._stop_evt.set()

    def is_active(self) -> bool:
        return bool(self.listener and self.listener.running)

