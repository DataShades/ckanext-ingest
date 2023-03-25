from __future__ import annotations

import enum
import json
import tempfile
from typing import Any


def make_artifacts(report: str) -> Artifacts:
    return Type[report].value()


class Artifacts:
    def fail(self, data):
        pass

    def success(self, data):
        pass

    def collect(self):
        pass


class DetailedArtifacts(Artifacts):
    collection: list[dict[str, Any]]

    def __init__(self):
        self.collection = []

    def fail(self, data):
        rec = {"success": False}
        rec.update(data)
        self.collection.append(rec)

    def success(self, data):
        rec = {"success": True}
        rec.update(data)
        self.collection.append(rec)

    def collect(self):
        return self.collection


class TmpArtifacts(Artifacts):
    def __init__(self):
        self.output = tempfile.NamedTemporaryFile("w", delete=False)

    def fail(self, data):
        rec = {"success": False}
        rec.update(data)
        self.output.write(json.dumps(rec) + "\n")

    def success(self, data):
        rec = {"success": True}
        rec.update(data)
        self.output.write(json.dumps(rec) + "\n")

    def collect(self):
        self.output.close()
        return {"report_path": self.output.name}


class StatArtifacts(Artifacts):
    succeed: int = 0
    failed: int = 0

    def fail(self, data):
        self.failed += 1

    def success(self, data):
        self.succeed += 1

    def collect(self):
        return {
            "fail": self.failed,
            "success": self.succeed,
        }


class Type(enum.Enum):
    stats = StatArtifacts
    details = DetailedArtifacts
    tmp = TmpArtifacts
