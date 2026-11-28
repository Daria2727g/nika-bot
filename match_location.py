import re
from datetime import datetime


def match_location_answer(question, team, schedule, teams_data):
    """Ответ на вопрос о месте матча; None, если вопрос не об этом."""
    text = question.lower().replace("ё", "е")
    location_words = ("где", "адрес", "место", "в каком зале", "куда ехать", "на каком поле")
    game_words = ("игр", "матч", "соревнован")
    has_date = bool(re.search(r"(?<!\d)\d{1,2}[./]\d{1,2}(?!\d)", text))
    if not (any(w in text for w in location_words) and (any(w in text for w in game_words) or has_date)):
        return None
    if not team:
        return "Уточните команду: Ника-Восток или Ника-Юго-Восток."

    games = schedule.get(team, [])
    date_match = re.search(r"(?<!\d)(\d{1,2})[./](\d{1,2})(?:[./](\d{4}))?(?!\d)", text)
    if date_match:
        day, month = map(int, date_match.group(1, 2))
        year = int(date_match.group(3) or 2026)
        try:
            date_key = datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return "Такой даты не существует. Проверьте дату."
        games = [g for g in games if g["date"] == date_key]
    else:
        # Без даты ищем упомянутого соперника.
        normalized = lambda s: re.sub(r"[^а-яa-z0-9]+", "", s.lower().replace("ё", "е"))
        games = [g for g in games if normalized(g["opponent"]) in normalized(text)]
        if not games:
            return "Укажите дату матча, например: где играем 29.11?"

    if not games:
        return f"На указанную дату у команды {team} нет матча в расписании."
    if len(games) > 1:
        return "Найдено несколько матчей. Уточните дату."

    game = games[0]
    host = game.get("home_team")
    if not host:
        return "Хозяин матча не указан в расписании. Уточните место у тренера."

    # В базе команд Ники используются пробелы, в расписании — дефисы.
    aliases = {"Ника-Восток": "Ника Восток", "Ника-Юго-Восток": "Ника Юго-Восток"}
    venue = teams_data.get("venues", {}).get(aliases.get(host, host))
    if not venue:
        return f"Хозяин матча — {host}, но зал не указан. Уточните адрес у тренера."
    address = teams_data.get("venue_addresses", {}).get(venue)
    if not address:
        return f"Хозяин матча — {host}. Зал: {venue}. Адрес пока не указан."

    display_date = datetime.strptime(game["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
    return (f"{display_date} команда {team} играет с {game['opponent']}. "
            f"Хозяин матча — {host}. Место: {venue}, {address}.")
