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


def verb_create_words_form_message(data: dict) -> dict:
    forms = data.get("forms")
    active = forms.get("active")

    present = "\n".join(active.get("present"))
    past = "\n".join(active.get("past"))
    future = "\n".join(active.get("future"))

    transcription = data.get("infinitive").get("transcription")
    menukad = data.get("infinitive").get("menukad")
    verb_type = TYPES_DICT.get(data.get("type")).capitalize()

    text = f"""{verb_type} *{menukad}* {{{transcription}}}
*{data.get("translation")}*
*{active.get("benian")}*
Корень: *{data.get("sqrt")}*

*наст. вр.*
{present}
*прошед. вр.*
{past}
*буд. вр.*
{future}
"""

    return {
        "passive_voice": bool(forms.get("passive")),
        "imperative_mode": bool(active.get("imperative")),
        "text": text.strip(),
    }


def noun_create_words_form_message(data: dict) -> dict:
    forms = "\n".join(data.get("forms"))
    sqrt = f'Корень: *{data.get("sqrt")}*' if data.get("sqrt") else ""
    verb_type = TYPES_DICT.get(data.get("type")).capitalize()

    text = f"""{verb_type} *{data.get("base_form")}*
*{data.get("translation")}*
{sqrt}

{forms}
"""
    return {"text": text.strip()}


def basic_create_words_from_message(data: dict) -> dict:
    verb_type = TYPES_DICT.get(data.get("type")).capitalize()
    sqrt = f'Корень: *{data.get("sqrt")}*' if data.get("sqrt") else ""
    transcription = data.get("transcription")
    show_transcription = f"{{{transcription}}}" if transcription else ""
    text = f"""{verb_type} *{data.get("base_form")}* {show_transcription}

*{data.get("translation")}*

{sqrt}
"""
    return {"text": text.strip()}


def pretext_create_words_form_message(data: dict) -> dict:
    forms = "\n".join(data.get("forms"))
    verb_type = TYPES_DICT.get(data.get("type")).capitalize()
    text = f"""{verb_type} *{data.get("base_form")}* {{{data.get("transcription")}}}
*{data.get("translation")}*

{forms}
"""
    return {"text": text.strip()}
