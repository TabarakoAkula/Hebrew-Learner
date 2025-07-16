TYPES_DICT: str = {
    "verb": "глагол",
    "noun": "существительное",
    "adj": "прилагательное",
    "adv": "наречие",
    "pronoun": "местоимение",
    "union": "союз",
    "pretext": "предлог",
    "interjection": "междометие",
}


def normalize_text(text: str) -> str:
    characters = ["-", "{", "}", ".", "(", ")", "~", ">", "<"]
    for character in characters:
        text = text.replace(character, "\\" + character)
    return text


def create_words_form_message(data: dict) -> str:
    try:
        d: dict = data["forms"]["Действительный залог"]
    except KeyError:
        d: dict = data["forms"]["active"]
    present: str = "\n".join(d["present"])
    past: str = "\n".join(d["past"])
    future: str = "\n".join(d["future"])
    transcription: str = data["infinitive"]["transcription"]
    menukad: str = data["infinitive"]["menukad"]
    return f"""
{TYPES_DICT[data["type"]].capitalize()} *{menukad}* {{{transcription}}}
*{data["translation"]}*
*{d["benian"]}*
Корень: *{data["sqrt"]}*

*наст. вр.*
{present}
*прошед. вр.*
{past}
*буд. вр.*
{future}
"""
