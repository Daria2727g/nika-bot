def classify_message(text):
    text = text.lower()
        # Сначала проверяем обращения, требующие помощи человека
    if any(word in text for word in [
        "жалоб", "конфликт", "травм",
        "боль", "опасност", "перевестись","пожаловаться",
        "записаться", "связаться с тренером"
    ]):
        return "передача человеку"

    if "игра" in text or "матч" in text or "соревнован" in text:
        return "соревнования"

    if "тренировк" in text:
        return "тренировки"

    if "тренер" in text:
        return "тренеры"

    if "адрес" in text or "зал" in text:
        return "адреса"

    return "иные вопросы"

if __name__ == "__main__":
    # Проверяем работу классификатора
    print(classify_message("Когда следующая игра?"))
    print(classify_message("Что взять на тренировку?"))
    print(classify_message("Кто мой тренер?"))
    print(classify_message("Какой адрес зала?"))
    print(classify_message("Что подарить команде?"))
    print(classify_message("Хочу пожаловаться на тренера"))
