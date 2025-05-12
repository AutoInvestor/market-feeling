from typing import Optional

from pymongo import MongoClient

from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository
from stock_api.logger import get_logger

logger = get_logger(__name__)


class MongoCompanyRepository(CompanyRepository):
    def __init__(self, uri: Optional[str], db_name: str):
        self._enabled = bool(uri)
        if not self._enabled:
            logger.warning(
                "No MONGODB_URI provided: MongoCompanyRepository disabled, using dummy behavior."
            )
            return

        client = MongoClient(uri)
        self._coll = client[db_name]["companies"]

    def exists(self, id: str) -> bool:
        if not self._enabled:
            return False

        return self._coll.find_one({"_id": id}) is not None

    def get_all(self) -> dict[str, Company]:
        if not self._enabled:
            return {}

        cursor = self._coll.find({}, {"_id": 1, "ticker": 1, "name": 1})
        companies: dict[str, Company] = {}
        for doc in cursor:
            companies[doc["ticker"]] = Company(
                id=doc["_id"], ticker=doc["ticker"], name=doc["name"]
            )
        return companies

    def find_by_ticker(self, ticker: str) -> Optional[Company]:
        if not self._enabled:
            return None

        doc = self._coll.find_one(
            {"ticker": ticker}, {"_id": 1, "ticker": 1, "name": 1}
        )
        if not doc:
            return None

        return Company(id=doc["_id"], ticker=doc["ticker"], name=doc["name"])

    def save(self, company: Company):
        if not self._enabled:
            return

        doc = {"_id": company.id, "ticker": company.ticker, "name": company.name}

        self._coll.replace_one({"_id": company.id}, doc, upsert=True)
