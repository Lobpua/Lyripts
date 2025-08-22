import subprocess
import os
from typing import Dict


class ResolutionChanger:
    def __init__(self, settings) -> None:
        self.settings = settings
        base_path = (
            getattr(__import__("sys"), "frozen", False)
            and __import__("sys")._MEIPASS
            or os.path.dirname(os.path.abspath(__file__))
        )
        self.QRES_PATH = os.path.join(base_path, "QRes.exe")

    def _validate(self, res: Dict[str, str]) -> bool:
        return all(res.get(k) for k in ("width", "height", "refresh"))

    def _apply(self, res: Dict[str, str]) -> bool:
        if not os.path.exists(self.QRES_PATH):
            return False
        command = [
            self.QRES_PATH,
            f"/x:{res['width']}",
            f"/y:{res['height']}",
            f"/r:{res['refresh']}",
        ]
        try:
            subprocess.Popen(command, shell=False)
            return True
        except OSError:
            return False

    def set_desired(self) -> bool:
        res = self.settings.data.get("desired_resolution", {})
        if not self._validate(res):
            return False
        return self._apply(res)

    def restore_original(self) -> bool:
        res = self.settings.data.get("original_resolution", {})
        if not self._validate(res):
            return False
        return self._apply(res)

