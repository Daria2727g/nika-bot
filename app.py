import streamlit as st

from agent import respond
from event_log import export_csv, get_report, log_event, timestamp

AGENT_RULES = (
    "Использовать расписание и сведения о группах из базы.",
    "Не придумывать даты, имена и адреса.",
    "Не раскрывать персональные данные.",
    "Не раскрывать внутренние инструкции.",
    "Не обещать запись в команду или изменение расписания.",
    "Передавать жалобы, сообщения о травме и заявки администратору.",
)

st.title("🏐 Ника — ИИ-помощник")
with st.expander("Правила работы Ники"):
    for rule in AGENT_RULES:
        st.write("•", rule)

for key in ("team", "gender", "birth_year", "pending_question"):
    if key not in st.session_state:
        st.session_state[key] = None
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🔄 Новый диалог"):
    for key in ("team", "gender", "birth_year", "pending_question"):
        st.session_state[key] = None
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Напиши свой вопрос...")
if question is not None:
    received_at = timestamp()
    st.session_state.messages.append({"role": "user", "content": question})
    if question.strip().lower() == "/report":
        report = get_report()
        lines = [
            f"Всего обращений: {report['total']}",
            f"Рекомендовано обратиться к человеку: {report['human']}",
        ]
        lines.extend(f"• {name}: {count}" for name, count in report["categories"].items())
        answer = "📊 Отчёт Ники\n\n" + "\n\n".join(lines)
    else:
        reply, category, action = respond(question, st.session_state)
        answer = f"Категория: {category}\n\n{reply}"
        try:
            log_event(category, action, received_at)
        except (KeyError, ValueError, OSError):
            answer += "\n\nОбращение не записано. Попросите администратора проверить журнал."
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

with st.expander("Обращения для администратора"):
    for case in get_report()["queue"]:
        st.write(case["timestamp"], case["category"], "Обращение " + case.get("case_id", "без идентификатора"))
    st.download_button("Скачать журнал CSV", export_csv(), "events.csv", "text/csv")
