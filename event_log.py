"""Журнал метаданных обращений и экспорт для анализа процесса."""

import csv
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from hash_chain import new_chain, verify

LOG_PATH = Path(__file__).with_name("events.jsonl")
FIELDS = ("case_id", "activity", "timestamp", "category", "action")
lock = Lock()


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def log_event(category, action, received_at):
    case_id = uuid4().hex
    rows = [
        dict(case_id=case_id, activity="получено", timestamp=received_at,
             category=category, action=""),
        dict(case_id=case_id, activity="обработано", timestamp=timestamp(),
             category=category, action=action),
    ]
    with lock:
        existing = _read_rows()
        if existing and not verify(existing):
            raise ValueError("Хэш-цепочка журнала повреждена")
        new_rows = new_chain(existing + rows)[-len(rows):]
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in new_rows))


def _read_rows():
    if not LOG_PATH.exists():
        return []
    return [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_rows():
    with lock:
        return _read_rows()


def get_report():
    completed = [row for row in read_rows() if row.get("activity", "обработано") == "обработано"]
    queue = [row for row in completed if row["action"] == "направил к человеку"]
    return {
        "total": len(completed),
        "human": len(queue),
        "categories": Counter(row["category"] for row in completed),
        "queue": queue,
    }


def export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(read_rows())
    return output.getvalue().encode("utf-8-sig")
