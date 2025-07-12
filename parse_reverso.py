from bs4 import BeautifulSoup
import cloudscraper

BASE_LINK = "https://context.reverso.net/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4/%D0%B8%D0%B2%D1%80%D0%B8%D1%82-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9/"
SCRAPER = cloudscraper.create_scraper()


def get_sentences_for_word(word: str) -> list:
    response = SCRAPER.get(BASE_LINK + word)
    soup = BeautifulSoup(response.text, "html.parser")
    sentences = soup.findAll("div", "example")
    output: list[dict] = []

    for sentence in sentences:
        spans = sentence.findAll("span", class_="text")
        output.append({"he": spans[0].text.strip(), "ru": spans[1].text.strip()})
    return output
