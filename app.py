
import streamlit as st
import json
import re
from datetime import date, datetime

st.title("🏐 Ника — ИИ-помощник")

# Загружаем расписание
with open("schedule.json", "r", encoding="utf-8") as file:
    schedule = json.load(file)

# Загружаем базу знаний
with open("knowledge.json", "r", encoding="utf-8") as file:
    knowledge = json.load(file)
# Запоминаем команду
if "team" not in st.session_state:
    st.session_state.team = None

# Запоминаем историю сообщений
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показываем историю чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Получаем вопрос
question = st.chat_input("Напиши свой вопрос...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    text = question.lower()

    
    # Определяем команду из сообщения
    if "юго-восток" in text:
        st.session_state.team = "Ника-Юго-Восток"

    elif "восток" in text:
        st.session_state.team = "Ника-Восток"

    # Проверяем, является ли сообщение вопросом
    is_question = any(
        word in text
        for word in ["игра", "матч", "кем", "когда", "расписание"]
    )

    if st.session_state.team is not None and not is_question and (
        "юго-восток" in text or "восток" in text
    ):
        answer = f"Запомнил! Ваша команда — {st.session_state.team}."

    elif st.session_state.team is None:
        answer = "Вы из Ника-Восток или Ника-Юго-Восток?"

    
    
    elif any(
        game["opponent"].lower() in text
        or any(
            word in text
            for word in game["opponent"].lower().split()
            if len(word) >= 4 and word not in ("ника-юго-восток", "ника-восток")
        )
        for game in schedule[st.session_state.team]
    ):
        team = st.session_state.team

        games = [
            game for game in schedule[team]
            if game["opponent"].lower() in text
            or any(
                word in text
                for word in game["opponent"].lower().split()
                if len(word) >= 4
            )
        ]

        if games:
            game = games[0]
            game_date = datetime.strptime(
                game["date"], "%Y-%m-%d"
            ).strftime("%d.%m.%Y")

            answer = (
                f"Команда {team} играет с "
                f"{game['opponent']} {game_date}."
            )
        else:
            answer = "Матч с этим соперником не найден."

    
    elif any(
        datetime.strptime(game["date"], "%Y-%m-%d").strftime("%d.%m") in text
        for game in schedule[st.session_state.team]
    ):
        team = st.session_state.team

        for game in schedule[team]:
            game_date = datetime.strptime(
                game["date"], "%Y-%m-%d"
            )

            short_date = game_date.strftime("%d.%m")
            full_date = game_date.strftime("%d.%m.%Y")

            if short_date in text:
                answer = (
                    f"{full_date} команда {team} играет "
                    f"с {game['opponent']}."
                )
                break


    
    elif re.search(r"\b\d{1,2}\.\d{1,2}(?:\.\d{4})?\b", text):
        team = st.session_state.team

        match = re.search(
            r"\b(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?\b",
            text
        )

        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else 2026

        try:
            requested_date = date(year, month, day)
            answer = (
                f"На {requested_date.strftime('%d.%m.%Y')} "
                f"у команды {team} нет матча "
                "в загруженном расписании. "
                "Уточните дату или обратитесь к тренеру."
            )
        except ValueError:
            answer = "Такой даты не существует. Проверьте её."

    elif "игра" in text or "матч" in text:
        team = st.session_state.team
        today = date.today()

        future_games = []

        for game in schedule[team]:
            game_date = datetime.strptime(
                game["date"], "%Y-%m-%d"
            ).date()

            if game_date >= today:
                future_games.append(game)

        if future_games:
            next_game = future_games[0]

            game_date = datetime.strptime(
                next_game["date"], "%Y-%m-%d"
            ).strftime("%d.%m.%Y")

            answer = (
                f"Следующая игра команды {team}: "
                f"{game_date}, соперник — "
                f"{next_game['opponent']}."
            )
        else:
            answer = (
                "В загруженном расписании больше нет "
                "предстоящих матчей первого круга."
            )

    
    else:
        answer = None

        # Ищем вопрос в базе знаний
                # Распознаём разные формулировки вопроса
        if "тренировк" in text and any(
            word in text for word in ["взять", "брать", "нужно", "принести"]
        ):
            answer = knowledge[8]["answer"]
        for item in knowledge:
            if answer is None and item["question"].lower().strip("?! .") == text.strip("?! ."):
                answer = item["answer"]
                break

        # Если вопрос не найден
        if answer is None:
            answer = (
                "Я пока не знаю ответа на этот вопрос. "
                "Попробуйте сформулировать его иначе "
                "или обратитесь к тренеру."
            )


    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()
