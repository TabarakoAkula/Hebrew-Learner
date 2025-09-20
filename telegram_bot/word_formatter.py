import re


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

PEALIM_LINK = "https://www.pealim.com"


def normalize_text(text: str) -> str:
    characters = ["-", "{", "}", ".", "(", ")", "~", ">", "<", "|", "!", "?"]
    for character in characters:
        text = text.replace(character, "\\" + character)
    return text


def get_clear_text(text: str) -> str:
    return re.sub(r"[\u0591-\u05C7]", "", text).strip()


def verb_create_words_form_message(data: dict, imperative: bool, passive: bool) -> dict:
    forms = data.get("forms")
    active = forms.get("active")

    present = "\n".join(active.get("present"))
    past = "\n".join(active.get("past"))
    future = "\n".join(active.get("future"))
    active_text = "\n_Действительный залог_" if passive else ""
    transcription = data.get("infinitive").get("transcription")
    menukad = data.get("infinitive").get("menukad")
    verb_type = TYPES_DICT.get(data.get("type")).capitalize()

    text = f"""{verb_type} *{menukad}* {{{transcription}}}
*{data.get("translation")}*
*{active.get("benian")}*
Корень: *{data.get("sqrt")}*
{active_text}
*наст. вр.*
{present}
*прошед. вр.*
{past}
*буд. вр.*
{future}
"""
    if imperative and not text.count("пов. накл.:"):
        imperative_text = "*пов. накл.:*\n" + "\n".join(active.get("imperative"))
        text += imperative_text

    if passive and not text.count("Страдательный залог"):
        passive = forms.get("passive")
        present = "\n".join(passive.get("present"))
        past = "\n".join(passive.get("past"))
        future = "\n".join(passive.get("future"))
        passive_text = f"""
_Страдательный залог_
*наст. вр.*
{present}
*прошед. вр.*
{past}
*буд. вр.*
{future}
"""
        text += passive_text

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


def get_many_results_message(data: list[dict]) -> dict:
    text = "*Найдено несколько результатов:*\n\n"
    words_data = []
    for word in data:
        words_data.append(
            {
                "word": word.get("word"),
                "base_form": word.get("label"),
                "translation": word.get("translation"),
                "link": PEALIM_LINK + word.get("link"),
                "label": word.get("type").capitalize() + " | " + word.get("label"),
                "id": word.get("link").strip("/").split("/")[-1].replace("-", "_"),
            }
        )
        type_text = word.get("type").capitalize()
        label_text = word.get("label")
        text += f"{type_text} *{label_text}* - _{word.get('translation')}_\n\n"
    return {"text": text.strip(), "data": words_data}
