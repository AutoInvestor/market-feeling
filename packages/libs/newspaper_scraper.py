import newspaper


class NewspaperScraper:

    def scrape(self, url: str) -> str:
        try:
            article = newspaper.article(url)
            return article.text
        except Exception as e:
            return ""
