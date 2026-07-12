import json
import os
import tempfile
import time
from pathlib import Path

class SpawnRegistry:

    def __init__(self, json_path=None):
        if json_path is None:
            json_path = Path(__file__).resolve().parent / "spawned_objects.json"

        self._json_path = Path(json_path)

        self._json_path.parent.mkdir(parents=True, exist_ok=True)

        if not self._json_path.exists():
            self._write({})
            
    def _read(self):
        try:
            with open(self._json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write(self, data):
        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            dir=self._json_path.parent,
            encoding="utf-8",
        ) as tmp:
            json.dump(data, tmp, indent=4)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name

        os.replace(tmp_name, self._json_path)

    def add(self, obj, spawn_time=None):
        if spawn_time is None:
            spawn_time = time.time()

        data = self._read()

        data[obj.name] = {
            "model": obj.model,
            "spawn_time": spawn_time,
        }

        self._write(data)

    def remove(self, name):
        data = self._read()

        if name in data:
            del data[name]
            self._write(data)

    def get_all(self):
        return self._read()

    def clear(self):
        self._write({})

    def cleanup(self, lifetime):
        now = time.time()

        data = self._read()

        changed = False

        for name in list(data.keys()):
            if now - data[name]["spawn_time"] > lifetime:
                del data[name]
                changed = True

        if changed:
            self._write(data)