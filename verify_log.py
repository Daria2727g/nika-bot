"""Команда для запуска существующей проверки журнала Ники."""
import argparse
import json
from pathlib import Path

from hash_chain import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path,
                        default=Path(__file__).with_name("events.jsonl"))
    args = parser.parse_args()
    events = []
    try:
        with args.path.open(encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    events.append(json.loads(line))
                    valid = verify(events)
                except (ValueError, KeyError, TypeError):
                    valid = False
                if not valid:
                    print(f"Ошибка целостности в строке {number}.")
                    return 1
    except OSError as error:
        print(f"Не удалось открыть журнал: {error}")
        return 1
    print(f"Журнал прошёл проверку. Записей: {len(events)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
