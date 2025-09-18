import re

from bs4 import BeautifulSoup
import requests


SEARCH_LINK = "https://www.pealim.com/ru/search/?q="
BASE_LINK = "https://www.pealim.com"

VERB_SETTINGS = {
    "present": [
        ("ז.", "AP-ms"),
        ("נ.", "AP-fs"),
        ('ז"ר', "AP-mp"),
        ('נ"ר', "AP-fp"),
    ],
    "past": [
        ("אני", "PERF-1s"),
        ("אתה", "PERF-2ms"),
        ("את", "PERF-2fs"),
        ("הוא", "PERF-3ms"),
        ("היא", "PERF-3fs"),
        ("אנחנו", "PERF-1p"),
        ("אתם", "PERF-2mp"),
        ("אתן", "PERF-2fp"),
        ("הם/הן", "PERF-3p"),
    ],
    "future": [
        ("אני", "IMPF-1s"),
        ("אתה", "IMPF-2ms"),
        ("את", "IMPF-2fs"),
        ("הוא", "IMPF-3ms"),
        ("היא", "IMPF-3fs"),
        ("אנחנו", "IMPF-1p"),
        ("אתם", "IMPF-2mp"),
        ("אתן", "IMPF-2fp"),
        ("הם/הן", "IMPF-3mp"),
    ],
    "imperative": [
        ("ז.", "IMP-2ms"),
        ("נ.", "IMP-2fs"),
        ('ז"ר', "IMP-2mp"),
        ('נ"ר', "IMP-2fp"),
    ],
}

VOICES = {
    "Действительный залог": "active",
    "Страдательный залог": "passive",
}


def get_clear_text(text: str) -> str:
    return re.sub(r"[\u0591-\u05C7]", "", text).strip()


def get_word_page(search_word: str) -> list | None:
    response = requests.get(SEARCH_LINK + search_word)
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.findAll("div", "verb-search-result")
    if not results:
        return None
    output = []
    found = False
    for result in results:
        word = result.find("div", "verb-search-lemma")
        word_data = {
            "label": word.text,
            "word": get_clear_text(word.text),
            "translation": result.find("div", "verb-search-meaning").text,
            "type": result.find("div", "verb-search-binyan")
            .contents[1]
            .replace("–", "")
            .strip(),
            "link": word.find("a")["href"],
        }
        if get_clear_text(word.text) == search_word:
            found = True
        output.append(word_data)
    if found:
        return [i for i in output if get_clear_text(i["label"]) == search_word]
    return output


def get_verb_text(soup: str) -> dict:
    output = {
        "present": [],
        "past": [],
        "future": [],
        "imperative": [],
    }
    for time in output:
        for label, eid in VERB_SETTINGS[time]:
            el = soup.find(id=eid)
            if not el:
                el = soup.find(id=f"passive-{eid}")
            if not el:
                continue
            menukad = el.find("span", class_="menukad").text.strip()
            try:
                chaser = el.find("span", class_="chaser").text.strip()
            except AttributeError:
                chaser = ""
            transcription = el.find("div", class_="transcription").text.strip()
            output[time].append(f"{label.ljust(9)}*{menukad} {chaser}* {{{transcription}}}")
    return output


def get_noun_text(soup: str) -> dict:
    result = []
    rows = soup.select("table.conjugation-table tbody tr")
    for row in rows:
        state_name = row.find("th").get_text(strip=True).lower()
        result.append("*" + state_name.capitalize() + "*")

        cells = row.find_all("td")
        labels = ["יחיד", "רבים"]

        for i, cell in enumerate(cells):
            menukad = cell.find("span", class_="menukad").text.strip().replace("־", "")
            try:
                chaser = cell.find("span", class_="chaser").text.strip()
            except AttributeError:
                chaser = ""
            transcription = (
                cell.find("div", class_="transcription")
                .get_text(strip=True)
                .replace("-", "")
            )
            result.append(f"{labels[i].ljust(9)}*{menukad} {chaser}* {{{transcription}}}")
    return result


def get_adj_text(soup: str) -> list:
    labels = [".ז", ".נ", 'ז"ר', 'נ"ר']
    cells = soup.select("td.conj-td")
    results = []

    for label, cell in zip(labels, cells):
        menukad = cell.find("span", class_="menukad").text.strip()
        try:
            chaser = cell.find("span", class_="chaser").text.strip()
        except AttributeError:
            chaser = ""
        transcription = cell.find("div", class_="transcription").get_text(
            strip=True,
        )
        results.append(f"{label.ljust(9)}*{menukad} {chaser}* {{{transcription}}}")
    return results


