# prev_hash - хэш предыдущей записи
# hash - хэш текущей записи
# verify - проверка на соответствие хэшей

import hashlib
import json


def get_hash_chain(prev_hash, event_data):
    text = json.dumps(event_data, ensure_ascii=False, sort_keys=True)
    combined = prev_hash + text
    combined_bytes = combined.encode("utf-8")
    result = hashlib.sha256(combined_bytes).hexdigest()
    return result

def new_chain(events):
    prev_hash = '0'
    for event in events:
        event['prev_hash'] = prev_hash
        event_copy = event.copy()
        event_copy.pop("hash", None)
        new_hash = get_hash_chain(prev_hash, event_copy)
        event['hash'] = new_hash
        prev_hash = new_hash 
    return events

def verify(events):
    prev_hash = '0'
    for event in events:
        if event["prev_hash"] != prev_hash:
            return False
        event_copy = event.copy()
        event_copy.pop("hash", None)
        calc_hash = get_hash_chain(prev_hash, event_copy)
        if calc_hash != event["hash"]:
            return False
        prev_hash = event["hash"]
    return True

if __name__ == "__main__":
    test_events = [
        {"category": "тренировки", "action": "ответ"},
        {"category": "соревнования", "action": "ответ"}
    ]
    print(new_chain(test_events))
    print(new_chain(test_events))
    print("Проверка цепочки:", verify(test_events))
    test_events[0]["category"] = "адреса"
    print("После изменения:", verify(test_events))
