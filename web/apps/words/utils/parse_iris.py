from urllib.parse import quote

from bs4 import BeautifulSoup
import requests

url = "https://www.slovar.co.il/txajax.php"


def get_translation(word: str) -> list:
    output = []
    response = requests.post(
        url,
        data={
            "xajax": "XTranslate",
            "xajaxargs[]": f"<xjxquery><q>word={quote(word)}"
            f"&word_enc=&lang=1&nikud=1&transcription=1</q></xjxquery>",
        },
    )
    xml_soup = BeautifulSoup(response.text, "xml")
    html_soup = BeautifulSoup(xml_soup.findAll("cmd")[-1].text, "html.parser")
    divs = html_soup.findAll(
        "div",
        class_=lambda x: x and ("cycle1" in x or "cycle-1" in x),
    )
    for pare in divs:
        translation = pare.find("span", "translation")
        if not translation:
            continue
        label = pare.find("span", "word").text
        translit = pare.find("span", "translit").text
        translation = translation.text.capitalize()
        output.append(
            {"word": label, "transcription": translit, "translation": translation}
        )
    return output