def get_pretext_text(soup: str) -> list:
    rows = soup.select("table.conjugation-table tbody tr")
    labels = [
        ["ז.", "נ."],
        ["ז.", "נ.", 'ז"ר', 'נ"ר'],
    ]
    result = []
    for row_idx, row in enumerate(rows):
        person = row.find("th").text.strip()
        result.append(f"*{person} лицо*")

        cells = row.find_all("td")
        cell_labels = labels[0] if row_idx == 0 else labels[1]

        for label, cell in zip(cell_labels, cells):
            forms = cell.find_all("div", recursive=False)
            for form in forms:
                menukad = form.find("span", class_="menukad").text.strip()
                try:
                    chaser = form.find("span", class_="chaser").text.strip()
                except AttributeError:
                    chaser = ""
                transcription = form.find("div", class_="transcription").get_text(
                    strip=True
                )
                result.append(f"{label.ljust(9)}*{menukad} {chaser}* {{{transcription}}}")
    return result


def get_word(link: str) -> dict:
    output = {
        "forms": {},
        "sqrt": "",
        "link": link.split("/")[-2],
    }
    response = requests.get(BASE_LINK + link)
    soup = BeautifulSoup(response.text, "html.parser")
    page_type = soup.findAll("div", class_="container")[1].find("p").text
    tables = soup.findAll("table", "table table-condensed conjugation-table")
    lead = None

    if page_type.lower().count("глагол"):
        infinitive = soup.find("div", id="INF-L")
        output["infinitive"] = {
            "menukad": infinitive.find("span", class_="menukad").text.strip(),
            "transcription": infinitive.find(
                "div", class_="transcription"
            ).text.strip(),
        }
        output["type"] = "verb"
        if len(tables) == 1:
            output["forms"]["active"] = get_verb_text(tables[0])
            output["forms"]["active"]["benian"] = (
                "Биньян " + page_type.split("–")[-1].strip().lower()
            )
            output["forms"]["passive"] = {}
        else:
            headers = soup.find("div", class_="horiz-scroll-wrapper").findAll(
                "h3", class_="page-header"
            )
            if len(tables) != len(headers):
                return "ERROR"
            for index in range(len(headers)):
                heading = headers[index].contents[0].strip()
                output["forms"][VOICES[heading]] = get_verb_text(tables[index])
                output["forms"][VOICES[heading]]["benian"] = (
                    headers[index].contents[1].text.strip()
                )
    elif page_type.lower().count("существительное"):
        output["type"] = "noun"
        output["forms"] = get_noun_text(tables[0])
    elif page_type.lower().count("прилагательное"):
        output["type"] = "adj"
        output["forms"] = get_adj_text(tables[0])
    elif page_type.lower().count("наречие"):
        output["type"] = "adv"
        lead = soup.findAll("div", class_="lead")[1]
    elif page_type.lower().count("местоимение"):
        output["type"] = "pronoun"
        try:
            lead = soup.findAll("div", class_="lead")[1]
        except IndexError:
            lead = None
    elif page_type.lower().count("союз"):
        output["type"] = "union"
        lead = soup.findAll("div", class_="lead")[1]
    elif page_type.lower().count("предлог"):
        output["type"] = "pretext"
        output["forms"] = get_pretext_text(tables[0])
        lead = soup.find("div", id="b")
    elif page_type.lower().count("междометие"):
        output["type"] = "interjection"
        lead = soup.findAll("div", class_="lead")[1]
    else:
        output["type"] = "error"

    if output["type"] not in ["pronoun", "pretext", "union", "interjection"]:
        try:
            output["sqrt"] = soup.find("span", class_="menukad").find("a").text.strip()
        except AttributeError:
            output["sqrt"] = ""

    if (
        output["type"] in ["adv", "union", "pretext", "pronoun", "interjection"]
        and lead
    ):
        output["transcription"] = (
            lead.find("div", "transcription").text.replace("-", "").strip()
        )
        output["base_form"] = lead.find("span", "menukad").text.replace("־", "").strip()
    elif output["type"] in ["pronoun", "noun", "adj", "verb"] and not lead:
        output["base_form"] = (
            soup.find("h2", "page-header").contents[0].text.split()[-1].strip()
        )

    output["translation"] = soup.find("div", class_="lead").text.strip().capitalize()
    return output
