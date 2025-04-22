import logging
import newspaper

logger = logging.getLogger(__name__)


class NewspaperScraper:

    def scrape(self, url: str) -> str:
        try:
            article = newspaper.article(url)
            return article.text
        except Exception as e:
            return ""
